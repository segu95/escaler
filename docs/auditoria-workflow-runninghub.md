# Auditoría del workflow exportado de RunningHub

Fuente: JSON en formato API facilitado por el usuario para el workflow
1995790546771783682. Este análisis de conexiones sustituye las inferencias
anteriores basadas solo en el catálogo. No se ejecutó el workflow en GPU.

## Hallazgo principal: una rama costosa solo calcula dimensiones

La ruta que determina dimensiones es:

`123 original → 161 Nomos 4× → 172 encajar en 1024×1024 → 170 very sharp
→ 142 Lanczos 8× → 155 leer dimensiones`.

Pero el nodo 154 toma los PÍXELES del original 123 y solo el ANCHO/ALTO del 155.
Por tanto, ni los píxeles generados por Nomos ni el enfoque very sharp se usan
como imagen de entrada a SeedVR2. Esa rama sí es dependencia del resultado y
puede consumir GPU, tiempo y memoria para obtener unas dimensiones.

La ruta de imagen que se guarda es:

`123 original → 154 redimensionar → 36 dividir en mosaicos
→ 143 reducir cada mosaico a 0,25× → 128 SeedVR2
→ 144 ajustar al tamaño del mosaico → 125 ensamblar → 168 guardar`.

111 calcula el tamaño de los mosaicos; 138 mide los mosaicos de 36.
159 es un comparador con URLs temporales firmadas antiguas, innecesario en la API.
173 lee dimensiones pero no alimenta ningún resultado guardado.
Los artefactos preparados excluyen 159 y 173 y sustituyen la imagen de ejemplo.
El archivo original del usuario se conserva sin modificar.

## Parámetros originales exactos

| Nodo | Campo | Valor |
|---|---|---|
| 123 | image | Archivo que se debe sustituir en cada solicitud |
| 162 | model_name | 4xNomos8kHAT-L_otf.pth |
| 172 | width, height | 1024, 1024 |
| 172 | method, condition | keep proportion, downscale if bigger |
| 170 | enhance | very sharp; solo afecta a la rama de dimensiones |
| 142 | scale_by | 8; interpolación Lanczos |
| 154 | multiple_of | 8; ancho/alto desde 155, imagen desde 123 |
| 111 | width_factor, height_factor | 2, 2 |
| 111 | overlap_rate | 0,10 aproximadamente |
| 143 | scale_by | 0,25; interpolación Lanczos |
| 128 | resolution, max_resolution | 1536, 0 |
| 128 | seed | 923278288 |
| 128 | batch_size, uniform_batch_size | 1, false |
| 128 | color_correction | wavelet |
| 128 | input_noise_scale, latent_noise_scale | 0, 0 |
| 128 | temporal_overlap, prepend_frames | 0, 0 |
| 129 | model | seedvr2_ema_3b_fp16.safetensors |
| 129 | device, blocks_to_swap | cuda:0, 16 |
| 129 | attention_mode, offload_device | sdpa, cpu |
| 130 | model | ema_vae_fp16.safetensors |
| 130 | encode_tiled, decode_tiled | false, false |
| 130 | encode/decode_tile_size | 1024; inactivos al deshabilitar VAE tiling |
| 130 | encode/decode_tile_overlap | 64; inactivos al deshabilitar VAE tiling |
| 130 | device, offload_device | cuda:0, none |
| 144 | method, multiple_of | stretch, 8; dimensiones desde 138 |
| 125 | padding | 64 |
| 168 | images | Salida de 125 |

`cpu` y `cuda:0` se refieren a la máquina que ejecuta el workflow, es decir,
RunningHub en la arquitectura propuesta; no al VPS de SEGUTOOLS.
Los mosaicos TTP están activos aunque el tiling interno del VAE esté desactivado.

El título del nodo 128 dice v2.5.24, mientras sus metadatos registran versión
2.5.10 del paquete. Esto no cambia el archivo de pesos SeedVR2 3B declarado.
Se debe verificar la versión instalada antes de atribuir semánticas nuevas al nodo.

