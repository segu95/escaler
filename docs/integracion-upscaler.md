# SEGUTOOLS Upscaler: especificación de integración

Destino: `https://upscaler.segutools.store`.
Revisión de fuentes públicas: 4 de noviembre de 2026.

Estado: análisis y diseño, sin despliegue ni ejecuciones autenticadas de IA.
Esta especificación no es una configuración de producción ni demuestra calidad,
costo o dimensiones de salida mediante pruebas.

Actualización: se recibió y analizó el JSON exportado del workflow. La auditoría
en `auditoria-workflow-runninghub.md` sustituye las limitaciones de inspección
del grafo descritas más abajo. Ya existen presets candidatos; siguen pendientes
las pruebas autenticadas. Nomos y el filtro de enfoque solo alimentan una rama
de dimensiones, no los píxeles de salida de SeedVR2.

## Infraestructura disponible

Según el diagnóstico facilitado por el propietario: Ubuntu 24.04, una CPU,
913 MiB de RAM, unos 199 MiB disponibles, sin swap y 2,5 GB de disco libre.
Nginx sirve 80/443; la aplicación existente usa 127.0.0.1:8000 y otro servicio
usa 127.0.0.1:8011. PostgreSQL y Redis ya están en uso por el proyecto existente.
El DNS del subdominio resolvía a 82.39.109.28. No se ha validado TLS ni el
virtual host de este subdominio. No se dispone de acceso directo al VPS.

Propuesta: interfaz estática compilada fuera del VPS, Nginx existente, backend
ligero de un proceso y SQLite para tareas y usuarios. Elegir un puerto local
libre después de comprobarlo. No añadir PostgreSQL/Redis nuevos por defecto.
La capacidad real requiere medir memoria y concurrencia junto al proyecto actual.

Las imágenes irán a almacenamiento externo, por ejemplo R2. El backend
transferirá archivos por streaming con límites de tamaño; evitará cargar imágenes
8K completas, Base64 grandes y redimensionados de alta resolución en memoria.
Una imagen RGBA de 8192 × 8192 ocupa 256 MiB solo en el búfer de píxeles.

## Proveedor 1: Crystal en Replicate

Modelo: `philz1337x/crystal-upscaler`.

Esquema público consultado:

| Campo | Tipo / valores | Predeterminado |
|---|---|---|
| image | URI de imagen, obligatorio | — |
| scale_factor | número | 2 |
| creativity | número, 0 a 10 | 0 |
| output_format | png o jpg | png |

JPG se describe con calidad 95 %. El esquema consultado no expone prompt,
pasos, CFG ni restauración facial. La ausencia de un máximo de scale_factor
en el esquema no garantiza que cualquier tamaño sea aceptado en ejecución.

Preset inicial: creatividad 0, PNG para diseño gráfico. Calcular el factor como
`lado_objetivo / max(ancho, alto)` para ampliaciones. Si la entrada ya alcanza
o supera el objetivo, tratarla como un caso separado: no enviar factores menores
que uno sin confirmar su soporte. Probar factores fraccionarios y verificar las
dimensiones devueltas. No prometer fidelidad absoluta a texto o identidad.

Objetivos de la interfaz: 4K = 4096, 6K = 6144, 8K = 8192 en el lado mayor.
Ejemplo para entrada 2048 × 1536: factores 2, 3 y 4 respectivamente.

Los metadatos públicos consultados indican `supports_cancelation: false`.
Permitir cancelar trabajos locales no enviados; una ejecución aceptada por el
proveedor no debe presentarse como detenida ni reembolsada automáticamente.

El precio depende de píxeles de salida. Ejemplos publicados al revisar:
4096 × 3072: US$0,20; 6144 × 4608: US$0,80;
8192 × 6144: US$0,80; 8192 × 8192: US$1,60.
Revalidar las tarifas antes de vender créditos. No equivalen al costo total del servicio.

## Proveedor 2: workflow de RunningHub

- Workflow: `1995790546771783682`.
- Aplicación vinculada: `1995795227128500225`.
- Título: `upscale 8K Fast-seedvr2.5+ttp`.
- Ruta publicada: `/run/workflow/1995790546771783682`.
- Modelos declarados: `seedvr2_ema_3b_fp16.safetensors`,
  `ema_vae_fp16.safetensors`, `4xNomos8kHAT-L_otf.pth`.
- Nodos declarados: SeedVR2, escalado con modelo, mosaicos TTP, recomposición,
  redimensionado y `LayerFilter: Sharp & Soft`.

El título no acredita una versión SeedVR2.5 distinta del archivo declarado.
La lista de componentes no establece su orden ni parámetros internos.

La aplicación pública expone un único parámetro:

```json
{
  "nodeInfoList": [
    {
      "nodeId": "123",
      "fieldName": "image",
      "fieldValue": "<referencia de imagen obtenida al subir el archivo>"
    }
  ]
}
```

Es un ejemplo de mapeo, no una petición lista para ejecutar. Verificar el host,
prefijo API, autenticación y formato de referencia de archivo con el ejemplo
generado en la cuenta. La documentación describe una subida multipart que
devuelve `download_url` y `fileName`; no asumir que son intercambiables para el nodo.

