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
    """List all professors"""
    return db.list_professores()


@router.post("/", response_model=Dict[str, Any])
def create_professor(
    professor: ProfessorCreate,
    db: SupabaseDB = Depends(get_db_manager)
):
    """Create a new professor and assign classes"""
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
    """Update a professor and their assigned classes"""
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
    """Delete a professor by ID"""
    success = db.delete_professor(professor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Professor not found")
    return {"message": "Professor deleted successfully"}
