# Radio La Grande de Huétamo — Android y panel de control

Proyecto Android Studio con panel administrativo PHP para alojamiento cPanel/Hostinger. No utiliza Firebase ni MySQL: la configuración de la emisora se guarda en un archivo JSON.

## Componentes

- `app/`: aplicación Android.
- `admin/`: panel web para administrar la identidad visual, streaming, chat y enlaces.
- `api/`: endpoint JSON que consume la aplicación.
- `storage/`: configuración persistente de la emisora.
- `uploads/`: imágenes subidas desde el panel.

## Instalación del panel en Hostinger/cPanel

1. Crea la carpeta `public_html/radio/`.
2. Sube el contenido de esta carpeta del proyecto (`admin/`, `api/`, `storage/` y `uploads/`) dentro de `public_html/radio/`.
3. Usa PHP 8 o superior y activa HTTPS.
4. Comprueba que `storage/` y `uploads/` tengan permisos de escritura para PHP (normalmente 755 o 775, según el hosting).
5. Abre `https://TU-DOMINIO/radio/admin/`.
6. Inicia sesión con el usuario y la contraseña entregados junto con este paquete. Cambia la contraseña después del primer acceso.

La API de configuración queda en `https://TU-DOMINIO/radio/api/config.php`.

## Conectar la aplicación Android

Abre `app/src/main/assets/index.html` y sustituye el valor de `apiUrl` dentro de `DEFAULTS`:

```js
apiUrl: "https://TU-DOMINIO/radio/api/config.php",
```

Usa tu dominio real con HTTPS.

## Abrir en Android Studio

1. Abre la carpeta `radio-la-grande-app` como proyecto.
2. Deja que Android Studio sincronice Gradle.
3. Instala el SDK indicado por el proyecto.
4. Selecciona **Build > Build Bundle(s) / APK(s) > Build APK(s)** para generar el APK.

## Funciones del panel

Permite cambiar nombre de la emisora, textos, colores, logo, fondo, URL de streaming, chat/WhatsApp y administrar enlaces (agregar, editar, activar, desactivar, ordenar y eliminar).

**Nota:** la reproducción actual está integrada en la pantalla de la aplicación; esta versión no incluye un servicio de audio persistente en segundo plano.
