# Aplicación web: piloto privado

Primera versión local, sin despliegue. Interfaz HTML/CSS/JavaScript sin compilación,
backend FastAPI de un proceso, SQLite independiente. Procesamiento de IA en
RunningHub usando los presets candidatos 4K/6K/8K existentes. No hay modelos
locales ni decodificación de píxeles en el backend.

## Iniciar la vista previa

Desde la raíz del repositorio, Python 3.10+:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m uvicorn web.app:create_app --factory --host 127.0.0.1 --port 8020 --workers 1
```

Abrir http://127.0.0.1:8020. Sin credenciales se puede seleccionar y previsualizar
una imagen, pero el botón de procesamiento permanece deshabilitado.
No usar múltiples workers ni compartir esta base entre procesos: el límite de
concurrencia corresponde a un proceso. No iniciar otra instancia sobre los mismos
datos mientras una está trabajando.

## Arranque privado con entrada oculta

Para una prueba local, sin guardar credenciales en archivos ni en el historial:

```bash
python3 tools/start_web.py --port 8021
```

Ejecutarlo en la terminal del entorno de desarrollo, no en el VPS. Pide la API key
sin mostrarla y una clave distinta para acceder al estudio (mínimo 16 caracteres).
El puerto 8021 permite mantener la vista previa sin credenciales en 8020. Si se
usa un entorno virtual, ejecutar `.venv/bin/python` en lugar de `python3`.
Las claves quedan en memoria del proceso y desaparecen al terminarlo. No pegar
la API key en el chat. El arranque no envía tareas: la ejecución comienza cuando
se pulsa «Ampliar imagen» en la web. Para la primera prueba usar 4K y una imagen
propia; verificar el historial del proveedor si hay un resultado incierto.

## Habilitar procesamiento real

Configurar de forma segura en el entorno del backend:

- `RUNNINGHUB_API_KEY`: secreto del proveedor, nunca llega al navegador.
- `UPSCALER_ACCESS_TOKEN`: clave aleatoria larga para este estudio privado.
- `UPSCALER_DATA_DIR`: directorio propio y escribible para SQLite y temporales.

`.env.example` documenta las variables; el servidor no lee archivos .env por sí
solo. El usuario introduce únicamente la clave del estudio en la interfaz. Se
conserva en sessionStorage durante la sesión de pestaña. No reutilizar la API key
como clave del estudio. Servir mediante HTTPS si se habilita acceso remoto.

Al pulsar «Ampliar imagen» con las credenciales configuradas se envía una tarea
facturable. Los presets y el contrato del proveedor todavía requieren una prueba
real con la cuenta. No se ha ejecutado esa prueba ni se garantiza la dimensión
exacta o calidad final. El piloto es de un solo propietario: no hay cuentas,
créditos, cobros a clientes ni aislamiento entre varios usuarios de la misma clave.

## Flujo y recursos

- JPG/PNG/WebP hasta 10 MiB y 40 megapíxeles; se comprueban firma y dimensiones
  de cabecera, no se hace una decodificación completa de validación.
- Carga del navegador al backend por bloques, temporal acotado y subida multipart
  al proveedor desde archivo. El original se elimina al terminar o fallar el envío.
- Una sola tarea activa; journal SQLite previo al envío facturable.
- Idempotencia por UUID: repetir el mismo identificador no vuelve a enviar.
- Timeout durante envío: estado `uncertain`, que bloquea nuevas tareas. Revisar
  el historial del proveedor antes de reconciliarlo; no borrar el journal para
  forzar otro envío. La reconciliación administrativa se realiza con la herramienta local descrita abajo.
- Un reinicio conserva tareas con ID externo y marca envíos interrumpidos como
  inciertos. «Consultar mis tareas» recupera el trabajo más reciente o pendiente.
- Consulta cada 5 segundos desde la pestaña activa. Sin pestaña abierta no hay
  sondeo automático; se reanuda al consultar. Fallos de consulta no generan tareas.
- Resultado HTTPS del nodo final 168; lo recibe directamente el navegador.
  El servidor no descarga, almacena ni redimensiona la imagen final.
- Comparación mediante botones Original/Resultado. Tras recargar, el original
  local ya no está disponible. El enlace permite abrir y guardar el resultado;
  no se promete descarga forzada entre dominios ni retención de 48 horas.

La API externa reduce el trabajo local, pero atender HTTP, subir archivos,
consultar tareas y almacenar metadatos sí usa CPU, RAM, red y algo de disco.
Quedan pendientes límites de tráfico en el proxy, política de retención de
metadatos, evaluación de carga y medición de memoria en el destino antes de
producción. El piloto no modifica ni comparte el proyecto existente del VPS.

## Comprobaciones

```bash
python3 -m unittest discover -s tests -v
node --check web/static/app.js
```

18 pruebas locales: 7 existentes, 7 del backend web y 4 de recuperación. Cubren autorización,
idempotencia, envío ambiguo, tamaño/formato, seguimiento y borrado de temporales.
Se comprobó la interfaz en Chromium a 1440 y 390 px, carga y vista previa,
sin desbordamiento horizontal ni errores JavaScript. Las respuestas de proveedor
son simuladas; estas comprobaciones no consumen saldo.

## Recuperar un envío incierto sin repetir el cobro

En RunningHub comprobar manualmente que la tarea corresponde a la misma imagen,
hora y workflow. Copiar su ID y el identificador local mostrado por la web:

```bash
python3 tools/reconcile_web_task.py --job ID_LOCAL --task ID_RUNNINGHUB --confirm-match
```

La herramienta consulta únicamente la tarea externa, verifica el ID y un estado
conocido, y vincula el ID al registro incierto. Rechaza IDs ya asociados y tareas
locales confirmadas. No llama a subida ni a ejecución. Después usar «Consultar
estado» en la web. Para otro directorio de datos indicar `--database RUTA_SQLITE`.
La correspondencia de imagen/hora/workflow requiere revisión del propietario;
la respuesta de consulta por sí sola no prueba que sea la misma imagen.
Si el historial no muestra una tarea inequívoca, mantener el estado incierto y
consultar al proveedor antes de volver a enviar.
