import sqlalchemy
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List

# --- Database Configuration ---
DATABASE_URL = "sqlite:///./contacts.db"
engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Model ---
class ContactRequest(Base):
    __tablename__ = "contacts"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    nome = sqlalchemy.Column(sqlalchemy.String, index=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True)
    telefone = sqlalchemy.Column(sqlalchemy.String)
    empresa = sqlalchemy.Column(sqlalchemy.String, nullable=True)

Base.metadata.create_all(bind=engine)

# --- Pydantic Schema ---
class ContactSchema(BaseModel):
    nome: str
    email: str
    telefone: str
    empresa: str | None = None

    class Config:
        from_attributes = True

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

# --- Dependency for Database Session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---
# NOTE: API routes are defined *before* the static files mount.

@app.post("/api/contact", response_model=ContactSchema)
def create_contact_request(contact: ContactSchema, db: Session = Depends(get_db)):
    db_contact = ContactRequest(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@app.get("/api/contacts", response_model=List[ContactSchema])
def get_contacts(db: Session = Depends(get_db)):
    return db.query(ContactRequest).all()

@app.get("/contatos", response_class=HTMLResponse)
def view_contacts_page(db: Session = Depends(get_db)):
    contacts = db.query(ContactRequest).order_by(ContactRequest.id.desc()).all()
    
    html_content = """
    <html>
        <head>
            <title>Contatos Salvos</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body { font-family: sans-serif; margin: 2em; background-color: #f8f9fa; color: #212529; }
                h1 { color: #01022E; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="my-4">Contatos Recebidos</h1>
                <table class="table table-striped table-hover">
                    <thead class="table-dark">
                        <tr>
                            <th>ID</th>
                            <th>Nome</th>
                            <th>Email</th>
                            <th>Telefone</th>
                            <th>Empresa</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for contact in contacts:
        html_content += f"""
                        <tr>
                            <td>{contact.id}</td>
                            <td>{contact.nome}</td>
                            <td>{contact.email}</td>
                            <td>{contact.telefone}</td>
                            <td>{contact.empresa}</td>
                        </tr>
        """
    
    html_content += """
                    </tbody>
                </table>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# --- Static Files Mount ---
# This must be the LAST route defined
app.mount("/", StaticFiles(directory="../static", html=True), name="static")
