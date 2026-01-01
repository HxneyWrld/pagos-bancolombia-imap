# Bancolombia Auto – Pagos QR

Aplicación de escritorio desarrollada en Python + PyQt6 que permite leer automáticamente correos de Bancolombia, detectar pagos realizados por QR, mostrarlos en una interfaz gráfica y guardarlos de forma persistente para el control diario en una droguería o negocio.

---

## Características

- Lectura automática de correos vía IMAP (Gmail)
- Detección de pagos QR de Bancolombia
- Interfaz gráfica clara y legible
- Persistencia de pagos en archivo JSON
- Evita pagos duplicados usando UID de correo
- Actualización automática cada 60 segundos
- No se pierden datos al cerrar el programa

---

## Requisitos

- Python 3.10 o superior
- Cuenta de Gmail con IMAP activado
- Contraseña de aplicación de Gmail

---

## Instalación

Clona el repositorio y entra a la carpeta del proyecto:

git clone https://github.com/tu-usuario/pagos-bancolombia-imap  
cd pagos-bancolombia-imap  

(Opcional) Crear entorno virtual:

python -m venv .venv  

Activar el entorno virtual en Windows:

.venv\Scripts\activate  

Activar el entorno virtual en Linux / macOS:

source .venv/bin/activate  

Instalar dependencias:

pip install -r requirements.txt  

---

## Configuración (.env)

Al ejecutar el programa por primera vez, se creará automáticamente el archivo .env.

Edita el archivo .env y completa las variables:

MAIL_USERNAME=tu_correo@gmail.com  
MAIL_PASSWORD=tu_contraseña_de_aplicacion  

IMPORTANTE:
No uses tu contraseña normal de Gmail.
Debes usar una contraseña de aplicación.

---

## Uso

Ejecuta la aplicación con:

python ui.py  

Comportamiento al iniciar:
- Carga pagos guardados previamente
- Sincroniza correos antiguos sin mostrarlos
- A partir de ese momento, solo muestra y guarda pagos nuevos

---

## Persistencia

pagos_guardados.json  
Guarda los pagos detectados para no perderlos al cerrar el programa.

last_uid.txt  
Guarda el UID del último correo procesado para evitar duplicados.

Si se borra last_uid.txt, el sistema se resincroniza automáticamente con el último correo disponible.

---

## Personalización

Puedes cambiar el nombre del negocio editando en el archivo ui.py:

self.label_titulo = QLabel("🏥 NOMBRE DE TU DROGUERÍA")

---

## Mejoras futuras

- Exportar pagos a Excel
- Filtros por fecha y monto
- Notificaciones visuales o sonoras
- Soporte para otros bancos
- Base de datos SQLite