# Memoria de continuidad: SEGUTOOLS Upscaler

Estado al 5 de noviembre de 2026. Idioma del usuario: español. Zona: America/Lima.
Este documento resume trabajo realizado, evidencia y pendientes; no reemplaza
las instrucciones nuevas del usuario ni las políticas del siguiente entorno.

## Estado vigente para el siguiente chat — entrega a GitHub

El usuario autorizó expresamente subir el código y la memoria a GitHub, rama
`main`, para continuar sin descargar un ZIP. Esa autorización se refiere al
repositorio: no autoriza desplegar ni modificar servicios del VPS.
Leer primero esta sección; los apartados inferiores conservan la historia.

- Existe un piloto web privado en `web/`, con 18 pruebas locales aprobadas.
  No se ha desplegado y no hay un resultado de IA exitoso todavía.
- Workflow elegido por el usuario: `1995790546771783682`. No cambiarlo por
  `2118434176885411841`, la copia que aparecía en una captura.
- Una única solicitud real 4K fue rechazada con `errorCode=605` y taskId vacío.
  La subida sí devolvió fileName. No hubo reintentos ni resultado descargable.
- La cuenta mostraba RHcoins 100 y Wallet Balance 0. La clave `escaler` estaba
  en Enterprise-Shared, cuya pantalla indica facturación en dólares y Recharge
  Wallet. `Limit($)=9999` era un límite de gasto, no saldo.
- El usuario indica que dispone de otra clave Consumer-Membership y quiere
  sustituir la anterior en `RUNNINGHUB_API_KEY`. No ha podido introducirla aún.
  Verificar condiciones, saldo y compatibilidad de esa modalidad; no asumir
  que los 100 RHcoins permiten el workflow ni que basta cambiar la clave.
- El campo secreto está limitado al destino HTTPS `www.runninghub.ai`.
  La clave anterior fue declarada ready por el entorno; no pedirla ni mostrarla.
- El borrador del chat anterior rechaza modificaciones con `draft_not_editable`.
  El usuario no ve «Editar entorno» y tampoco dispone de terminal visible.
  No repetir instrucciones de terminal interactiva ni inventar botones de UI.
  Preparar el requisito del secreto mediante las herramientas de configuración
  en una nueva sesión de configuración editable; su valor se introduce en el
  formulario seguro, nunca como mensaje. No reutilizar IDs del entorno anterior.
- La aplicación requiere además una clave privada propia del estudio si se
  habilita acceso a su API; es distinta de la API key del proveedor.
- No asumir que las credenciales, archivos ignorados o claves SSH sobreviven.
  Este repositorio no contiene secretos, bases de tareas, respuestas privadas
  ni originales/resultados de las pruebas.

Imagen suministrada por el usuario para UNA prueba 4K (ilustración navideña,
478×641 px, no es el diseño Nitro enviado inicialmente):

https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR3MxMFAWZ6f8Mzu3vlEbie1sbGpDGNBYIxoIfSHuYe-g&s=10

Próximo paso: resolver el campo seguro de la nueva API key, verificar la modalidad
Consumer-Membership y el saldo aplicable, y solo entonces continuar la prueba
única acordada, registrando el ID externo antes de consultar. No comprar saldo.
No duplicar envíos ambiguos. La revisión del VPS ya se completó y permanece
limitada a lectura; conservar separados el proyecto existente y el nuevo upscaler.

## Prueba real: envío rechazado por saldo insuficiente

El usuario aportó un enlace de Google a una ilustración «¡Feliz Navidad!» de
478×641 px (distinta de la imagen Nitro inicialmente adjunta). Se descargó en
`run-output/navidad-source.jpg`. La subida a RunningHub devolvió fileName y se
intentó UNA ejecución 4K del workflow original `1995790546771783682`.
RunningHub respondió errorCode 605, saldo insuficiente, con taskId vacío.
No existe resultado ni ID confirmado. No se reintentó. El reporte saneado está
en `run-output/navidad-4k-first/report.json`; la respuesta privada está fuera de
Git. El journal conservador registra submission_unconfirmed; el error explícito
605 explica el rechazo. No presentar el envío como una ampliación completada.
La captura previa mostraba RHcoins 100 y Wallet Balance 0. La respuesta actual
confirma saldo insuficiente para esta solicitud; no se verificó tarifa ni importe
mínimo de recarga. Siguiente paso: el propietario comprueba/recarga el saldo API
y avisa para reintentar una sola vez. No comprar saldo ni reenviar automáticamente.

