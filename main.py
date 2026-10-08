import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import sys
import argparse

# ==============================
# CONFIGURACIÓN DE CREDENCIALES
# ==============================
SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses",
    "https://www.googleapis.com/auth/classroom.rosters",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Configuración para autenticación OAuth
CLIENT_SECRET_FILE = "credentials.json"
TOKEN_FILE = "token.json"


# Función de depuración
def debug(message):
    print(f"DEBUG: {message}")


# Autenticación con OAuth 2.0
def get_oauth_credentials():
    debug(f"Intentando obtener credenciales OAuth desde {TOKEN_FILE}")
    creds = None
    if os.path.exists(TOKEN_FILE):
        debug(f"Archivo {TOKEN_FILE} encontrado")
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Si no hay credenciales (o no son válidas), solicitamos autorización
    if not creds or not creds.valid:
        debug("Credenciales no válidas o no existentes")
        if creds and creds.expired and creds.refresh_token:
            debug("Intentando refrescar token caducado")
            creds.refresh(Request())
        else:
            debug(f"Iniciando flujo de autorización con {CLIENT_SECRET_FILE}")
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Guardar las credenciales para la próxima ejecución
        debug(f"Guardando credenciales en {TOKEN_FILE}")
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds


# ==============================
# INICIALIZACIÓN DE SERVICIOS
# ==============================


def init_services():
    """Autentica y crea los clientes de Classroom y Sheets."""
    global credentials, classroom_service, gc

    try:
        # Obtener credenciales para Google Classroom
        debug("Obteniendo credenciales OAuth")
        credentials = get_oauth_credentials()

        # Crear cliente para Google Classroom
        debug("Creando servicio de Google Classroom")
        classroom_service = build("classroom", "v1", credentials=credentials)
        debug("Servicio de Google Classroom creado correctamente")

        # Para Google Sheets, usamos otro método de autenticación
        debug("Configurando acceso a Google Sheets")

        # MÉTODO 1: Usando credenciales OAuth directamente
        debug("Intentando autorizar gspread con credenciales OAuth")
        try:
            gc = gspread.authorize(credentials)
            debug("Autorización de gspread exitosa usando OAuth")
        except Exception as e:
            debug(f"Error autorizando gspread con OAuth: {e}")

            # MÉTODO 2: Usando credenciales de cuenta de servicio
            debug("Intentando con credenciales de cuenta de servicio...")
            try:
                # Verificar si existe client_secret.json
                if os.path.exists("client_secret.json"):
                    debug("Usando client_secret.json para servicio de Sheets")
                    scope = [
                        "https://spreadsheets.google.com/feeds",
                        "https://www.googleapis.com/auth/drive",
                    ]
                    service_creds = ServiceAccountCredentials.from_json_keyfile_name(
                        "client_secret.json", scope
                    )
                    gc = gspread.authorize(service_creds)
                    debug("Autorización de gspread exitosa usando cuenta de servicio")
                else:
                    debug("No se encontró client_secret.json, abortando")
                    raise Exception("No se encontró archivo de credenciales de servicio")
            except Exception as inner_e:
                debug(f"Error con método alternativo: {inner_e}")
                raise

    except Exception as e:
        print(f"Error durante la inicialización: {e}")
        sys.exit(1)


# ==============================
# LECTURA DE DATOS DE GOOGLE SHEETS
# ==============================
SPREADSHEET_ID = "157s4L5xfjKyaJp90Rg7WpGWwkWe7E0WfG3alOgJ1qws"


