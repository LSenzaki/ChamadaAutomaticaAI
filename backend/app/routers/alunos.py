"""
app/routers/alunos.py
---------------------
API endpoints for managing students (alunos) with face recognition.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from app.services.db_service import get_db_manager, SupabaseDB
from app.services.face_service import get_face_encoding
from app.services.hybrid_face_service import recognize_face_hybrid
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import pickle
import base64


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


# ============================================================
# FACE RECOGNITION ENDPOINTS
# ============================================================

@router.post("/cadastrar")
async def cadastrar_com_foto(
    nome: str = Form(...),
    fotos: List[UploadFile] = File(...),
    turma_id: Optional[int] = Form(None),
    db: SupabaseDB = Depends(get_db_manager)
):
    """
    Register a new student with face photos.
    
    Supports multiple photos for better recognition accuracy.
    
    Parameters:
    - nome: Student name
    - fotos: One or more face photos
    - turma_id: Optional class ID
    - db: Database manager (injected)
    
    Returns:
    - Success message with student ID and photo count
    """
    if not fotos or len(fotos) == 0:
        raise HTTPException(status_code=400, detail="At least one photo is required")
    
    # Convert turma_id=0 to None (0 is not a valid foreign key)
    if turma_id == 0:
        turma_id = None
    
    # Create student
    aluno_data = db.create_aluno(
        nome=nome,
        turma_id=turma_id,
        check_professor=False
    )
    aluno_id = aluno_data['id']
    
    # Process each photo and save embeddings
    successful_embeddings = 0
    failed_photos = []
    
    for idx, foto in enumerate(fotos):
        try:
            # Extract face encoding
            encoding = get_face_encoding(foto)
            if encoding is None:
                failed_photos.append(f"{foto.filename or f'photo_{idx+1}'} (no face detected)")
                continue
            
            # DEBUG: Check what we're getting
            print(f"DEBUG: encoding type: {type(encoding)}, shape: {encoding.shape if hasattr(encoding, 'shape') else 'N/A'}")
            
            # Convert to base64 for storage
            embedding_bytes = pickle.dumps(encoding)
            print(f"DEBUG: pickled bytes length: {len(embedding_bytes)}")
            embedding_b64 = base64.b64encode(embedding_bytes).decode('utf-8')
            print(f"DEBUG: base64 string length: {len(embedding_b64)}, sample: {embedding_b64[:50]}...")
            
            # Save to database
            db.add_embedding(
                aluno_id=aluno_id,
                embedding_data=embedding_b64,
                foto_nome=foto.filename or f"photo_{idx+1}.jpg"
            )
            successful_embeddings += 1
            
        except Exception as e:
            failed_photos.append(f"{foto.filename or f'photo_{idx+1}'} (error: {str(e)})")
    
    # Build response
    response = {
        "mensagem": f"{nome} cadastrado com sucesso!",
        "id": aluno_id,
        "fotos_processadas": successful_embeddings,
        "total_fotos": len(fotos)
    }
    
    if failed_photos:
        response["fotos_com_erro"] = failed_photos
    
    if successful_embeddings == 0:
        # Rollback: delete student if no photos were processed
        db.delete_aluno(aluno_id)
        raise HTTPException(
            status_code=400,
            detail=f"No faces detected in any photo. Errors: {', '.join(failed_photos)}"
        )
    
    return response


@router.post("/reconhecer")
async def reconhecer_rosto(
    foto: UploadFile = File(...),
    db: SupabaseDB = Depends(get_db_manager)
):
    """
    Recognize a face and register attendance.
    
    Uses hybrid recognition (face_recognition + DeepFace) for better accuracy.
    
    Parameters:
    - foto: Face photo to recognize
    - db: Database manager (injected)
    
    Returns:
    - Recognition result with student info and attendance ID
    """
    # Get all registered faces
    known_faces = db.get_all_faces()
    
    if not known_faces:
        raise HTTPException(
            status_code=404,
            detail="No registered students found"
        )
    
    # Perform hybrid recognition
    result = recognize_face_hybrid(foto, known_faces, mode="smart")
    
    if not result.aluno_id:
        return {
            "reconhecido": False,
            "mensagem": "Face not recognized",
            "confianca": result.confidence,
            "metodo": result.method_used,
            "tempo_processamento": result.processing_time
        }
    
    # Get student info
    aluno = db.get_aluno_by_id(result.aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Student not found in database")
    
    # Check if student is validated
    if not aluno.get('check_professor'):
        return {
            "reconhecido": True,
            "aluno_id": result.aluno_id,
            "aluno_nome": aluno['nome'],
            "confianca": result.confidence,
            "metodo": result.method_used,
            "mensagem": "Student pending professor validation",
            "presenca_registrada": False
        }
    
    # Check if student is currently in class (for entry/exit logic)
    # Register attendance
    turma_id = aluno.get('turma_id')
    presenca = db.create_presenca(
        aluno_id=result.aluno_id,
        turma_id=turma_id if turma_id else 0,
        confianca=result.confidence if result.confidence else 0.0
    )
    
    return {
        "reconhecido": True,
        "aluno_id": result.aluno_id,
        "aluno_nome": aluno['nome'],
        "turma_id": turma_id,
        "confianca": result.confidence,
        "metodo": result.method_used,
        "tempo_processamento": result.processing_time,
        "presenca_registrada": True,
        "presenca_id": presenca['id'],
        "data_hora": presenca['data_hora'],
        "mensagem": "Presença registrada com sucesso"
    }


@router.post("/reconhecer/teste")
async def testar_reconhecimento(
    foto: UploadFile = File(...),
    db: SupabaseDB = Depends(get_db_manager)
):
    """
    Test face recognition without registering attendance.
    
    Useful for testing and validation.
    
    Parameters:
    - foto: Face photo to test
    - db: Database manager (injected)
    
    Returns:
    - Recognition result without attendance registration
    """
    # Get all registered faces
    known_faces = db.get_all_faces()
    
    if not known_faces:
        raise HTTPException(
            status_code=404,
            detail="No registered students found"
        )
    
    # Perform hybrid recognition
    result = recognize_face_hybrid(foto, known_faces, mode="smart")
    
    if not result.aluno_id:
        return {
            "reconhecido": False,
            "mensagem": "Face not recognized",
            "confianca": result.confidence,
            "metodo": result.method_used,
            "tempo_processamento": result.processing_time,
            "detalhes": result.to_dict()
        }
    
    # Get student info
    aluno = db.get_aluno_by_id(result.aluno_id)
    
    return {
        "reconhecido": True,
        "aluno_id": result.aluno_id,
        "aluno_nome": aluno['nome'] if aluno else "Unknown",
        "turma_id": aluno.get('turma_id') if aluno else None,
        "confianca": result.confidence,
        "metodo": result.method_used,
        "tempo_processamento": result.processing_time,
        "check_professor": aluno.get('check_professor') if aluno else False,
        "detalhes": result.to_dict()
    }


@router.post("/saida/{aluno_id}")
def registrar_saida(
    aluno_id: int,
    db: SupabaseDB = Depends(get_db_manager)
):
    """
    Explicitly register student exit/departure.
    
    Parameters:
    - aluno_id: Student ID
    - db: Database manager (injected)
    
    Returns:
    - Exit registration confirmation
    """
    # Get student info
    aluno = db.get_aluno_by_id(aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check if student is currently in class
    if not db.is_student_in_class(aluno_id):
        raise HTTPException(
            status_code=400,
            detail="Student has no active entry for today"
        )
    
    # Register exit
    turma_id = aluno.get('turma_id')
    presenca = db.create_presenca(
        aluno_id=aluno_id,
        turma_id=turma_id if turma_id else 0,
        confianca=None
    )
    
    return {
        "mensagem": "Saída registrada com sucesso",
        "aluno_id": aluno_id,
        "aluno_nome": aluno['nome'],
        "presenca_id": presenca['id'],
        "data_hora": presenca['data_hora']
    }


@router.get("/{aluno_id}/presencas/hoje")
def get_presencas_hoje(
    aluno_id: int,
    db: SupabaseDB = Depends(get_db_manager)
):
    """
    Get all attendance records for a student today.
    
    Shows entry and exit times for the current day.
    
    Parameters:
    - aluno_id: Student ID
    - db: Database manager (injected)
    
    Returns:
    - List of today's attendance records
    """
    from datetime import date
    today = date.today().isoformat()
    
    # Get student info
    aluno = db.get_aluno_by_id(aluno_id)
    if not aluno:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get today's attendance records
    response = db.client.table('presencas').select(
        '*'
    ).eq('aluno_id', aluno_id).gte(
        'data_hora', today
    ).order('data_hora', desc=False).execute()
    
    presencas = response.data if response.data else []
    
    # Calculate if student is currently in class
    is_in_class = db.is_student_in_class(aluno_id)
    
    return {
        "aluno_id": aluno_id,
        "aluno_nome": aluno['nome'],
        "data": today,
        "esta_em_aula": is_in_class,
        "presencas": presencas
    }


@router.delete("/{aluno_id}/embeddings")
def delete_aluno_embeddings(
    aluno_id: int,
    db: SupabaseDB = Depends(get_db_manager)
):
    """
    Delete all face embeddings for a specific student.
    
    Useful for removing corrupted embeddings before re-registering.
    
    Parameters:
    - aluno_id: Student ID
    - db: Database manager (injected)
    
    Returns:
    - Deletion confirmation
    """
    try:
        # Delete embeddings for this student
        result = db.client.table('face_embeddings').delete().eq(
            'aluno_id', aluno_id
        ).execute()
        
        count = len(result.data) if result.data else 0
        
        return {
            "mensagem": f"Embeddings deletados para aluno {aluno_id}",
            "quantidade": count,
            "aluno_id": aluno_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao deletar embeddings: {str(e)}"
        )