## Actualización: credencial disponible en el entorno

RUNNINGHUB_API_KEY está presente y el runtime la declara ready con observaciones
actuales, limitada al destino HTTPS www.runninghub.ai. Se comprobó POST /query
con un ID inexistente y válido sintácticamente: respuesta 1004, Task not found.
Esto confirma respuesta del endpoint con la configuración actual; no demuestra
permisos para ejecutar el workflow, saldo suficiente ni calidad. No se crearon
tareas ni se hicieron ampliaciones. Falta una imagen propia aportada por el usuario
para la prueba 4K. No solicitar ni mostrar el valor de la credencial.

## Confirmación del workflow al retomar el entorno

El usuario confirmó continuar con el workflow original `1995790546771783682`,
no con la copia `2118434176885411841` mostrada en su captura. En el nuevo entorno
se conservaron los archivos y pasaron las 18 pruebas locales. La credencial
RUNNINGHUB_API_KEY sigue ausente; no se han ejecutado trabajos reales.

## Actualización: preparada la prueba con credenciales

Se añadieron `tools/start_web.py` (entrada oculta, puerto local configurable) y
`tools/reconcile_web_task.py` (vincular una tarea incierta a un ID externo verificado,
sin reenviar). Hay 18 pruebas locales correctas. RUNNINGHUB_API_KEY sigue ausente:
no se enviaron ejecuciones reales. La clave se introduce en terminal, no por chat.
Consultar la guía web para arrancar en 8021 junto a la vista previa en 8020.

## Actualización: primera web local preparada

A petición del usuario se creó un piloto web ligero: `web/`, `requirements.txt`,
`.env.example` y `tests/test_web.py`. Ver [guía web](aplicacion-web.md).
Incluye carga y vista previa, 4K/6K/8K, autenticación privada, journal SQLite,
envío único a RunningHub, seguimiento y enlace de resultado. 14 pruebas locales
pasaron, más comprobaciones de navegador en escritorio/móvil. No hubo trabajos
facturables, despliegues ni cambios de servicios. La integración real sigue
pendiente de credenciales y de validar los presets. Esta actualización sustituye
el estado histórico de ausencia de aplicación que se conserva más abajo.

## Actualización: acceso SSH y revisión completados

El 5 de noviembre de 2026, aproximadamente a las 14:29 America/Lima, se accedió
por SSH a Serversegu y se completó la revisión de solo lectura. Ver
[revisión del VPS](revision-vps-2026-11-05.md) para evidencia, recursos y propuesta
independiente. Esta actualización sustituye las referencias históricas de abajo
que indicaban que nunca se había entrado o que el transporte seguía bloqueado.

La privada anterior no estaba disponible. Se generó otra fuera del repositorio;
el propietario autorizó su pública y la autenticación funcionó. Se verificó la
huella registrada. No se modificaron servicios ni se desplegó la aplicación.
El puerto 8020 está libre en la medición; no existe un virtual host upscaler.
RAM disponible: 176 MiB; disco libre: 2,3 GB; sin swap. La capacidad de producción
no está demostrada. Los detalles anteriores del VPS se conservan como historia.

## Objetivo y autorización vigente

El usuario quiere reproducir las funciones de Designmarket Upscaler en
https://upscaler.segutools.store usando APIs externas de IA. Su proyecto actual
ya funciona en segutools.store y NO quiere mezclar las aplicaciones.
Prioridad actual: conseguir acceso al VPS y revisar su configuración SOLO EN
LECTURA. No instalar la nueva app, cambiar Nginx, reiniciar servicios, tocar
bases de datos ni modificar su proyecto durante esa revisión.

