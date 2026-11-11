# Radio La Grande de Huétamo — Android 17

Proyecto Android Studio + panel PHP para cPanel. No usa Firebase ni MySQL; la configuración se guarda en JSON.

## Subir panel a cPanel
Copia las carpetas `admin/`, `api/`, `storage/` y `uploads/` a `public_html/radio/`. Usa PHP 8+ y HTTPS. Permisos de escritura para `storage/` y `uploads/`: 755 o 775 según el hosting.

Panel: `https://TU-DOMINIO/radio/admin/`
Usuario inicial: `admin`
Contraseña inicial: `RadioAdmin2026!` (cámbiala antes de publicar).
JSON: `https://TU-DOMINIO/radio/api/config.php`

## Conectar Android
Abre `app/src/main/assets/index.html` y configura dentro de `DEFAULTS`:
```js
apiUrl:"https://TU-DOMINIO.com/radio/api/config.php",
```
Reemplaza el dominio por el tuyo.

## Android Studio
SDK Platform 37, Android Gradle Plugin 9.5.0 y Gradle 9.6. Abre esta carpeta como proyecto y sincroniza. Compila con **Build > Build Bundle(s) / APK(s) > Build APK(s)**.

El panel permite cambiar logo, fondo, colores, nombre, streaming, chat/WhatsApp y gestionar enlaces (agregar, editar, activar/desactivar, ordenar y eliminar). La reproducción actual es en pantalla; no incluye servicio persistente de audio en segundo plano.
