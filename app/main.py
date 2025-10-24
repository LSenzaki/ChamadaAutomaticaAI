"""
main.py
--------
Arquivo principal da aplicação FastAPI.

Responsável por:
- Criar a instância FastAPI
- Configurar middlewares (CORS)
- Incluir os routers de students e faces
- Executar o servidor (uvicorn) no modo debug/reload
"""

from fastapi import FastAPI
# Importe o novo roteador de faces
from app.routers import students, faces 

app = FastAPI(
    title="API de Chamada Facial",
    description="Sistema de reconhecimento facial e registro de presença.",
    version="1.0.0",
)

# Incluir o roteador de alunos (students)
app.include_router(students.router)
# Incluir o novo roteador de faces
app.include_router(faces.router) 

@app.get("/")
def read_root():
    return {"message": "API de Chamada Facial (FastAPI + Supabase) está online!"}

# Remoção da lógica if __name__ == "__main__" se você roda com uvicorn app.main:app