El editor usa una consulta de lectura POST `/api/workflow/getContent` con
`workflowId`. Sin sesión respondió `403 TOKEN_MISSION`. No se obtuvo el grafo.
No se han descubierto los IDs ni campos de resolución, mosaicos o nitidez.
Por tanto no añadir controles ficticios de creatividad o resolución al payload.

Para modificar tamaños se necesita exportar el workflow normal y, preferiblemente,
también el workflow en formato API. Después: localizar los nodos de tamaño,
confirmar si 8K se refiere al lado mayor, distinguir escala intermedia/final,
revisar límites de mosaicos y exportar presets verificables para 4096/6144/8192.

La documentación general admite:

- `nodeInfoList`: mapeo de nodos obligatorio.
- `addMetadata`: opcional; propuesta inicial false.
- `instanceType`: default (24 GB VRAM), plus (48 GB), ultra (84 GB).
  No elegir una instancia por defecto sin revisar las necesidades del workflow.
- `usePersonalQueue`: depende del acceso contratado.
- `retainSeconds`: opción de Enterprise Shared con cobro adicional; omitir inicialmente.
- `webhookUrl`: callback cuando termina el trabajo.

La documentación indica enlaces de resultados con validez de 24 horas y datos
de uso en `usage`. El tiempo de unos dos minutos es una afirmación del autor,
no una medición propia. El costo queda pendiente de la cuenta y ejecución real.

## Funciones de producto

Mantener el objetivo de seis acabados de Designmarket, pero no presentar como
distintos motores lo que solo son etiquetas del mismo procesamiento:

| Acabado deseado | Candidato | Estado |
|---|---|---|
| HD / fidelidad | Crystal, creatividad 0 | Pendiente de pruebas |
| Natural / detalle | Workflow de RunningHub | Pendiente de pruebas y tamaño real |
| Retratos | Comparar Crystal y RunningHub | Pendiente de preservar identidad en muestras |
| Creativo | Workflow adicional | Por seleccionar |
| Retoque de estudio | Edición localizada de piel e iluminación | Por seleccionar |

Entrada JPG/PNG/WebP, máximo 10 MiB. Validar tipo real, dimensiones, orientación
EXIF y cuota; probar transparencia en PNG, sin prometer su conservación todavía.
Antes/después, zoom y descarga del resultado. Los controles sin proveedor validado
quedan fuera del lanzamiento inicial; las seis opciones siguen como alcance pendiente.

Login propio inicialmente. Integrar cuentas de segutools.store exige revisar su
autenticación. Créditos y paquetes serán configurables, sin copiar precios de
Designmarket automáticamente. No reutilizar su sesión, API, marca o claves.

## Trabajos y almacenamiento

1. Autenticar, validar imagen y cuota, y crear un identificador idempotente.
2. Guardar la imagen en almacenamiento externo con acceso temporal.
3. Reservar crédito y registrar tarea local antes de enviar al proveedor.
4. Guardar el ID externo. Si un envío queda ambiguo por timeout, reconciliar antes
   de reintentar: un reenvío ciego podría cobrar dos veces.
5. Consultar estado o recibir webhook; nunca esperar minutos en una petición web.
6. Verificar estado consultando al proveedor antes de aceptar callbacks no firmados.
   No descargar URLs arbitrarias provenientes de un callback sin validación.
7. Copiar resultado válido a almacenamiento propio antes de caducar el enlace.
8. Registrar resolución, consumo, costo y saldo de forma transaccional.
9. Limpiar originales y resultados según la política elegida.

Para anunciar 48 horas de descarga, conservar copia propia 48 horas desde la
finalización; el enlace de 24 horas de RunningHub no basta. Definir política
separada para originales y backups.

API keys solo en backend. Acceso a resultados restringido al propietario de la
tarea; enlaces firmados de corta duración. Configuración DNS/TLS y Nginx del
subdominio se preparará al revisar el virtual host actual, sin sustituir el del sitio principal.

## Prueba comparativa pendiente

Usar imágenes autorizadas: afiche con texto pequeño y logotipos, composición con
varios rostros y retrato con textura de piel. Comparar Crystal creatividad 0 y
RunningHub con valores originales. Añadir una muestra PNG transparente si se
ofrecerá transparencia. Empezar con pocas ejecuciones y registrar:

- dimensiones reales y conservación de proporción;
- fidelidad de letras, números, logotipos y rostros;
- nitidez, halos, piel y detalles inventados al 100 %;
- tiempo completo, tiempo de proceso y costo real;
- formato, tamaño y disponibilidad de descarga;
- recuperación de errores, doble envío y contabilización de créditos.

Requisitos pendientes: exportación JSON de RunningHub, acceso seguro de las APIs,
imágenes de prueba y almacenamiento. No se han ejecutado ni cobrado tareas desde aquí.

## Fuentes

- https://designmarketperu.com/pages/designmarketupscaler
- https://upscaler.designmarketperu.com/integration/upscaler.js?v=v41-todos-4k-6k-8k
- https://replicate.com/philz1337x/crystal-upscaler
- https://replicate.com/philz1337x/crystal-upscaler/api/schema
- https://www.runninghub.ai/call-api/api-detail/1995790546771783682?apiType=5
- https://www.runninghub.ai/ai-detail/1995795227128500225
