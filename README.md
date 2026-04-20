# Google Classroom Admin 🏫

Herramienta de automatización para la gestión masiva de cursos y alumnos en Google Classroom utilizando datos provenientes de Google Sheets.

## 🚀 Características

- **Creación masiva de cursos**: Genera múltiples cursos en Google Classroom a partir de una lista en una hoja de cálculo.
- **Sincronización de alumnos**: Añade automáticamente estudiantes a sus respectivos cursos.
- **Gestión de profesores**: Soporte para profesores asociados y auxiliares.
- **Doble Autenticación**: Soporta tanto OAuth 2.0 (usuario final) como Cuentas de Servicio.

## 📋 Requisitos Previos

1.  **Python 3.11+**
2.  **Google Cloud Project**:
    - Habilitar **Google Classroom API** y **Google Sheets API**.
    - Configurar la pantalla de consentimiento OAuth.
    - Descargar el archivo `credentials.json` (OAuth 2.0 Client ID) y colocarlo en la raíz del proyecto.
3.  **Google Sheet**: Una hoja de cálculo con el formato adecuado y las pestañas "Asignaturas" y "Curso".

## 🛠️ Instalación

1.  Clona este repositorio.
2.  Crea y activa un entorno virtual:
    ```bash
    python -m venv .venv
    # En Linux/macOS:
    source .venv/bin/activate
    # En Windows:
    .venv\Scripts\activate
    ```
3.  Instala las dependencias necesarias:
    ```bash
    pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib gspread oauth2client
    ```

## 📖 Uso

### Ejecución Directa
Para ejecutar el script principal y procesar la hoja de cálculo configurada:
```bash
python main.py
```
*Nota: La primera vez se abrirá una ventana en tu navegador para autorizar el acceso a tu cuenta de Google.*

### Notebook Interactivo
Si prefieres un entorno más visual o paso a paso, utiliza el archivo:
`google-classroom-admin.ipynb`

## ⚙️ Configuración del Spreadsheet

El ID de la hoja de cálculo está configurado actualmente en `main.py`. Asegúrate de que la hoja tenga las siguientes columnas en la pestaña **Asignaturas**:
- Nombre del curso
- Clase/Sección
- Email del profesor
- (Otras columnas según la definición de `COLS` en el código)

## 🛠️ Estructura del Proyecto

- `main.py`: Lógica principal de ejecución.
- `credentials.json`: Tus credenciales de Google Cloud (No compartir).
- `token.json`: Token de acceso generado tras el primer login.
- `pyproject.toml`: Configuración del proyecto.

## ⚖️ Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
