"""
main.py
--------
Arquivo principal da aplicação FastAPI.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import students, faces
from app.models import db_models
from app.models.db_session import Base, engine
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Chamada Automática")

# Lista de origens permitidas.
# Adicione a URL completa do seu frontend Lovable que aparece no erro de CORS.
origins = [
    "https://438e3a3d-8d30-40ad-ab75-20655a7bf554.lovableproject.com", # Domínio do Lovable
    "http://localhost",
    "http://localhost:8080",
    "*" # Curinga para cobrir o ngrok e outros ambientes de teste
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
 )

app.include_router(students.router)
app.include_router(faces.router)

if __name__ == "__main__":
    import uvicorn
    # Corrigido para evitar importação circular e usar host 0.0.0.0
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