def load_sheets():
    """Lee las pestañas 'Asignaturas' y 'Curso' del Sheet."""
    global sheet_cursos, sheet_alumnos, cursos, alumnos

    try:
        print("Intentando abrir la hoja de cálculo...")
        debug(f"Abriendo hoja con ID: {SPREADSHEET_ID}")

        # Comprobación de acceso a la API
        debug("Verificando que API de Google Drive está accesible")
        drive_service = build("drive", "v3", credentials=credentials)
        test_response = drive_service.files().list(pageSize=1).execute()
        debug("API de Drive accesible")

        # Comprobación de permisos sobre el archivo
        debug(f"Comprobando permisos sobre archivo {SPREADSHEET_ID}")
        try:
            file_info = (
                drive_service.files()
                .get(fileId=SPREADSHEET_ID, fields="name,owners")
                .execute()
            )
            debug(f"Información del archivo: {file_info}")
        except Exception as e:
            debug(f"No se pudo acceder a la información del archivo: {e}")

        # Intento de apertura del archivo
        try:
            spreadsheet = gc.open_by_key(SPREADSHEET_ID)
            debug("Hoja de cálculo abierta correctamente")
            print("Hoja de cálculo abierta correctamente.")
        except gspread.exceptions.SpreadsheetNotFound:
            debug("Hoja de cálculo no encontrada")
            print(
                f"Error: La hoja de cálculo con ID {SPREADSHEET_ID} no existe o no tienes permisos para acceder a ella."
            )
            sys.exit(1)
        except Exception as e:
            debug(f"Error desconocido abriendo hoja: {e}")
            raise

        print("Obteniendo hoja 'Asignaturas'...")
        sheet_cursos = spreadsheet.worksheet("Asignaturas")
        print("Obteniendo hoja 'Curso'...")
        sheet_alumnos = spreadsheet.worksheet("Curso")

        print("Leyendo datos de cursos...")
        cursos = sheet_cursos.get_all_values()[1:]  # Saltar encabezados
        print(f"Leídos {len(cursos)} cursos.")

        print("Leyendo datos de alumnos...")
        alumnos = sheet_alumnos.get_all_values()[1:]  # Saltar encabezados
        print(f"Leídos {len(alumnos)} alumnos.")
    except Exception as e:
        print(f"Error al acceder a Google Sheets: {str(e)}")
        print("Posibles soluciones:")
        print(
            "1. Asegúrate de que el archivo de credenciales tiene los permisos necesarios para acceder a este documento."
        )
        print(
            "2. Verifica que has compartido la hoja de cálculo con la dirección de correo del usuario autorizado."
        )
        print(
            "3. Si usas una cuenta de servicio, comparte la hoja con el email de la cuenta de servicio."
        )
        print("4. Verifica que el ID de la hoja de cálculo es correcto.")
        debug("Terminando programa debido a error en acceso a Sheets")
        sys.exit(1)


# Definir índices de columnas
COLS = {
    "CourseName": 0,
    "ClassName": 1,
    "MailAssociateTeacher": 3,
    "Section": 4,
    "Description": 5,
    "Room": 6,
    "CourseID": 7,
    "MailAssistantTeacher": 8,
}

# ==============================
# CREACIÓN DE CURSOS EN CLASSROOM
# ==============================


def create_students(course_id, group):
    """Añadir estudiantes al curso en Google Classroom."""
    print(f"Añadiendo estudiantes al curso {course_id}...")
    estudiantes_anadidos = 0

    for alumno in alumnos:
        student_email = alumno[2]  # Columna con el correo del estudiante
        if not student_email or "@" not in student_email:
            print(f"Correo de estudiante inválido: {student_email}")
            continue

        student_data = {"userId": student_email}
        try:
            classroom_service.courses().students().create(
                courseId=course_id, body=student_data
            ).execute()
            print(f"Estudiante {student_email} añadido al curso {course_id}")
            estudiantes_anadidos += 1
        except Exception as e:
            print(f"Error añadiendo {student_email}: {e}")

    print(f"Total de estudiantes añadidos: {estudiantes_anadidos}")


def create_courses():
    """Crear cursos en Google Classroom y asignar profesores."""
    print("Iniciando creación de cursos...")
    cursos_creados = 0

    for fila, curso in enumerate(cursos):
        nombre_curso = curso[COLS["CourseName"]]
        print(f"\nProcesando curso: {nombre_curso}")

        course_data = {
            "name": nombre_curso,
            "section": curso[COLS["Section"]],
            "descriptionHeading": curso[COLS["Description"]],
            "room": curso[COLS["Room"]],
            "ownerId": "me",  # "me" se refiere al usuario autenticado
            "courseState": "ACTIVE",
        }

        try:
            print(f"Creando curso en Classroom: {nombre_curso}")
            course = classroom_service.courses().create(body=course_data).execute()
            course_id = course["id"]
            print(f"Curso creado: {course['name']} (ID: {course_id})")
            cursos_creados += 1

            # Añadir profesor principal si es diferente del usuario autenticado
            if curso[COLS["MailAssociateTeacher"]]:
                email_profesor = curso[COLS["MailAssociateTeacher"]]
                if "@" in email_profesor:  # Validación básica de email
                    teacher_data = {"userId": email_profesor}
                    try:
                        classroom_service.courses().teachers().create(
                            courseId=course_id, body=teacher_data
                        ).execute()
                        print(f"Profesor principal {email_profesor} asignado")
                    except Exception as e:
                        print(
                            f"Error asignando profesor principal {email_profesor}: {e}"
                        )
                else:
                    print(f"Email de profesor principal inválido: {email_profesor}")

            # Añadir profesor asistente
            if curso[COLS["MailAssistantTeacher"]]:
                email_asistente = curso[COLS["MailAssistantTeacher"]]
                if "@" in email_asistente:  # Validación básica de email
                    teacher_data = {"userId": email_asistente}
                    try:
                        classroom_service.courses().teachers().create(
                            courseId=course_id, body=teacher_data
                        ).execute()
                        print(f"Profesor asistente {email_asistente} asignado")
                    except Exception as e:
                        print(
                            f"Error asignando profesor asistente {email_asistente}: {e}"
                        )
                else:
                    print(f"Email de profesor asistente inválido: {email_asistente}")

            # Actualizar ID del curso en la hoja
            print(f"Actualizando ID de curso en la hoja de cálculo...")
            try:
                sheet_cursos.update_cell(fila + 2, COLS["CourseID"] + 1, course_id)
                print("ID de curso actualizado en la hoja")
            except Exception as e:
                print(f"Error actualizando ID en la hoja: {e}")

            # Añadir estudiantes
            create_students(course_id, curso[COLS["ClassName"]])

        except Exception as e:
            print(f"Error creando curso {nombre_curso}: {e}")

    print(f"\nResumen: {cursos_creados} cursos creados de {len(cursos)} intentados")


