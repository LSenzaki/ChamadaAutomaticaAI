"""
main.py
--------
Main FastAPI application file.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    turmas, professores, alunos, presencas
)

app = FastAPI(title="Sistema de Chamada Automática")

# CORS configuration
# Add your frontend URLs here
origins = [
    "https://438e3a3d-8d30-40ad-ab75-20655a7bf554.lovableproject.com",
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "*"  # Wildcard for ngrok and test environments
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(turmas.router)
app.include_router(professores.router)
app.include_router(alunos.router)
app.include_router(presencas.router)


@app.get("/")
def root():
    """API root endpoint"""
    return {
        "message": "Sistema de Chamada Automática API",
        "version": "3.0",
        "description": "Face recognition attendance system",
        "endpoints": {
            "turmas": "/turmas - Manage classes",
            "professores": "/professores - Manage professors",
            "alunos": "/alunos - Manage students",
            "presencas": "/presencas - Manage attendance",
            "cadastrar": "/alunos/cadastrar - Register student with photos",
            "reconhecer": "/alunos/reconhecer - Recognize face and register attendance",
            "teste": "/alunos/reconhecer/teste - Test face recognition"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

