"""Private pilot: one active job, external AI, persistent submission journal."""
import asyncio
import hmac
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import time
import uuid
from urllib.parse import urlsplit

import httpx
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from tools.test_runninghub import dimensions, payload, BASE, WORKFLOW

STATIC = Path(__file__).parent / 'static'
LIMIT = 10 * 1024 * 1024
ACTIVE = ('uploading', 'submitting', 'tracking', 'uncertain')

class Provider:
    def __init__(self, key):
        self.key = key

    async def call(self, path, **kwargs):
        async with httpx.AsyncClient(timeout=60, follow_redirects=False) as client:
            async with client.stream('POST', BASE + path,
                    headers={'Authorization': 'Bearer ' + self.key}, **kwargs) as response:
                response.raise_for_status()
                raw = bytearray()
                async for chunk in response.aiter_bytes():
                    raw.extend(chunk)
                    if len(raw) > 2 * 1024 * 1024:
                        raise ValueError('Response too large')
                result = json.loads(raw)
                if not isinstance(result, dict):
                    raise ValueError('Invalid response')
                return result

    async def upload(self, path, mime):
        with open(path, 'rb') as source:
            data = await self.call('/media/upload/binary', files={'file': (Path(path).name, source, mime)})
        if data.get('code') != 0 or not (data.get('data') or {}).get('fileName'):
            raise ValueError('Upload failed')
        return data['data']['fileName']

    async def submit(self, reference, quality):
        return await self.call('/run/workflow/' + WORKFLOW, json=payload(reference, quality))

    async def query(self, task):
        return await self.call('/query', json={'taskId': task})


