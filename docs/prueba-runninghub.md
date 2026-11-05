# Ejecutar una prueba 4K desde el VPS

El script `tools/test_runninghub.py` necesita Python 3.10+ de la biblioteca
estándar. No instala paquetes ni modifica Nginx, Docker o los proyectos actuales.
No procesa píxeles con IA localmente: envía el trabajo a RunningHub y descarga
por bloques el resultado. Para subir el archivo admite hasta 10 MiB y utiliza
una carga multipart en memoria acotada; no es un servidor de producción.

Las rutas de envío y consulta se verificaron en el código público de los ejemplos
de RunningHub: host de la página, prefijo `/openapi/v2`,
`/run/workflow/{id}`, `/query` y `/media/upload/binary`.
Se usa el `fileName` devuelto por la subida como entrada de LoadImage.
La aceptación de overrides y la compatibilidad de esta cuenta siguen pendientes
de una ejecución autenticada. No confundir estas comprobaciones documentales
con una prueba real del proveedor.

## Preparación

Descargar el script y copiarlo al VPS, por ejemplo:

```bash
scp test_runninghub.py root@TU_IP:/root/test_runninghub.py
scp afiche.png root@TU_IP:/root/afiche.png
```

Usar una imagen autorizada con letras pequeñas, un rostro y detalles. No pasar
la API key como argumento ni enviarla por chat. El programa la solicita mediante
entrada oculta, o utiliza RUNNINGHUB_API_KEY si ya está configurada en la sesión.
No guarda la clave en sus reportes.

## Simulación local, sin llamar a la API

```bash
python3 /root/test_runninghub.py --image /root/afiche.png --quality 4k --out /root/prueba-upscaler-4k
```

## Ejecución real

Este comando envía UN trabajo facturable a la cuenta de RunningHub. El precio
depende del consumo y las condiciones del proveedor; el script no impone un
límite monetario. Empezar con 4K, no con tres ejecuciones simultáneas.

```bash
python3 /root/test_runninghub.py --image /root/afiche.png --quality 4k --out /root/prueba-upscaler-4k --run
```

Elegir una carpeta nueva. La cuenta necesita acceso al workflow y a la API.
El script muestra un Task ID y consulta cada 5 segundos, hasta 30 minutos de
espera local. Interrumpir la consola no cancela ni devuelve el costo de la tarea.

Si ya existe una tarea, reanudar sin subir ni enviar otra imagen:

```bash
python3 /root/test_runninghub.py --resume ID_DE_TAREA --out /root/prueba-upscaler-4k
```

Si el envío se interrumpe antes de confirmar Task ID, consultar el historial
de RunningHub antes de volver a ejecutar. No se reintenta automáticamente un
envío ambiguo. Los archivos `*.private.json` sirven para seguimiento local y
pueden incluir URLs firmadas; no publicarlos ni adjuntarlos por defecto.

## Resultado que compartir

- `report.json`: estado, tamaño real, consumo informado y tiempo observado.
- `result-*.png` o formato equivalente: imagen final del nodo 168.
- Original autorizado para comparar calidad, si todavía no se compartió.

El informe no incluye la clave ni las URLs de descarga. `usage` conserva los
campos del proveedor sin asumir moneda ni convertir RH coins a dólares.
El tiempo observado incluye esperas; no es exclusivamente tiempo de GPU.

Revisar manualmente: letras, números, identidad facial, piel, halos y uniones
de mosaicos. Un estado SUCCESS no demuestra fidelidad de imagen. Un resultado
con lado mayor diferente de 4096 queda marcado en el informe y debe investigarse.

## Validación local del código

Se prueban estructura de presets, consulta sin reenvío, rechazo de taskId ajeno,
estado de fallo, lectura de cabeceras de imagen sin decodificar píxeles,
ausencia de reintentos al enviar y bloqueo de redirecciones con credenciales.
Estas pruebas usan respuestas simuladas; no consumen saldo ni validan calidad IA.
