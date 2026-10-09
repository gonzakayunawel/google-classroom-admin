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

### Agregar un estudiante nuevo
Cuando llega un estudiante a un curso ya creado, se le puede matricular en todas las asignaturas de su curso (columna *Clase* de la pestaña **Asignaturas**):
```bash
python main.py add-student --curso "1°A" --email alumno@colegio.cl
```
- `--email` se puede repetir para agregar varios estudiantes del mismo curso.
- `--dry-run` muestra en qué asignaturas se matricularía, sin modificar Classroom.
- Usa el *CourseID* (columna H de **Asignaturas**), que la carga inicial (`python main.py` o `python main.py create-courses`) escribe automáticamente. Las asignaturas sin *CourseID* se omiten con un aviso.

### Clases huérfanas (profesor eliminado)
Si se elimina la cuenta de un profesor sin traspasar antes sus clases, estas quedan sin propietario ("Unknown User") y ya no se pueden modificar. Pasados 20 días la cuenta no se puede restaurar desde Admin console.

> Se requiere el scope `classroom.profile.emails`. Si ya tenías un `token.json`, bórralo y vuelve a autorizar. La cuenta debe ser superadministradora.

1. Buscar las clases huérfanas del dominio:
   ```bash
   python main.py find-orphans --csv huerfanas.csv
   ```
2. Revisar qué se haría con cada una, sin modificar nada:
   ```bash
   python main.py fix-orphan --course-id 123456789 --dry-run
   ```
3. Recuperarlas (`--course-id` se puede repetir; `--owner` es por defecto la cuenta autenticada):
   ```bash
   python main.py fix-orphan --course-id 123456789 --owner aulas@colegio.cl
   ```
   Primero se intenta cambiar el propietario por API, lo que conservaría todo el contenido. Si Google lo rechaza, el script explica los cambios y pide autorización (`[s/N]`) antes de crear una clase nueva con los mismos profesores y alumnos, actualizar el *CourseID* en **Asignaturas** e intentar archivar la clase vieja.

   **No se recuperan** las publicaciones, tareas, materiales ni calificaciones, y la clase nueva tiene otro código.

**Para evitarlo:** antes de eliminar a un profesor, suspende su cuenta y traspasa sus clases a otro profesor.

### Quitar una cuenta de sus clases
Para sacar a una cuenta (por ejemplo, la de administración) de todas las clases activas donde es co-profesor:
```bash
python main.py remove-teacher --email admin@colegio.cl --dry-run   # revisar
python main.py remove-teacher --email admin@colegio.cl             # pide confirmación [s/N]
```
Las clases de las que esa cuenta es propietaria se omiten, porque primero habría que traspasarlas. Los materiales que haya publicado se mantienen.

> Al crear cursos (`create-courses`), el propietario es el profesor de la columna *MailAssociateTeacher*. Si ese correo falta, el propietario es la cuenta autenticada.

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
