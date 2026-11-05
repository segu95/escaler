# Revisión del VPS — 5 de noviembre de 2026

Revisión por SSH completada aproximadamente a las 14:29 America/Lima.
Solo consultas: no se instalaron paquetes, reiniciaron servicios, modificaron
configuraciones, consultaron bases de datos ni limpiaron archivos en el VPS.
La autenticación puede generar los registros normales del sistema.

## Acceso verificado

- VPS: `Serversegu`, Tailscale `100.98.148.18`, OpenSSH puerto 22, usuario root.
- Conexión mediante HTTP CONNECT de `proxy:8088`, ejecución escalada autorizada.
- Huella ED25519 comprobada antes de autenticar:
  `SHA256:lSPOGe280XZdF0u3tAE40yaGF0U1TsghwghL1T3eykI`.
- La clave anterior no estaba disponible. Se generó una nueva en este entorno;
  el propietario confirmó la instalación de su pública y SSH autenticó.
- Privada fuera del repositorio: `/workspace/.upscaler-access/id_ed25519`.
  No se debe publicar, copiar a documentación ni asumir disponible en otro entorno.
- El entorno declara VPN configurada y listas TCP vacías, pero el CONNECT real
  respondió 200 y SSH funcionó. Esta prueba demuestra acceso en esta instancia;
  las listas declaradas por sí solas no reflejaron el resultado observado.
- GitHub también requiere la ejecución escalada en esta sesión. La vía normal
  falló al conectar con el proxy; no se desactivó el proxy ni la verificación TLS.

## Recursos y servicios observados

| Recurso | Medición |
|---|---|
| CPU | 1 CPU; carga 0,01 / 0,18 / 0,13 |
| RAM | 913 MiB totales; 176 MiB disponibles |
| Swap | 0 |
| Disco raíz | 14 GB; 84 % ocupado; 2,3 GB disponibles |
| Caché de build Docker | 2,76 GB; 2,415 GB reportados recuperables; sin limpieza |

Docker mantiene el proyecto `segu-downloads`, definido en
`/opt/segu-downloads/compose.yaml`:

- `segu_web`: imagen `segu-downloads-web`, `127.0.0.1:8000`, unos 167 MiB RAM.
- `segu_db`: `postgres:16-alpine`, healthy, unos 22 MiB RAM.
- `segu_redis`: `redis:7-alpine`, healthy, unos 3 MiB RAM.
- Red `segu-downloads_default`; volúmenes `segu-downloads_postgres_data` y
  `segu-downloads_redis_data`. Ningún límite de memoria configurado en los tres
  contenedores (`HostConfig.Memory=0`). No se leyeron datos ni Environment.

`segutube-premium.service` está activo, usa el usuario `segutube-premium`,
trabaja en `/opt/segutube-premium/current`, escucha en `127.0.0.1:8011`, consume
unos 44,5 MiB y tiene límite de 128 MiB. Nginx, Docker, SSH y Tailscale están activos.
UFW permite OpenSSH, 80/tcp y 443/tcp para IPv4/IPv6.

## Nginx efectivo

Se consultó `nginx -T` y se devolvieron solo directivas seleccionadas. No se
leyeron claves TLS, archivos .env ni configuraciones completas de contenedores.

| Dominio | Destino |
|---|---|
| segutools.store, www.segutools.store | 127.0.0.1:8000 |
| magnific.segutools.store | 127.0.0.1:8000 |
| admin.segutools.store, api.segutools.store | 127.0.0.1:8011 |
| segutube.segutools.store | Estáticos en /var/www/segutube-web/current |

No existe `server_name upscaler.segutools.store` en la configuración consultada.
Por tanto no hay un virtual host independiente para ese nombre; si una petición
llega a este Nginx con ese nombre, puede atenderla el servidor predeterminado del
socket. La respuesta pública histórica /panel/ no prueba un despliegue del upscaler.
No se volvió a validar DNS ni el certificado público del subdominio en esta revisión.

## Propuesta independiente, pendiente de implementación

- Código: `/opt/segutools-upscaler`.
- Estado mínimo: `/var/lib/segutools-upscaler`, con usuario de servicio propio.
- Servicio: `segutools-upscaler.service`.
- Backend: `127.0.0.1:8020`, libre en la medición; revalidar antes de desplegar.
- Sitio Nginx propio: `/etc/nginx/sites-available/upscaler.segutools.store`,
  con certificado válido para ese nombre y límite de subida acorde a 10 MiB
  más el overhead de la solicitud.
- Almacenamiento de imágenes externo, con caducidad; procesamiento IA externo.
- Sin reutilizar los volúmenes, bases de datos, credenciales, red Docker ni el
  compose del proyecto existente.

Las rutas propuestas no existen actualmente. Nada de lo anterior se creó en el VPS.
La separación de procesos no elimina la competencia por RAM y disco. Con 176 MiB
 disponibles y sin swap no se ha demostrado capacidad para producción: conviene
ampliar recursos o usar otro servidor para el backend. Evitar procesamiento local
8K y builds pesados en este VPS. Una eventual limpieza necesita autorización y
no sustituye una evaluación de capacidad de memoria.

## Pendiente

1. Elegir capacidad y alojamiento del nuevo backend antes de desplegar.
2. Preparar y validar la integración externa; aún no hay aplicación terminada.
3. Las pruebas reales de RunningHub siguen pendientes de credencial y ejecución
   facturable; no se enviaron trabajos durante esta revisión.
4. Cualquier despliegue o cambio de Nginx/servicios queda fuera de esta revisión.
