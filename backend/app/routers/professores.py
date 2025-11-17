"""
app/routers/professores.py
---------------------------
API endpoints for managing professors.
"""
from fastapi import APIRouter, Depends, HTTPException
from app.services.db_service import get_db_manager, SupabaseDB
from typing import List, Dict, Any
from pydantic import BaseModel


router = APIRouter(prefix="/professores", tags=["Professores"])


# Pydantic schemas
class ProfessorCreate(BaseModel):
    nome: str
    email: str
    turma_ids: List[int] = []


class ProfessorUpdate(BaseModel):
    nome: str = None
    email: str = None
    turma_ids: List[int] = None
    ativo: bool = None


class ProfessorResponse(BaseModel):
    id: int
    nome: str
    email: str
    ativo: bool
    created_at: str


@router.get("/", response_model=List[Dict[str, Any]])
def list_professores(db: SupabaseDB = Depends(get_db_manager)):
    """
    Lista todos os professores cadastrados no sistema.
    
    Args:
        db: Gerenciador de banco de dados injetado
        
    Returns:
        Lista de professores com seus dados completos
    """
    return db.list_professores()


@router.post("/", response_model=Dict[str, Any])
def create_professor(
    professor: ProfessorCreate,
    db: SupabaseDB = Depends(get_db_manager)
):
    """
    Cria um novo professor e atribui turmas a ele.
    
    Args:
        professor: Dados do professor incluindo nome, email e IDs das turmas
        db: Gerenciador de banco de dados injetado
        
    Returns:
        Dados do professor criado com ID gerado
    """
    return db.create_professor(
        nome=professor.nome,
        email=professor.email,
        turma_ids=professor.turma_ids
    )


@router.put("/{professor_id}", response_model=Dict[str, Any])
def update_professor(
    professor_id: int,
    professor: ProfessorUpdate,
    db: SupabaseDB = Depends(get_db_manager)
):
    """
    Atualiza os dados de um professor e suas turmas atribuídas.
    
    Args:
        professor_id: ID do professor a ser atualizado
        professor: Dados a serem atualizados (campos opcionais)
        db: Gerenciador de banco de dados injetado
        
    Returns:
        Dados atualizados do professor
    """
    return db.update_professor(
        professor_id=professor_id,
        nome=professor.nome,
        email=professor.email,
        turma_ids=professor.turma_ids,
        ativo=professor.ativo
    )


@router.delete("/{professor_id}")
def delete_professor(
    professor_id: int,
    db: SupabaseDB = Depends(get_db_manager)
):
    """
    Remove um professor do sistema pelo ID.
    
    Args:
        professor_id: ID do professor a ser removido
        db: Gerenciador de banco de dados injetado
        
    Returns:
        Mensagem de confirmação da remoção
        
    Raises:
        HTTPException: 404 se o professor não for encontrado
    """
    success = db.delete_professor(professor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Professor not found")
    return {"message": "Professor deleted successfully"}
