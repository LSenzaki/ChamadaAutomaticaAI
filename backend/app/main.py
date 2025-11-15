"""
main.py
--------
Main FastAPI application file.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    students, faces, comparison,
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
# New schema routers
app.include_router(turmas.router)
app.include_router(professores.router)
app.include_router(alunos.router)
app.include_router(presencas.router)

# Legacy routers (for backward compatibility)
app.include_router(students.router)
app.include_router(faces.router)
app.include_router(comparison.router)


@app.get("/")
def root():
    """API root endpoint"""
    return {
        "message": "Sistema de Chamada Automática API",
        "version": "2.0",
        "endpoints": {
            "turmas": "/turmas",
            "professores": "/professores",
            "alunos": "/alunos",
            "presencas": "/presencas",
            "legacy_students": "/students",
            "legacy_faces": "/faces",
            "legacy_comparison": "/comparison"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

