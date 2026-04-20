# Google Classroom Admin

## Project Overview
This project is a tool for automating the administration of Google Classroom courses and student enrollments. It reads course and student data from a Google Sheet and uses the Google Classroom API to create courses and add students.

### Main Technologies
- **Python 3.11+**
- **Google Classroom API**: For course and roster management.
- **Google Sheets API (via gspread)**: For reading source data.
- **OAuth 2.0**: For secure authentication with Google services.

### Inferred Dependencies
- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`
- `gspread`
- `oauth2client`

## Project Structure
- `main.py`: The primary script that executes the automation flow.
- `google-classroom-admin.ipynb`: A Jupyter Notebook ("Classroom Maker") for interactive execution and debugging.
- `credentials.json`: Google Cloud Console OAuth 2.0 credentials (required for setup).
- `token.json`: Stored authentication token, automatically generated after the first successful login.
- `pyproject.toml`: Project metadata and configuration.

## Setup and Requirements
1. **Virtual Environment**: A Python virtual environment should be used (found in `.venv/`).
2. **Google Cloud Project**:
   - Enable Google Classroom API and Google Sheets API.
   - Configure OAuth Consent Screen.
   - Download `credentials.json` and place it in the root directory.
3. **Google Sheet**:
   - The tool expects a specific spreadsheet ID (currently hardcoded in `main.py` as `157s4L5xfjKyaJp90Rg7WpGWwkWe7E0WfG3alOgJ1qws`).
   - The sheet must have tabs named "Asignaturas" and "Curso".

## Building and Running
To run the main automation script:
```bash
python main.py
```

To use the interactive notebook:
- Open `google-classroom-admin.ipynb` in VS Code or Jupyter.

## Development Conventions
- **Debugging**: The script uses a `debug(message)` function for logging internal state and API responses.
- **Authentication**: Supports both OAuth 2.0 (standard) and Service Account credentials (as a fallback for Sheets).
- **Data Mapping**: Column indices for the Google Sheet are defined in the `COLS` dictionary within `main.py`.
