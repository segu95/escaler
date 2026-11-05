#!/usr/bin/env python3
"""Run one billed RunningHub test, or resume an existing task. Python 3.10+."""
import argparse
import getpass
import json
import os
from pathlib import Path
import struct
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

BASE = "https://www.runninghub.ai/openapi/v2"
WORKFLOW = "1995790546771783682"


def dimensions(path):
    """Read image headers without decoding pixels. Return None if unsupported."""
    with open(path, "rb") as f:
        header = f.read(32)
        if header[:8] == b"\x89PNG\r\n\x1a\n" and len(header) >= 24:
            return struct.unpack(">II", header[16:24])
        if header[:2] == b"\xff\xd8":
            f.seek(2)
            while True:
                marker = f.read(1)
                if not marker:
                    return None
                if marker != b"\xff":
                    continue
                code = f.read(1)
                while code == b"\xff":
                    code = f.read(1)
                if not code or code in (b"\xd9", b"\xda"):
                    return None
                if code == b"\x01" or 0xd0 <= code[0] <= 0xd7:
                    continue
                raw = f.read(2)
                if len(raw) != 2:
                    return None
                size = int.from_bytes(raw, "big")
                if size < 2:
                    return None
                if code[0] in (0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf):
                    raw = f.read(5)
                    if len(raw) == 5:
                        height, width = struct.unpack(">HH", raw[1:])
                        return width, height
                    return None
                f.seek(size - 2, 1)
        if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
            if header[12:16] == b"VP8X":
                return (1 + int.from_bytes(header[24:27], "little"),
                        1 + int.from_bytes(header[27:30], "little"))
            if header[12:16] == b"VP8 " and header[23:26] == b"\x9d\x01\x2a":
                width, height = struct.unpack("<HH", header[26:30])
                return width & 0x3fff, height & 0x3fff
            if header[12:16] == b"VP8L" and header[20] == 0x2f:
                bits = int.from_bytes(header[21:25], "little")
                return (bits & 0x3fff) + 1, ((bits >> 14) & 0x3fff) + 1
    return None


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError("Redirección de API rechazada; comprueba el host de tu cuenta.")


class API:
    def __init__(self, key):
        self.key = key
        self.opener = urllib.request.build_opener(NoRedirect())

    def post(self, path, value=None, data=None, content_type="application/json"):
        if data is None:
            data = json.dumps(value).encode()
        request = urllib.request.Request(BASE + path, data=data, method="POST", headers={
            "Authorization": "Bearer " + self.key, "Content-Type": content_type,
        })
        try:
            with self.opener.open(request, timeout=60) as response:
                raw = response.read(2 * 1024 * 1024 + 1)
            if len(raw) > 2 * 1024 * 1024:
                raise RuntimeError("Respuesta API demasiado grande.")
            result = json.loads(raw)
        except urllib.error.HTTPError as error:
            raise RuntimeError(f"API HTTP {error.code}; sin reintento automático.") from None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            raise RuntimeError("Sin respuesta API confirmada; no se reenvía la solicitud.") from None
        if not isinstance(result, dict):
            raise RuntimeError("Respuesta API inesperada.")
        return result

    def upload(self, path):
        boundary = "segutools-" + uuid.uuid4().hex
        suffix = path.suffix.lower()
        content_type = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                        ".png": "image/png", ".webp": "image/webp"}[suffix]
        prefix = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; '
                  f'filename="input{suffix}"\r\nContent-Type: {content_type}\r\n\r\n').encode()
        data = prefix + path.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
        response = self.post("/media/upload/binary", data=data,
                             content_type="multipart/form-data; boundary=" + boundary)
        value = response.get("data") or {}
        if response.get("code") != 0 or not value.get("fileName"):
            raise RuntimeError("La subida no devolvió fileName; no se inició ninguna mejora.")
        return value["fileName"]


def payload(reference, quality):
    return {"addMetadata": False, "nodeInfoList": [
        {"nodeId": "123", "fieldName": "image", "fieldValue": reference},
        {"nodeId": "142", "fieldName": "scale_by", "fieldValue": quality[0]},
        {"nodeId": "172", "fieldName": "condition", "fieldValue": "always"},
    ]}


def save(path, value):
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    os.chmod(temp, 0o600)
    temp.replace(path)


def wait_for_result(api, task_id, out, timeout=1800, pause=time.sleep, clock=time.monotonic):
    started = clock()
    previous = None
    while clock() - started < timeout:
        response = api.post("/query", {"taskId": task_id})
        if str(response.get("taskId", "")) != str(task_id):
            raise RuntimeError("La consulta devolvió otro taskId o ninguno. Reanuda tras revisar la cuenta.")
        save(out / "provider-response.private.json", response)
        status = response.get("status")
        if status != previous:
            print("Estado:", status, flush=True)
            previous = status
        if status in ("SUCCESS", "FAILED", "CANCELLED", "CANCELED", "STOPPED"):
            return response
        if status not in ("QUEUED", "RUNNING", "PENDING", "WAITING", "SUBMITTING"):
            raise RuntimeError("Estado no reconocido. No se enviará otro trabajo.")
        pause(5)
    raise RuntimeError("Se agotó la espera local; la tarea puede continuar en RunningHub. Usa --resume.")


