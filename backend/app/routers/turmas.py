"""
app/routers/turmas.py
---------------------
API endpoints for managing classes (turmas).
"""
from fastapi import APIRouter, Depends, HTTPException
from app.services.db_service import get_db_manager, SupabaseDB
from typing import List, Dict, Any
from pydantic import BaseModel


router = APIRouter(prefix="/turmas", tags=["Turmas"])


# Pydantic schemas
class TurmaCreate(BaseModel):
    nome: str


class TurmaResponse(BaseModel):
    id: int
    nome: str
    created_at: str


@router.get("/", response_model=List[Dict[str, Any]])
def list_turmas(db: SupabaseDB = Depends(get_db_manager)):
    """
    Lista todas as turmas cadastradas no sistema.
    
    Args:
        db: Gerenciador de banco de dados injetado
        
    Returns:
        Lista de turmas com seus dados completos
    """
    return db.list_turmas()


@router.post("/", response_model=Dict[str, Any])
def create_turma(
    turma: TurmaCreate,
    db: SupabaseDB = Depends(get_db_manager)
):
    """
    Cria uma nova turma no sistema.
    
    Args:
        turma: Dados da turma incluindo nome
        db: Gerenciador de banco de dados injetado
        
    Returns:
        Dados da turma criada com ID gerado
    """
    return db.create_turma(nome=turma.nome)


@router.delete("/{turma_id}")
def delete_turma(
    turma_id: int,
    db: SupabaseDB = Depends(get_db_manager)
):
    """
    Remove uma turma do sistema pelo ID.
    
    Args:
        turma_id: ID da turma a ser removida
        db: Gerenciador de banco de dados injetado
        
    Returns:
        Mensagem de confirmação da remoção
        
    Raises:
        HTTPException: 404 se a turma não for encontrada
    """
    success = db.delete_turma(turma_id)
    if not success:
        raise HTTPException(status_code=404, detail="Class not found")
    return {"message": "Class deleted successfully"}
