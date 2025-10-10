import gspread
from google.oauth2.service_account import Credentials
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# --- DEBUGGING CODE ---
print("--- DEBUGGING FILE PATHS ---")
print(f"Current Working Directory: {os.getcwd()}")
print("\n--- Files in Project Root (`../`) ---")
try:
    print(os.listdir('../'))
except Exception as e:
    print(e)
print("\n--- Files in Backend Root (`./`) ---")
try:
    print(os.listdir('.'))
except Exception as e:
    print(e)
print("--- END DEBUGGING ---")
# --- END DEBUGGING CODE ---

# --- Pydantic Schema ---
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

SERVICE_ACCOUNT_FILE = '../google_credentials.json'
SHEET_URL = "https://docs.google.com/spreadsheets/d/1etHPBytBN5KHX8WOQHb4TIVJWpVG7Tp7DVrpp8MKryI/edit?pli=1&gid=0#gid=0"

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
    if not creds:
        raise HTTPException(status_code=500, detail="Google credentials not found. Check Secret File configuration.")
    try:
        # Open the spreadsheet by URL and select the first worksheet
        sheet = client.open_by_url(SHEET_URL).sheet1

        # Prepare the row data
        row = [contact.nome, contact.email, contact.telefone, contact.empresa]
        
        # Append the new row
        sheet.append_row(row)
        
        return contact
    except gspread.exceptions.SpreadsheetNotFound:
        raise HTTPException(status_code=404, detail="Spreadsheet not found. Check the URL and sharing settings.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

# --- Static Files Mount ---
app.mount("/", StaticFiles(directory="../static", html=True), name="static")