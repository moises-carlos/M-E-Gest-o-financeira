import gspread
from google.oauth2.service_account import Credentials
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# --- Pydantic Schema ---
# Defines the expected data structure for a request.
class ContactSchema(BaseModel):
    nome: str
    email: str
    telefone: str
    empresa: str | None = None

# --- Google Sheets Configuration ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]

# The secret file is read from the path where we saved it in Render
SERVICE_ACCOUNT_FILE = 'google_credentials.json'
SHEET_NAME = "megestao"

# Authenticate and get the gspread client
creds = None
if os.path.exists(SERVICE_ACCOUNT_FILE):
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

# --- FastAPI App Initialization ---
app = FastAPI(title="ME Gestão Financeira API", version="1.0")

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# --- API Endpoints ---
@app.post("/api/contact", response_model=ContactSchema)
def create_contact_request(contact: ContactSchema):
    """
    Receives contact form data and appends it to a Google Sheet.
    """
    if not creds:
        return {"error": "Google credentials not found. Check Secret File configuration."}
    try:
        # Open the spreadsheet and select the first worksheet
        sheet = client.open(SHEET_NAME).sheet1

        # Prepare the row data in the correct order
        # Assumes columns are: Nome, Email, Telefone, Empresa
        row = [contact.nome, contact.email, contact.telefone, contact.empresa]
        
        # Append the new row
        sheet.append_row(row)
        
        return contact
    except gspread.exceptions.SpreadsheetNotFound:
        return {"error": f"Spreadsheet named '{SHEET_NAME}' not found. Check the name and sharing settings."}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

# --- Static Files Mount ---
# This must be the LAST route defined
app.mount("/", StaticFiles(directory="../static", html=True), name="static")