El usuario autorizó expresamente instalar Tailscale y lo instaló desde su
terminal root siguiendo los comandos proporcionados. Esto no autoriza cambios
adicionales ajenos a la revisión. El asistente nunca ha entrado por SSH al VPS.

El usuario pide ahora trasladar toda la continuidad a otro chat. No volver a
pedir datos ya contenidos aquí salvo que hayan cambiado. Avanzar con acciones
reversibles autorizadas; declarar bloqueos reales sin afirmar acceso inexistente.

## Repositorio y paquete

Repositorio seleccionado: segu95/escaler, rama main. Checkout original en
/workspace/escaler, inicialmente solo README.md, commit corto 2170095.
Los archivos se prepararon durante esta conversación y el usuario solicitó
publicarlos en https://github.com/segu95/escaler para continuar en otro chat.
Consultar el historial Git para el commit de entrega. No hay despliegue en el VPS.
No hay aplicación web terminada: hay análisis, presets y un ejecutor de pruebas.
El nuevo chat no debe asumir acceso al filesystem, herramientas ni claves del anterior.
Adjuntar este ZIP al chat siguiente y extraerlo en un directorio de trabajo.

## VPS: diagnóstico aportado por el usuario

- Host: Serversegu; acceso root del propietario.
- Ubuntu 24.04.4 LTS x86_64, una CPU.
- RAM 913 MiB, aproximadamente 199 MiB disponibles en la medición; sin swap.
- Disco raíz 14 GB, unos 2,5 GB libres, 82 % ocupado.
- Nginx escucha 80/443; SSH habitual escucha 22.
- /opt/segu-downloads/compose.yaml: proyecto Docker existente.
- Contenedores: segu_web (segu-downloads-web) en 127.0.0.1:8000,
  segu_db (postgres:16-alpine), segu_redis (redis:7-alpine).
- Otro servicio: segutube-premium.service, Python, 127.0.0.1:8011.
- Sitios Nginx habilitados: segutools.store, segutube-premium, segutube-web.
- Configuración adicional: /etc/nginx/conf.d/cloudflare-real-ip.conf.
- Python 3.12.3, Docker 29.6.2, Compose v5.3.1, Certbot, UFW.
- UFW permitía OpenSSH, 80/tcp y 443/tcp para IPv4/IPv6.
- Caché de build Docker: 2,76 GB, 2,415 GB recuperables según diagnóstico.
  NO se autorizó ni ejecutó limpieza.
- Dominio administrado en Cloudflare. El subdominio resolvía a 82.39.109.28.
  No tratar esta resolución por sí sola como confirmación de IP SSH del VPS.
- Consultas HTTPS públicas devolvieron 302 a /panel/ tanto en segutools.store
  como en upscaler.segutools.store. Podría estar atendiendo el mismo sitio;
  confirmar en Nginx, no darlo por demostrado.

La IA externa evita ejecutar modelos en el VPS, pero no elimina consumo de CPU,
RAM, transferencias y almacenamiento de la aplicación. No decodificar 8K en este
VPS por defecto: un búfer RGBA cuadrado 8192×8192 consume 256 MiB por sí solo.

## SSH, Tailscale y bloqueo actual

VPS conectado a Tailscale y confirmado por su terminal:

- Nombre serversegu.
- IP privada 100.98.148.18.
- tailscaled: active.

Instalación: repositorio oficial firmado de Tailscale para Ubuntu noble,
apt-get install tailscale, systemctl enable --now tailscaled y
tailscale up --accept-dns=false --accept-routes=false.
No se habilitó Tailscale SSH: se pretende usar el OpenSSH habitual y llave pública.

El usuario ejecutó la adición de esta clave pública al authorized_keys de root:

```
restrict ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJTpzibZXJ5N41ZUGfVjZawSrmrfuZ2fwybHhDLmwM0q codex-upscaler-2026-11-05
```

