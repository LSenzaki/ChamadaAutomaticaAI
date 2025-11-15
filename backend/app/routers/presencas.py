"""
app/routers/presencas.py
-------------------------
API endpoints for managing attendance (presencas).
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.db_service import get_db_manager, SupabaseDB
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


router = APIRouter(prefix="/presencas", tags=["Presencas"])


# Pydantic schemas
class PresencaCreate(BaseModel):
    aluno_id: int
    turma_id: int
    confianca: Optional[float] = None


class PresencaValidate(BaseModel):
    professor_id: int
    observacao: Optional[str] = None


class PresencaResponse(BaseModel):
    id: int
    aluno_id: int
    turma_id: Optional[int]
    data_hora: str
    confianca: Optional[float]
    check_professor: bool
    validado_em: Optional[str]
    validado_por: Optional[int]


@router.get("/", response_model=List[Dict[str, Any]])
def list_presencas(
    data_inicio: Optional[str] = Query(
        None, description="Start date (ISO format)"
    ),
    data_fim: Optional[str] = Query(
        None, description="End date (ISO format)"
    ),
    turma_id: Optional[int] = Query(None, description="Filter by class ID"),
    db: SupabaseDB = Depends(get_db_manager)
):
    """List attendance records with optional filters"""
    return db.list_presencas(
        data_inicio=data_inicio,
        data_fim=data_fim,
        turma_id=turma_id
    )


@router.get("/{presenca_id}", response_model=Dict[str, Any])
def get_presenca(
    presenca_id: int,
    db: SupabaseDB = Depends(get_db_manager)
):
    """Get an attendance record by ID"""
    presenca = db.get_presenca_by_id(presenca_id)
    if not presenca:
        raise HTTPException(
            status_code=404, detail="Attendance record not found"
        )
    return presenca


@router.post("/", response_model=Dict[str, Any])
def create_presenca(
    presenca: PresencaCreate,
    db: SupabaseDB = Depends(get_db_manager)
):
    """Register new attendance"""
    return db.create_presenca(
        aluno_id=presenca.aluno_id,
        turma_id=presenca.turma_id,
        confianca=presenca.confianca
    )


@router.put("/{presenca_id}/validate")
def validate_presenca(
    presenca_id: int,
    validation: PresencaValidate,
    db: SupabaseDB = Depends(get_db_manager)
):
    """Validate attendance by professor"""
    success = db.validate_presenca(
        presenca_id=presenca_id,
        professor_id=validation.professor_id,
        observacao=validation.observacao
    )
    if not success:
        raise HTTPException(
            status_code=404, detail="Attendance record not found"
        )
    return {"message": "Attendance validated successfully"}