def create_app(data_dir=None, access_token=None, provider=None):
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    folder = Path(data_dir or os.environ.get('UPSCALER_DATA_DIR', 'run-output/web'))
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    token = access_token if access_token is not None else os.environ.get('UPSCALER_ACCESS_TOKEN', '')
    key = os.environ.get('RUNNINGHUB_API_KEY', '')
    backend = provider or (Provider(key) if key else None)
    dbfile = folder / 'tasks.sqlite3'
    def db():
        connection = sqlite3.connect(dbfile)
        connection.row_factory = sqlite3.Row
        return connection
    with db() as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, quality TEXT, state TEXT, task TEXT, result TEXT, created REAL, checked REAL DEFAULT 0)')
        conn.execute("UPDATE jobs SET state='uncertain' WHERE state='submitting'")
        conn.execute("UPDATE jobs SET state='failed' WHERE state='uploading'")
    os.chmod(dbfile, 0o600)
    for leftover in folder.glob('input-*'):
        leftover.unlink(missing_ok=True)
    lock = asyncio.Lock()
    receiving = asyncio.Lock()

    def get(job_id):
        with db() as conn:
            row = conn.execute('SELECT * FROM jobs WHERE id=?', (job_id,)).fetchone()
        if not row:
            raise HTTPException(404, 'Tarea no encontrada.')
        return dict(row)

    def update(job_id, **values):
        with db() as conn:
            conn.execute('UPDATE jobs SET ' + ','.join(k+'=?' for k in values) + ' WHERE id=?', (*values.values(), job_id))

    def public(row):
        return {k: row[k] for k in ('id', 'quality', 'state', 'task', 'result', 'created')}

    def authenticate(request):
        supplied = request.headers.get('authorization', '').removeprefix('Bearer ')
        if not token or not hmac.compare_digest(supplied.encode(), token.encode()):
            raise HTTPException(401, 'Introduce una clave de acceso válida.')

    @app.middleware('http')
    async def headers(request, next_handler):
        response = await next_handler(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' blob: https:; style-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
        return response

    @app.get('/api/config')
    async def config():
        return {'ready': bool(token and backend), 'max_bytes': LIMIT}

    async def work(job_id, path, mime, quality):
        try:
            reference = await backend.upload(path, mime)
            update(job_id, state='submitting')  # durable before billable request
            response = await backend.submit(reference, quality)
            task = response.get('taskId')
            if not isinstance(task, (str, int)) or not str(task):
                raise ValueError('No task id')
            update(job_id, state='tracking', task=str(task))
        except Exception:
            state = get(job_id)['state']
            update(job_id, state='uncertain' if state == 'submitting' else 'failed')
        finally:
            Path(path).unlink(missing_ok=True)

    @app.post('/api/jobs')
    async def submit(request: Request, background: BackgroundTasks):
        authenticate(request)
        if not backend:
            raise HTTPException(503, 'El procesamiento todavía no está configurado.')
        job_id = request.headers.get('idempotency-key', '')
        try:
            if str(uuid.UUID(job_id)) != job_id:
                raise ValueError()
        except ValueError:
            raise HTTPException(400, 'Identificador de solicitud inválido.')
        quality = request.query_params.get('quality', '4k')
        if quality not in ('4k', '6k', '8k'):
            raise HTTPException(400, 'Resolución inválida.')
        mime = request.headers.get('content-type', '').split(';')[0]
        suffix = {'image/png': '.png', 'image/jpeg': '.jpg', 'image/webp': '.webp'}.get(mime)
        if not suffix:
            raise HTTPException(415, 'Usa una imagen PNG, JPG o WebP.')
        if receiving.locked():
            raise HTTPException(429, 'Hay una carga en curso. Espera un momento.')
        async with receiving:
            with db() as conn:
                previous = conn.execute('SELECT * FROM jobs WHERE id=?', (job_id,)).fetchone()
                if previous:
                    if previous['quality'] != quality:
                        raise HTTPException(409, 'Este identificador ya pertenece a otra solicitud.')
                    return public(dict(previous))
                if conn.execute("SELECT 1 FROM jobs WHERE state IN ('uploading','submitting','tracking','uncertain') LIMIT 1").fetchone():
                    raise HTTPException(409, 'Hay una tarea pendiente. Revisa su estado antes de iniciar otra.')
            fd, path = tempfile.mkstemp(prefix='input-', suffix=suffix, dir=folder)
            try:
                total = 0
                with os.fdopen(fd, 'wb') as output:
                    async for chunk in request.stream():
                        total += len(chunk)
                        if total > LIMIT:
                            raise HTTPException(413, 'La imagen supera 10 MiB.')
                        output.write(chunk)
                with open(path, 'rb') as source:
                    signature = source.read(12)
                valid = (mime == 'image/png' and signature.startswith(b'\x89PNG\r\n\x1a\n') or
                         mime == 'image/jpeg' and signature.startswith(b'\xff\xd8') or
                         mime == 'image/webp' and signature[:4] == b'RIFF' and signature[8:12] == b'WEBP')
                size = dimensions(path)
                if not valid or not size or min(size) < 1 or max(size) > 32768 or size[0]*size[1] > 40_000_000:
                    raise HTTPException(400, 'Imagen no compatible o demasiado grande (máximo 40 megapíxeles).')
                with db() as conn:
                    conn.execute('INSERT INTO jobs(id,quality,state,created) VALUES(?,?,?,?)', (job_id, quality, 'uploading', time.time()))
                background.add_task(work, job_id, path, mime, quality)
                return public(get(job_id))
            except BaseException:
                Path(path).unlink(missing_ok=True)
                raise

    @app.get('/api/jobs')
    async def recent(request: Request):
        authenticate(request)
        with db() as conn:
            return [public(dict(row)) for row in conn.execute('SELECT * FROM jobs ORDER BY created DESC LIMIT 10')]

    @app.get('/api/jobs/{job_id}')
    async def status(job_id: str, request: Request):
        authenticate(request)
        async with lock:
            row = get(job_id)
            if backend and row['state'] == 'tracking' and time.time()-row['checked'] >= 5:
                update(job_id, checked=time.time())
                try:
                    result = await backend.query(row['task'])
                    if str(result.get('taskId', '')) != row['task']:
                        raise ValueError('Wrong task')
                    state = result.get('status')
                    if state == 'SUCCESS':
                        url = next((r.get('url') for r in result.get('results', []) if str(r.get('nodeId')) == '168'), None)
                        parsed = urlsplit(url or '')
                        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
                            raise ValueError('Missing result')
                        update(job_id, state='succeeded', result=url)
                    elif state in ('FAILED', 'CANCELLED', 'CANCELED', 'STOPPED'):
                        update(job_id, state='failed')
                    elif state not in ('QUEUED', 'RUNNING', 'PENDING', 'WAITING', 'SUBMITTING'):
                        raise ValueError('Unknown status')
                except Exception:
                    raise HTTPException(502, 'No se pudo confirmar el estado. La tarea se conserva; vuelve a consultar.') from None
            return public(get(job_id))

    @app.get('/')
    async def index():
        return FileResponse(STATIC / 'index.html')
    app.mount('/static', StaticFiles(directory=STATIC), name='static')
    return app