La clave privada solo estaba en /workspace/.upscaler-access/id_ed25519 del
entorno original. NO está en el ZIP ni debe pedirse por chat. Si el nuevo chat
no dispone de ella, generar otro par en su entorno y autorizar solo su pública.
La opción restrict impide PTY y forwarding, pero permite comandos SSH normales.

Huella ED25519 del servidor proporcionada por el propietario:

```
SHA256:lSPOGe280XZdF0u3tAE40yaGF0U1TsghwghL1T3eykI
```

Verificar esa huella antes de autenticar. No desactivar verificación de host.

El usuario configuró una clave de autenticación Tailscale en el panel del entorno
Codex. La captura mostraba VPN → Tailscale → Configurada; el editor solo pedía
auth key, NO mostraba campos de destinos TCP. No se expuso su clave en el chat.
Se indicó publicar para aplicar a una nueva instancia; no asumir que se adjuntó.

La última captura de la consola de Tailscale mostraba tres máquinas Connected:
- codex-environment: 100.116.214.57.
- codex-environment-1: 100.97.195.33.
- serversegu: 100.98.148.18.

Sin embargo, la instancia adjunta al chat anterior siguió informando:

```
vpn_configured: false
tcp_connect_proxy: http://proxy:8088
tcp_network_access: {domains: [], ip_ranges: []}
```

environment_status indicaba running/connected e Internet unrestricted/enforced,
pero eso NO confirmaba VPN ni TCP. ID anterior:
ccarenv_b64_Y2NhcmVudl81NzdhMWIxNjU0YzQ4MTkxOTY4ZTM0ZDQ3YzdiNjQ2Mw.

Se probó únicamente un CONNECT al proxy:8088 para 100.98.148.18:22:
- Ejecución normal: PermissionError, operación no permitida.
- Escalación admitida: ConnectionRefusedError en el listener proxy:8088.
No se llegó al servidor, no se autenticó ni se ejecutaron órdenes remotas.
No atribuir estos errores al firewall del VPS ni pedir reinstalar Tailscale allí.

Siguiente diagnóstico: comprobar a qué instancia está adjunto el NUEVO chat,
leer su network-policy y estado, y usar la ruta SSH/TCP admitida por ese entorno.
Los nodos Connected en la consola no prueban que el chat use uno de ellos.
No repetir el ciclo de pedir publicar sin verificar un cambio efectivo.
Si el entorno administrado sigue sin ruta, explicar el límite de plataforma.

## Revisión del sitio de referencia

https://designmarketperu.com/pages/designmarketupscaler
Frontend embebido:
https://upscaler.designmarketperu.com/integration/upscaler.js?v=v41-todos-4k-6k-8k

Comprobado en HTML/JS público: Shopify Horizon, componente personalizado
designmarket-upscaler, React con Shadow DOM y backend independiente en el
subdominio upscaler.designmarketperu.com. El panel administrativo identifica
RunningHub como proveedor. No se accedió al backend privado ni a sus claves.

Seis herramientas: hd, creativo, natural, fiel, retrato, retrato_estudio.
Entradas JPEG/PNG/WebP hasta 10 MiB; opciones 4K/6K/8K = 4096/6144/8192 px en
lado mayor. Comparador, zoom 100 %, seguimiento cada 5 segundos, cancelación,
sesiones, créditos, recargas y prioridad. Natural/retrato 6K/8K anuncian dos
etapas por un crédito. HD 6K anuncia proceso 8K y entrega a 6144.
Algunas descargas ajustan dimensiones en Canvas; no confundir eso con IA.
Cinco usos gratuitos por cuenta; precios anunciados S/2 por 1, S/5 por 3,
S/10 por 10. Son precios comerciales del sitio, no costos de proveedor.
Recargas por Yape con comprobante vía WhatsApp. Resultados anunciados 48 horas.

Rutas observadas: /api/enhance POST y GET ?task=, /api/cancel?task= POST,
/api/account, /api/credits, /api/shopify/config, /api/shopify/start,
/api/admin/upscaler, /api/admin/upscaler/settings.
Mejora envía image, tool, resolution, contentType y requestId.

