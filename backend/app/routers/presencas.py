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
    """
    Busca todos os registros de presença do dia atual.
    Enriquece os dados com informações de aluno, turma e professor.
    
    Args:
        db: Gerenciador de banco de dados injetado
        
    Returns:
        Dict contendo data, lista de presenças e total de registros
    """
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
    """
    Lista registros de presença com filtros opcionais.
    
    Args:
        data_inicio: Data inicial para filtro (formato ISO)
        data_fim: Data final para filtro (formato ISO)
        turma_id: ID da turma para filtrar
        db: Gerenciador de banco de dados injetado
        
    Returns:
        Lista de registros de presença filtrados
    """
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
    """
    Busca um registro de presença específico pelo ID.
    
    Args:
        presenca_id: ID do registro de presença
        db: Gerenciador de banco de dados injetado
        
    Returns:
        Dados completos do registro de presença
        
    Raises:
        HTTPException: 404 se o registro não for encontrado
    """
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
    """
    Registra uma nova presença no sistema.
    
    Args:
        presenca: Dados da presença incluindo aluno_id, turma_id e confiança
        db: Gerenciador de banco de dados injetado
        
    Returns:
        Dados do registro de presença criado
    """
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
    """
    Valida uma presença através de confirmação do professor.
    
    Args:
        presenca_id: ID do registro de presença a ser validado
        validation: Dados de validação (professor_id e observação)
        db: Gerenciador de banco de dados injetado
        
    Returns:
        Mensagem de confirmação da validação
        
    Raises:
        HTTPException: 404 se o registro não for encontrado
    """
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
