"""
app/routers/faces.py
--------------------
Rotas para reconhecimento facial e registro de chamada.
Agora usando sistema híbrido (face_recognition + DeepFace).
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Query
from app.services.db_service import get_db_manager, SupabaseDB
from app.services.face_service import get_face_encoding, recognize_face
from app.services.hybrid_face_service import recognize_face_hybrid
from typing import Optional, Dict, Any
import numpy as np

router = APIRouter(prefix="/faces", tags=["Faces"])

# Dependência do SupabaseDB
SupabaseDep = Depends(get_db_manager)

@router.post("/reconhecer", status_code=status.HTTP_200_OK)
async def validate_face(
    foto: UploadFile = File(...),
    mode: str = Query(default="smart", description="Modo: smart, always_both, ou fallback"),
    db_manager: SupabaseDB = SupabaseDep
):
    """
    Recebe uma imagem de rosto, realiza o reconhecimento facial usando estratégia híbrida
    (face_recognition + DeepFace) e registra a chamada se o rosto for identificado.
    
    Modos disponíveis:
    - smart: Usa face_recognition primeiro, valida com DeepFace se necessário (RECOMENDADO)
    - always_both: Sempre executa ambos os modelos para máxima precisão
    - fallback: Só usa DeepFace se face_recognition falhar
    """
    # 1. Recuperar todos os rostos conhecidos do Supabase
    try:
        known_faces = db_manager.get_all_faces()
        if not known_faces:
            return {
                "status": "failure", 
                "detail": "Nenhum rosto cadastrado no banco de dados."
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao recuperar faces do banco de dados: {e}"
        )

    # 2. Reconhecer o rosto usando estratégia híbrida
    try:
        hybrid_result = recognize_face_hybrid(foto, known_faces, mode=mode)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Falha ao processar a imagem: {e}"
        )

    # 3. Verificar se houve match
    if hybrid_result.aluno_id and hybrid_result.confidence is not None:
        aluno_id = hybrid_result.aluno_id
        confidence = hybrid_result.confidence
        
        # 4. Buscar informações do aluno
        aluno_record = db_manager.get_aluno_by_id(aluno_id)
        
        if not aluno_record:
            return {
                "status": "failure",
                "message": "Rosto reconhecido, mas aluno não encontrado no registro principal.",
                "recognition_details": hybrid_result.to_dict()
            }

        aluno_nome = aluno_record.get('nome', 'Nome Desconhecido')

        # 5. Registrar a chamada
        try:
            attendance_data = {
                "aluno_id": aluno_id,
                "confidence": round(confidence, 4),
            }
            db_manager.register_attendance(attendance_data)
            
            # Sucesso
            return {
                "status": "success",
                "message": f"Chamada registrada para {aluno_nome}!",
                "aluno_id": aluno_id,
                "nome": aluno_nome,
                "confidence": round(confidence, 2),
                "recognition_details": hybrid_result.to_dict()
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Rosto reconhecido ({aluno_nome}), mas falha ao registrar chamada: {e}"
            )
    else:
        # Nenhuma correspondência
        return {
            "status": "failure",
            "message": "Rosto não reconhecido ou fora da tolerância.",
            "recognition_details": hybrid_result.to_dict()
        }


@router.post("/reconhecer/teste", status_code=status.HTTP_200_OK)
async def test_recognition(
    foto: UploadFile = File(...),
    db_manager: SupabaseDB = SupabaseDep
):
    """
    Endpoint de teste que executa reconhecimento com TODOS os métodos
    e retorna comparação detalhada. Não registra chamada.
    
    Útil para avaliar qual estratégia funciona melhor.
    """
    try:
        known_faces = db_manager.get_all_faces()
        if not known_faces:
            return {
                "status": "failure", 
                "detail": "Nenhum rosto cadastrado no banco de dados."
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao recuperar faces do banco de dados: {e}"
        )

    results = {}
    
    # Testar cada modo
    for mode in ["smart", "always_both", "fallback"]:
        try:
            foto.file.seek(0)  # Reset file pointer
            result = recognize_face_hybrid(foto, known_faces, mode=mode)
            results[mode] = result.to_dict()
        except Exception as e:
            results[mode] = {"error": str(e)}
    
    # Adicionar informações do estudante se encontrado
    for mode, result_data in results.items():
        if result_data.get("aluno_id"):
            aluno = db_manager.get_aluno_by_id(result_data["aluno_id"])
            if aluno:
                result_data["aluno_nome"] = aluno.get("nome", "Desconhecido")
    
    return {
        "status": "success",
        "message": "Teste de reconhecimento concluído",
        "results": results,
        "recommendation": _get_best_mode_recommendation(results)
    }


def _get_best_mode_recommendation(results: Dict) -> str:
    """Analisa resultados e recomenda melhor modo"""
    smart = results.get("smart", {})
    both = results.get("always_both", {})
    
    if smart.get("agreement") is True:
        return "SMART mode recomendado - ambos modelos concordam com alta confiança"
    elif both.get("agreement") is True:
        return "ALWAYS_BOTH recomendado - precisa validação máxima"
    elif smart.get("processing_time", 999) < both.get("processing_time", 999):
        return "SMART mode recomendado - melhor custo-benefício velocidade/precisão"
    else:
        return "Avaliar caso a caso - resultados inconclusivos"