Se pretende reproducir funciones con implementación propia. No se conocen los
workflows ni parámetros privados exactos de Designmarket. No copiar sus claves
ni presentar una calidad idéntica como garantizada. Shopify no es necesario.

## Crystal / Replicate elegido por el usuario

https://replicate.com/philz1337x/crystal-upscaler
https://replicate.com/philz1337x/crystal-upscaler/api/schema

Esquema consultado: image URI obligatoria, scale_factor número predeterminado 2,
creativity número 0..10 predeterminado 0, output_format png/jpg predeterminado png.
JPG 95 % según descripción. No expone prompt/CFG/pasos/restauración facial.
Preset recomendado para fidelidad: creativity=0, PNG. Factor = objetivo/lado mayor
para ampliaciones. Factores fraccionarios, límites y dimensiones deben probarse.
Metadatos de la página: supports_cancelation=false. No prometer devolución de
costo al cancelar una tarea ya enviada.
Tarifas consultadas: 4096×3072 US$0,20; 6144×4608 US$0,80;
8192×6144 US$0,80; 8192×8192 US$1,60. Revalidar antes de vender créditos.
No se han hecho ejecuciones reales ni recibido REPLICATE_API_TOKEN.

## Workflow concreto de RunningHub

https://www.runninghub.ai/call-api/api-detail/1995790546771783682?apiType=5
Aplicación pública: https://www.runninghub.ai/ai-detail/1995795227128500225
Nombre: upscale 8K Fast-seedvr2.5+ttp.

El usuario aportó upscale 8K Fast-seedvr2.5+ttp_api.json. Contiene 20 nodos.
El original incluía referencias firmadas antiguas del comparador: NO incluirlas
en reportes ni usarlas para acceso. El ZIP conserva una versión saneada de 18
nodos, eliminando comparador 159 y nodo sin uso 173. Se reemplazó la imagen ejemplo.

Hallazgo importante confirmado por el grafo:
123 original → 161 Nomos 4× → 172 caja 1024×1024 → 170 very sharp
→ 142 Lanczos 8× → 155 dimensiones.
154 recibe PÍXELES de 123 y solo dimensiones de 155. Así, Nomos y very sharp
consumen trabajo pero sus píxeles no alimentan la imagen final.

Ruta final: 123 → 154 → 36 mosaicos → 143 escala 0,25 → 128 SeedVR2
→ 144 tamaño de mosaico → 125 ensamblar → 168 SaveImage.

Valores originales:
- 128: resolution=1536, max_resolution=0, seed=923278288, batch_size=1,
  uniform_batch_size=false, color_correction=wavelet, input_noise_scale=0,
  latent_noise_scale=0, temporal_overlap=0, prepend_frames=0, offload_device=cpu.
- 129: seedvr2_ema_3b_fp16.safetensors, cuda:0, blocks_to_swap=16,
  swap_io_components=false, attention_mode=sdpa, offload_device=cpu.
- 130: ema_vae_fp16.safetensors, cuda:0, encode_tiled=false, decode_tiled=false,
  tamaños VAE 1024, overlaps 64 (inactivos con tiling desactivado), offload none.
- 111: width_factor=2, height_factor=2, overlap_rate≈0,10.
- 125: padding=64.
- 142: scale_by=8.
- 172: width=height=1024, keep proportion, downscale if bigger.
- 154 y 144: multiple_of=8.
- 162: 4xNomos8kHAT-L_otf.pth.

El título SeedVR2.5 no prueba otra versión de pesos: archivo SeedVR2 3B.
Nodo título v2.5.24 y metadatos paquete 2.5.10. No confundir resolution 1536
de SeedVR2 con resolución del resultado ensamblado.

Presets candidatos preparados: 142.scale_by=4/6/8 y 172.condition=always para
base 1024 aun con originales diminutos. Conservan el resto del procesamiento.
Objetivos 4096/6144/8192; se deben verificar redondeos, proporción y costuras.
No se aplicó todavía la optimización de quitar la rama Nomos de dimensiones.