`resolution: 1536` es un parámetro de la etapa SeedVR2, no la resolución final
del archivo. La salida se vuelve a ajustar en 144 y se recompone en 125.
No hay prompt ni un control genérico `creativity` en este export.

## Tamaños y presets propuestos

El original reduce la salida de Nomos a una caja de 1024×1024 y luego multiplica
sus dimensiones por 8. Con una salida Nomos 4× normal y originales cuyo lado
mayor alcanza 256 px, esa base suele alcanzar 1024 px. Para imágenes menores,
`downscale if bigger` no garantiza esa base y el resultado puede quedar por
debajo de 8192. No basta con el nombre del workflow para garantizar 8K.

Los presets de revisión conservan la cadena de procesamiento y cambian:

| Preset | 172.condition | 142.scale_by | Lado mayor objetivo |
|---|---|---|---|
| 4K | always | 4 | 4096 |
| 6K | always | 6 | 6144 |
| 8K | always | 8 | 8192 |

Mantienen 172.width/height=1024, method=keep proportion y todos los valores
SeedVR2/TTP originales. El prefijo de guardado identifica cada variante.
La condición always también amplía originales pequeños a la base de 1024;
no implica que se recuperen detalles inexistentes.

Los nodos con multiple_of=8 pueden redondear o recortar ligeramente dimensiones.
El código público actual de ImageResize+ aplica ajuste a múltiplos y un recorte
final cuando corresponde. La versión instalada de RunningHub y el ensamblador
TTP deben comprobarse. No prometer dimensiones exactas, ausencia de costuras ni
proporción matemáticamente idéntica antes de ejecutar las variantes.

Los archivos *_request-template.json son cuerpos candidatos con nodeInfoList.
El campo fieldValue usa cadenas para los overrides; validar la coerción y los
campos admitidos contra la API real. El endpoint de workflow y el endpoint de
aplicación no son intercambiables: la aplicación publicada solo expone image.
Si el endpoint no admite estos overrides, importar una variante como workflow
propio y usar su nuevo ID. No se ha publicado ni modificado ningún workflow remoto.

## Optimización propuesta, todavía no aplicada

Sustituir la rama 161/162/172/170/142/155 por un cálculo directo de dimensiones
a partir del original, conservando la política de proporciones, redondeos y tamaño
intermedio que se valide. Así se evitarían Nomos y filtros cuyos píxeles se
descartan. Se conservaría la rama SeedVR2/TTP que realmente produce el resultado.

No reconectar automáticamente la salida Nomos a SeedVR2: sería un cambio de
procesamiento y de calidad, no una mera optimización equivalente. Tampoco activar
VAE tiling, cambiar padding o aumentar ruido sin una prueba comparativa.
Los presets entregados mantienen la rama original para establecer una referencia.

## Validación realizada y pendiente

Realizada: lectura JSON, inventario de nodos, referencias válidas, ausencia de
ciclos, dependencias de SaveImage, eliminación de comparadores con URLs firmadas,
generación de tres variantes y cuerpos de solicitud sin credenciales.

Pendiente: aceptación por RunningHub, carga del archivo, dimensiones finales,
integridad del ensamblado TTP, memoria de GPU, tiempo, costo, conservación de
texto/rostros y comparación con Crystal creatividad 0. No se ejecutaron imágenes.

Las pruebas deben incluir entrada horizontal, vertical, cuadrada, pequeña y un
afiche con letras finas. Inspeccionar uniones de mosaicos al 100 %, no solo el
tamaño nominal. Registrar versión de workflow y costo por preset.

## Artefactos

- `workflows/runninghub/original-sanitized_api.json`: referencia sin comparador.
- `workflows/runninghub/4k_api.json`, `6k_api.json`, `8k_api.json`: candidatos.
- `workflows/runninghub/*_request-template.json`: overrides de entrada y tamaño.
- `workflows/runninghub/provenance.json`: hash de origen y alcance de verificación.
- `tools/prepare_runninghub_presets.py`: generación reproducible, sin llamadas API.

Referencia de implementación del nodo de tamaño (rama principal, no una
certificación de la versión instalada):
https://github.com/cubiq/ComfyUI_essentials/blob/main/image.py
