"""
app/routers/faces.py
--------------------
Rotas para reconhecimento facial e registro de chamada.
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from app.services.db_service import get_db_manager, SupabaseDB
from app.services.face_service import get_face_encoding, recognize_face
from typing import Optional, Dict, Any
import numpy as np

router = APIRouter(prefix="/faces", tags=["Faces"])

# Dependência do SupabaseDB
SupabaseDep = Depends(get_db_manager)

@router.post("/reconhecer", status_code=status.HTTP_200_OK)
async def validate_face(
    foto: UploadFile = File(...),
    db_manager: SupabaseDB = SupabaseDep
):
    """
    Recebe uma imagem de rosto, realiza o reconhecimento facial
    e registra a chamada se o rosto for identificado, retornando o nome.
    """
    # 1. Gerar o encoding do rosto da imagem recebida
    try:
        encoding = get_face_encoding(foto)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Falha ao processar a imagem: {e}"
        )

    if encoding is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhum rosto detectado na imagem."
        )

    # 2. Recuperar todos os rostos conhecidos (embeddings) do Supabase
    try:
        known_faces = db_manager.get_all_faces()
        if not known_faces:
            return {"status": "failure", "detail": "Nenhum rosto cadastrado no banco de dados."}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao recuperar faces do banco de dados: {e}"
        )

    # 3. Reconhecer o rosto (comparação de vetores)
    match_result = recognize_face(encoding, known_faces)

    if match_result:
        student_id, confidence = match_result
        
        # 4. BUSCAR O NOME DO ALUNO
        student_record = db_manager.get_student_by_id(student_id)
        
        if not student_record:
            # Rosto encontrado, mas registro do aluno não (erro de integridade)
            return {
                "status": "failure",
                "message": "Rosto reconhecido, mas aluno não encontrado no registro principal."
            }

        student_name = student_record.get('nome', 'Nome Desconhecido') # Usa 'name' ou 'nome' conforme sua DB

        # 5. Registrar a chamada (Attendance)
        try:
            attendance_data = {
                "student_id": student_id,
                "confidence": round(confidence, 4),
            }
            db_manager.register_attendance(attendance_data)
            
            # Sucesso
            return {
                "status": "success",
                "message": f"Chamada registrada para {student_name}!",
                "student_id": student_id,
                "nome": student_name, # Retornando o nome
                "confidence": confidence
            }

        except Exception as e:
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Rosto reconhecido ({student_name}), mas falha ao registrar chamada: {e}"
            )
    else:
        # Nenhuma correspondência dentro da tolerância
        return {
            "status": "failure",
            "message": "Rosto não reconhecido ou fora da tolerância."
        }