def download_results(response, out):
    images = []
    # Download only final SaveImage output, not temporary comparators.
    for index, result in enumerate(response.get("results") or []):
        if str(result.get("nodeId")) != "168":
            continue
        url = result.get("url", "")
        if urllib.parse.urlsplit(url).scheme != "https":
            raise RuntimeError("El resultado no tiene URL HTTPS.")
        suffix = str(result.get("outputType", "")).lower().lstrip(".")
        if suffix not in ("png", "jpg", "jpeg", "webp"):
            continue
        target = out / f"result-{index}.{suffix}"
        temporary = target.with_suffix(target.suffix + ".part")
        count = 0
        # Separate request: never send the API credential to storage hosts.
        with urllib.request.urlopen(url, timeout=60) as source, temporary.open("wb") as dest:
            while chunk := source.read(65536):
                count += len(chunk)
                if count > 512 * 1024 * 1024:
                    raise RuntimeError("Resultado excede 512 MiB; detenida la descarga.")
                dest.write(chunk)
        temporary.replace(target)
        size = dimensions(target)
        if size is None:
            raise RuntimeError("No se reconocen las dimensiones del resultado descargado.")
        images.append({"file": target.name, "bytes": count, "width": size[0], "height": size[1]})
    if not images:
        raise RuntimeError("No se encontró una imagen del nodo final 168; revisa la respuesta privada.")
    return images


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", type=Path)
    parser.add_argument("--quality", choices=("4k", "6k", "8k"), default="4k")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--resume", help="Consultar tarea existente; nunca enviar otra")
    parser.add_argument("--run", action="store_true", help="Enviar un trabajo facturable")
    args = parser.parse_args()
    if args.resume and args.run:
        parser.error("Usa --resume o --run, no ambos.")
    if not args.resume:
        if not args.image or not args.image.is_file():
            parser.error("Indica --image con un archivo existente.")
        if args.image.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            parser.error("Solo PNG, JPG o WebP.")
        if not 0 < args.image.stat().st_size <= 10 * 1024 * 1024:
            parser.error("Límite de entrada: 10 MiB.")
        if dimensions(args.image) is None:
            parser.error("No se reconocen las dimensiones de la entrada.")
        if not args.run:
            print(json.dumps(payload("<imagen-subida>", args.quality), indent=2))
            print("Simulación local. Añade --run para enviar UNA ejecución facturable.")
            return
        if args.out.exists():
            parser.error("La carpeta de salida ya existe. Usa --resume para una tarea anterior.")
    os.umask(0o077)
    args.out.mkdir(parents=True, exist_ok=bool(args.resume))
    key = os.environ.get("RUNNINGHUB_API_KEY") or getpass.getpass("Clave RunningHub (oculta): ")
    if not key.strip():
        parser.error("Falta la clave API.")
    api = API(key.strip())
    start = time.time()
    journal = args.out / "task.private.json"
    metadata = json.loads(journal.read_text()) if args.resume and journal.exists() else {}
    if args.resume:
        if metadata.get("taskId") and metadata["taskId"] != args.resume:
            parser.error("La carpeta pertenece a otra tarea.")
        task_id = args.resume
    else:
        reference = api.upload(args.image)
        body = payload(reference, args.quality)
        metadata = {"workflow": WORKFLOW, "quality": args.quality,
                    "input_dimensions": dimensions(args.image), "started_at": start,
                    "phase": "submission_unconfirmed"}
        save(journal, metadata)
        # Exactly one submit attempt. An ambiguous timeout MUST NOT trigger a retry.
        response = api.post("/run/workflow/" + WORKFLOW, body)
        save(args.out / "submission.private.json", response)
        task_id = response.get("taskId")
        if not task_id:
            raise RuntimeError("No se confirmó taskId; revisa el historial de RunningHub antes de reenviar.")
    metadata.update({"taskId": task_id, "phase": "tracking"})
    save(journal, metadata)
    print("Task ID:", task_id, flush=True)
    print("Para reanudar usa --resume con este ID y la misma carpeta.", flush=True)
    response = wait_for_result(api, task_id, args.out)
    report = {"status": response.get("status"), "workflow": WORKFLOW,
              "quality": metadata.get("quality", "unknown"), "usage": response.get("usage"),
              "elapsed_since_submission_seconds": round(time.time() - metadata["started_at"], 1)
              if "started_at" in metadata else None, "images": []}
    save(args.out / "report.json", report)
    if report["status"] != "SUCCESS":
        raise RuntimeError("La tarea no terminó correctamente. Consulta report.json; no se reintenta.")
    report["images"] = download_results(response, args.out)
    expected = {"4k": 4096, "6k": 6144, "8k": 8192}.get(report["quality"])
    for result in report["images"]:
        result["matches_longest_side"] = max(result["width"], result["height"]) == expected if expected else None
    save(args.out / "report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, ValueError, KeyboardInterrupt) as error:
        # Avoid printing provider URLs, keys or raw server error bodies.
        message = str(error) if isinstance(error, RuntimeError) else type(error).__name__
        print("Prueba detenida:", message)
        raise SystemExit(1)
