#!/usr/bin/env python3
"""Attach a verified provider task to an uncertain local job. Never submits work."""
import argparse
import asyncio
import getpass
import os
from pathlib import Path
import re
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from web.app import Provider


async def reconcile(database, job_id, task_id, provider):
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,128}', task_id):
        raise ValueError('ID externo inválido.')
    # mode=rw: fail rather than silently creating a different database.
    connection = sqlite3.connect(Path(database).resolve().as_uri() + '?mode=rw', uri=True)
    try:
        row = connection.execute('SELECT state,task FROM jobs WHERE id=?', (job_id,)).fetchone()
        if row is None or row[0] != 'uncertain' or row[1]:
            raise ValueError('La tarea local debe estar sin confirmar y sin ID externo.')
        result = await provider.query(task_id)
        if str(result.get('taskId', '')) != task_id or result.get('status') not in (
                'QUEUED', 'RUNNING', 'PENDING', 'WAITING', 'SUBMITTING',
                'SUCCESS', 'FAILED', 'CANCELLED', 'CANCELED', 'STOPPED'):
            raise ValueError('El proveedor no confirmó el ID y estado de esa tarea.')
        with connection:
            if connection.execute('SELECT 1 FROM jobs WHERE task=? AND id<>?', (task_id, job_id)).fetchone():
                raise ValueError('Ese ID externo ya está asociado a otra tarea.')
            changed = connection.execute(
                "UPDATE jobs SET task=?,state='tracking',checked=0 WHERE id=? AND state='uncertain' AND task IS NULL",
                (task_id, job_id)).rowcount
            if changed != 1:
                raise ValueError('La tarea cambió durante la consulta. No se modificó.')
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, default=ROOT / 'run-output/web/tasks.sqlite3')
    parser.add_argument('--job', required=True, help='ID local de la tarea incierta')
    parser.add_argument('--task', required=True, help='ID correspondiente en el historial de RunningHub')
    parser.add_argument('--confirm-match', action='store_true', help='Confirma haber comprobado imagen, hora y workflow en el historial')
    args = parser.parse_args()
    if not args.confirm_match:
        parser.error('Verifica imagen, hora y workflow en RunningHub; luego añade --confirm-match.')
    key = os.environ.get('RUNNINGHUB_API_KEY') or getpass.getpass('Clave API de RunningHub (oculta): ')
    if not key.strip():
        parser.error('Falta la clave API.')
    asyncio.run(reconcile(args.database, args.job, args.task, Provider(key.strip())))
    print('Tarea vinculada. Consulta su estado desde la web. No se envió una nueva ejecución.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, sqlite3.Error, OSError, KeyboardInterrupt, EOFError):
        raise SystemExit('No se pudo reconciliar la tarea. Revisa los identificadores y la base local; no se reenvió.')
    except Exception:
        raise SystemExit('El proveedor no confirmó la consulta. Conserva la tarea y vuelve a consultar; no se reenvió.')
