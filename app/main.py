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
from app.routers import students, faces
from app.config import settings # Novo import para configurações

# Removido: toda a importação e lógica de db_session.py e db_models.py

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de Reconhecimento Facial com Supabase e Lovable"
)

# Adicionando Rotas
app.include_router(students.router)
app.include_router(faces.router)

@app.get("/")
def read_root():
    return {"message": "API de Chamada Facial (FastAPI + Supabase) está online!"}

# Remoção da lógica if __name__ == "__main__" se você roda com uvicorn app.main:app