# SEGUTOOLS Upscaler

Preparación de un ampliador de imágenes para `upscaler.segutools.store`, con
procesamiento externo mediante Replicate Crystal Upscaler y RunningHub.

**Para continuar en otro chat, leer primero [docs/CONTINUIDAD.md](docs/CONTINUIDAD.md).**
Incluye el estado vigente, la infraestructura y los pendientes. La revisión del
VPS ya se completó. La prioridad es configurar la nueva clave de RunningHub en
un formulario seguro y validar una prueba 4K; el primer envío fue rechazado
por saldo insuficiente. No hay despliegue autorizado.

## Estado

Este repositorio contiene una primera aplicación web para pruebas privadas,
análisis, workflows candidatos y un ejecutor de pruebas. La interfaz permite
cargar imágenes y elegir 4K/6K/8K; el backend integra el envío y seguimiento con
RunningHub. Todavía no está desplegada ni validada con una ejecución real de IA.

Para iniciar la vista previa y configurar el piloto, leer
[Aplicación web](docs/aplicacion-web.md).

Se completó una [revisión del VPS por SSH, solo de lectura](docs/revision-vps-2026-11-05.md).
No se instaló ni desplegó el upscaler. Los presets requieren pruebas de dimensiones,
calidad y costo con la cuenta del proveedor.

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

Python 3.10 o superior; instalar primero `requirements.txt` para las pruebas web:

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