La aplicación expone solo image: nodeId 123, fieldName image. Overrides de 142
y 172 se preparan para endpoint WORKFLOW; su aceptación real está pendiente.
Si hace falta importar un workflow propio, usar su nuevo ID, no confundirlo con
el ID público ni con el endpoint AI App.

Rutas vistas en JS oficial de RunningHub:
https://www.runninghub.ai/openapi/v2/run/workflow/1995790546771783682
POST /openapi/v2/query con taskId; subida /openapi/v2/media/upload/binary.
Autenticación Bearer desde backend. El script usa fileName devuelto por upload
para LoadImage; compatibilidad pendiente de ejecución con cuenta real.
Enlaces de resultados duran 24 h; copiar a almacenamiento propio para ofrecer 48 h.
API admite webhookUrl, devuelve usage y estados. Costos y VRAM real sin medir.
No se recibió RUNNINGHUB_API_KEY ni se lanzó ninguna tarea facturable.

## Artefactos preparados y pruebas

- docs/integracion-upscaler.md: diseño general, costos, almacenamiento y límites.
- docs/auditoria-workflow-runninghub.md: nodos y presets auditados.
- workflows/runninghub/: original saneado, variantes API 4K/6K/8K,
  request templates, provenance/hash. Son candidatos NO ejecutados.
- tools/prepare_runninghub_presets.py: generación desde export original.
- tools/test_runninghub.py: prueba remota de un solo trabajo, sin dependencias
  externas, Python 3.10+. Pide clave oculta o usa RUNNINGHUB_API_KEY.
- docs/prueba-runninghub.md: instrucciones de ejecución y reanudación.
- tests/test_runninghub_runner.py: siete pruebas locales pasaron; mocks, sin saldo.

El ejecutor valida cabeceras sin decodificar píxeles, sube imagen hasta 10 MiB,
envía una vez, guarda taskId, consulta, permite --resume, descarga salida 168 y
genera report.json con dimensiones y usage. No reenvía tras timeout ambiguo.
Archivos *.private.json pueden contener URLs firmadas; no pedirlos por defecto.
No tratar siete pruebas unitarias como validación real del proveedor.

Comando previsto, aún NO ejecutado en el VPS:

```
python3 /root/test_runninghub.py --image /root/afiche.png --quality 4k --out /root/prueba-upscaler-4k --run
```

--run envía UN trabajo facturable. Primero revisar el VPS en lectura, como pidió
el usuario. Para continuar el seguimiento sin generar otra mejora:

```
python3 /root/test_runninghub.py --resume ID_DE_TAREA --out /root/prueba-upscaler-4k
```

## Próximas acciones, por orden

1. Revisar capacidad real de conexión del nuevo chat; resolver instancia/VPN/TCP
   sin modificar el proyecto del VPS ni inventar controles de UI.
2. Verificar huella y clave SSH disponible; si falta la privada, generar nueva
   pública y que el usuario la autorice. Nunca pedir claves privadas por chat.
3. Al entrar, solo lectura: recursos, Nginx efectivo sanitizado, puertos,
   contenedores/volúmenes y servicios. Evitar volcar .env, secretos y docker
   inspect completo con Environment. No resetear, reiniciar ni limpiar.
4. Proponer ubicación independiente para upscaler, puerto libre, virtual host
   propio y almacenamiento externo. No prometer capacidad con tan poca RAM.
5. Preparar ejecución 4K real de RunningHub cuando la revisión esté terminada
   y las credenciales se configuren de forma segura. Comparar con Crystal.
6. Solo entonces definir producción, precios y flujos adicionales para creativo
   y retoque. Hoy no existe un despliegue listo ni las seis herramientas validadas.

Preferencias: comunicación clara en español; trabajar de forma autónoma dentro
del alcance autorizado; no mezclar proyectos; no repetir confirmaciones sin motivo;
proteger claves y mantener verificaciones TLS/SSH. El paquete no contiene secretos.
