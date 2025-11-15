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
    """List all classes"""
    return db.list_turmas()


@router.post("/", response_model=Dict[str, Any])
def create_turma(
    turma: TurmaCreate,
    db: SupabaseDB = Depends(get_db_manager)
):
    """Create a new class"""
    return db.create_turma(nome=turma.nome)


@router.delete("/{turma_id}")
def delete_turma(
    turma_id: int,
    db: SupabaseDB = Depends(get_db_manager)
):
    """Delete a class by ID"""
    success = db.delete_turma(turma_id)
    if not success:
        raise HTTPException(status_code=404, detail="Class not found")
    return {"message": "Class deleted successfully"}
