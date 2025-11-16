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


@router.get("/hoje")
def get_presencas_hoje(
    db: SupabaseDB = Depends(get_db_manager)
):
    """Get all attendance records for today"""
    from datetime import date
    today = date.today().isoformat()
    
    response = db.client.table('presencas').select(
        '*, alunos(id, nome), turmas(id, nome)'
    ).gte('data_hora', today).order('data_hora', desc=False).execute()
    
    presencas = response.data if response.data else []
    
    # Enrich presencas with professor information
    for presenca in presencas:
        turma_id = presenca.get('turma_id')
        if turma_id:
            # Get professors assigned to this turma
            prof_response = db.client.table('turmas_professores').select(
                'professores(id, nome)'
            ).eq('turma_id', turma_id).execute()
            
            if prof_response.data and len(prof_response.data) > 0:
                # Get the first professor assigned (or could return all)
                professor_data = prof_response.data[0].get('professores', {})
                presenca['professor_nome'] = professor_data.get('nome', 'Não atribuído')
                presenca['professor_id'] = professor_data.get('id')
            else:
                presenca['professor_nome'] = 'Não atribuído'
                presenca['professor_id'] = None
        else:
            presenca['professor_nome'] = 'Não atribuído'
            presenca['professor_id'] = None
    
    return {
        "data": today,
        "presencas": presencas,
        "total_registros": len(presencas)
    }


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
