#!/usr/bin/env python3
"""Start the private local pilot; credentials are prompted without echo."""
import argparse
import getpass
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8020)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("El puerto debe estar entre 1024 y 65535.")
    import uvicorn
    from web.app import create_app, Provider

    key = os.environ.get('RUNNINGHUB_API_KEY', '').strip()
    access = os.environ.get('UPSCALER_ACCESS_TOKEN', '').strip()
    if not key:
        key = getpass.getpass('Clave API de RunningHub (oculta): ').strip()
    if not access:
        access = getpass.getpass('Crea una clave privada para entrar al estudio (mínimo 16 caracteres): ').strip()
        repeated = getpass.getpass('Repite la clave del estudio: ').strip()
        if access != repeated:
            raise SystemExit('Las claves del estudio no coinciden.')
    if not key or len(access) < 16:
        raise SystemExit('Falta la API key o la clave del estudio tiene menos de 16 caracteres.')
    if key == access:
        raise SystemExit('Usa una clave del estudio distinta de la API key.')
    data = os.environ.get('UPSCALER_DATA_DIR', str(ROOT / 'run-output' / 'web'))
    app = create_app(data_dir=data, access_token=access, provider=Provider(key))
    print(f'Estudio privado: http://127.0.0.1:{args.port}')
    print('Abre la web e introduce la clave del estudio. Ampliar imagen consume saldo de RunningHub.')
    uvicorn.run(app, host='127.0.0.1', port=args.port, workers=1)


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        raise SystemExit('Arranque cancelado.')
