"""
app/routers/alunos.py
---------------------
API endpoints for managing students (alunos).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.db_service import get_db_manager, SupabaseDB
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


router = APIRouter(prefix="/alunos", tags=["Alunos"])


# Pydantic schemas
class AlunoCreate(BaseModel):
    nome: str
    turma_id: Optional[int] = None
    check_professor: bool = False


class AlunoUpdate(BaseModel):
    nome: Optional[str] = None
    turma_id: Optional[int] = None
    check_professor: Optional[bool] = None
    ativo: Optional[bool] = None


class AlunoResponse(BaseModel):
    id: int
    nome: str
    turma_id: Optional[int]
    check_professor: bool
    ativo: bool
    created_at: str


@router.get("/", response_model=List[Dict[str, Any]])
def list_alunos(
    turma_id: Optional[int] = Query(None, description="Filter by class ID"),
    db: SupabaseDB = Depends(get_db_manager)
):
    """List all students, optionally filtered by class"""
    return db.list_alunos(turma_id=turma_id)


@router.get("/{aluno_id}", response_model=Dict[str, Any])
def get_aluno(
    aluno_id: int,
    db: SupabaseDB = Depends(get_db_manager)
):
    """Get a student by ID"""
    aluno = db.get_aluno_by_id(aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Student not found")
    return aluno


@router.post("/", response_model=Dict[str, Any])
def create_aluno(
    aluno: AlunoCreate,
    db: SupabaseDB = Depends(get_db_manager)
):
    """Create a new student"""
    return db.create_aluno(
        nome=aluno.nome,
        turma_id=aluno.turma_id,
        check_professor=aluno.check_professor
    )


@router.put("/{aluno_id}", response_model=Dict[str, Any])
def update_aluno(
    aluno_id: int,
    aluno: AlunoUpdate,
    db: SupabaseDB = Depends(get_db_manager)
):
    """Update student information"""
    # Only include fields that were provided
    update_data = {k: v for k, v in aluno.dict().items() if v is not None}
    
    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields to update"
        )
    
    result = db.update_aluno(aluno_id, **update_data)
    if not result:
        raise HTTPException(status_code=404, detail="Student not found")
    return result


@router.delete("/{aluno_id}")
def delete_aluno(
    aluno_id: int,
    db: SupabaseDB = Depends(get_db_manager)
):
    """Delete a student by ID"""
    success = db.delete_aluno(aluno_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully"}