# ==============================
# MATRICULAR ESTUDIANTES NUEVOS
# ==============================


def add_student(emails, curso, dry_run=False):
    """Añadir estudiantes a todas las asignaturas de un curso (ClassName)."""
    curso_norm = curso.strip().casefold()
    asignaturas = [
        fila for fila in cursos if fila[COLS["ClassName"]].strip().casefold() == curso_norm
    ]

    if not asignaturas:
        disponibles = sorted({fila[COLS["ClassName"]].strip() for fila in cursos} - {""})
        print(f"No se encontraron asignaturas para el curso '{curso}'.")
        print(f"Cursos disponibles: {', '.join(disponibles)}")
        return

    print(f"Encontradas {len(asignaturas)} asignaturas para el curso '{curso}'.")
    agregados = ya_existentes = omitidos = errores = 0

    for email in emails:
        email = email.strip()
        if "@" not in email:
            print(f"Correo de estudiante inválido: {email}")
            omitidos += 1
            continue

        print(f"\nProcesando estudiante: {email}")
        for fila in asignaturas:
            nombre_curso = fila[COLS["CourseName"]]
            course_id = fila[COLS["CourseID"]].strip()
            if not course_id:
                print(f"Asignatura {nombre_curso} sin CourseID, se omite")
                omitidos += 1
                continue

            if dry_run:
                print(f"[dry-run] Se añadiría a {nombre_curso} (ID: {course_id})")
                continue

            try:
                classroom_service.courses().students().create(
                    courseId=course_id, body={"userId": email}
                ).execute()
                print(f"Añadido a {nombre_curso} (ID: {course_id})")
                agregados += 1
            except HttpError as e:
                if e.resp.status == 409:
                    print(f"Ya estaba matriculado en {nombre_curso} (ID: {course_id})")
                    ya_existentes += 1
                else:
                    print(f"Error añadiendo a {nombre_curso} (ID: {course_id}): {e}")
                    errores += 1

    print(
        f"\nResumen: {agregados} añadidos, {ya_existentes} ya existentes, "
        f"{omitidos} omitidos, {errores} errores"
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Administración de Google Classroom")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "create-courses", help="Crear todos los cursos de la hoja (comportamiento por defecto)"
    )

    add_parser = subparsers.add_parser(
        "add-student", help="Añadir estudiantes a todas las asignaturas de un curso"
    )
    add_parser.add_argument(
        "--email",
        action="append",
        required=True,
        help="Correo del estudiante (se puede repetir para varios estudiantes)",
    )
    add_parser.add_argument(
        "--curso", required=True, help="Curso (columna ClassName de 'Asignaturas'), p. ej. '1°A'"
    )
    add_parser.add_argument(
        "--dry-run", action="store_true", help="Mostrar qué se haría sin modificar Classroom"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    print(f"Usando archivo de credenciales: {CLIENT_SECRET_FILE}")
    init_services()
    load_sheets()

    if args.command == "add-student":
        print("=== Añadiendo estudiantes a Google Classroom ===")
        add_student(args.email, args.curso, dry_run=args.dry_run)
    else:
        print("=== Iniciando programa de creación de cursos en Google Classroom ===")
        create_courses()
    print("=== Programa finalizado ===")
