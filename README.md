# SEGUTOOLS Upscaler

Preparación de un ampliador de imágenes para `upscaler.segutools.store`, con
procesamiento externo mediante Replicate Crystal Upscaler y RunningHub.

**Para continuar en otro chat, leer primero [docs/CONTINUIDAD.md](docs/CONTINUIDAD.md).**
Incluye el contexto, la infraestructura, los hallazgos, las autorizaciones y el
bloqueo de acceso remoto. La prioridad vigente es revisar el VPS en modo lectura.

## Estado

Este repositorio contiene análisis, workflows candidatos y un ejecutor de
pruebas. Todavía no contiene una aplicación web terminada ni desplegada.
No se han realizado ejecuciones autenticadas de IA ni se ha accedido al VPS por SSH.
Los presets 4K/6K/8K requieren pruebas de dimensiones, calidad y costo en RunningHub.

## Archivos principales

| Ruta | Contenido |
|---|---|
| [docs/CONTINUIDAD.md](docs/CONTINUIDAD.md) | Memoria completa para retomar el trabajo |
| [docs/integracion-upscaler.md](docs/integracion-upscaler.md) | Arquitectura propuesta y proveedores |
| [docs/auditoria-workflow-runninghub.md](docs/auditoria-workflow-runninghub.md) | Conexiones y parámetros reales del workflow |
| [docs/prueba-runninghub.md](docs/prueba-runninghub.md) | Guía para la prueba remota y su reanudación |
| [workflows/runninghub](workflows/runninghub) | JSON saneado, presets y plantillas de solicitudes |
| [tools/test_runninghub.py](tools/test_runninghub.py) | Ejecutar una prueba o consultar una tarea existente |
| [tools/prepare_runninghub_presets.py](tools/prepare_runninghub_presets.py) | Regenerar variantes desde un export original |

## Validación local

Python 3.10 o superior, sin dependencias adicionales:

```bash
python3 -m unittest discover -s tests -v
```

Estas pruebas usan respuestas simuladas y no consumen saldo. No demuestran
aceptación del proveedor ni calidad de imagen.

## Prueba con RunningHub

Leer primero la guía. Sin `--run`, este comando solo muestra el payload:

```bash
python3 tools/test_runninghub.py --image /ruta/afiche.png --quality 4k --out /ruta/prueba-4k
```

Añadir `--run` envía una ejecución facturable. La clave se solicita con entrada
oculta o mediante `RUNNINGHUB_API_KEY`. No guardar claves, respuestas privadas,
URLs firmadas ni imágenes de clientes en Git. Para una tarea ya enviada usar
`--resume`; no reenviar ante un timeout ambiguo.

## Continuación desde otra máquina

```bash
git clone https://github.com/segu95/escaler.git
cd escaler
```

Cada tarea cloud ya tiene un entorno aislado. Si existe un checkout, utilizarlo;
no crear otro worktree sin necesidad o sin petición del usuario. Verificar las
instrucciones y permisos vigentes antes de operar sobre infraestructura remota.
