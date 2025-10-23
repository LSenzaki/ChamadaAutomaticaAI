"""
faces.py (Versão Supabase Corrigida com Depends)
---------------------------------------------
Router responsável pelo reconhecimento facial e registro de chamada.
Utiliza injeção de dependência para o db_manager.
"""

from fastapi import APIRouter, UploadFile, HTTPException, Form, Depends # Adicionado Depends
from app.services.face_service import get_face_encoding, compare_encodings
# Alterado: Importamos a função de dependência e a classe SupabaseDB, NÃO a instância global db_manager
from app.services.db_service import get_db_manager, SupabaseDB 
from app.config import settings
from app.models.response import ResultadoReconhecimento, ResultadoSimilaridade # Se você ainda usa Pydantic
import json
import numpy as np 
from typing import List

# Configurações globais
SIMILARITY_THRESHOLD = settings.SIMILARITY_THRESHOLD

router = APIRouter(prefix="/faces", tags=["faces"])


@router.post("/reconhecer") # Removido response_model para simplificar o retorno JSON do Supabase
async def reconhecer(
    foto: UploadFile, 
    session_tag: str = Form("Default Session"),
    db_manager: SupabaseDB = Depends(get_db_manager) # NOVO: Injeção de dependência
):
    """
    Reconhece o aluno em uma foto e registra a chamada se a confiança for alta.
    """
    encoding = get_face_encoding(foto)
    if encoding is None or (isinstance(encoding, np.ndarray) and encoding.size == 0):
        raise HTTPException(status_code=400, detail="Nenhum rosto detectado na imagem enviada")

    # 1. Carregar todos os embeddings do Supabase (JSON + nome do aluno)
    face_embeddings_data = db_manager.load_all_embeddings()
    
    if not face_embeddings_data:
        return {"mensagem": "Nenhum rosto cadastrado para comparação", "mais_provavel": None}

    melhores_resultados_por_aluno = {}
    
    # 2. Comparar com todos os rostos cadastrados
    for face_data in face_embeddings_data:
        
        student_data = face_data.get('students')
        if not student_data:
            continue # Pular se não houver dados do aluno (problema de RLS ou FK)
        
        student_id = face_data['student_id']
        
        # Desserialização JSON: Transforma a string/JSONB de volta em numpy array
        try:
            # Assumimos que o campo 'vector' é uma string JSON válida
            emb_list = json.loads(face_data['vector'])
            emb = np.array(emb_list)
        except Exception:
            continue 
        
        sim = compare_encodings(emb, encoding)
        
        # Armazena apenas se for a maior similaridade encontrada para este aluno
        if student_id not in melhores_resultados_por_aluno or sim > melhores_resultados_por_aluno[student_id]['similaridade']:
            
            melhores_resultados_por_aluno[student_id] = {
                "id": student_id,
                "nome": student_data['nome'],
                "similaridade": sim,
                "check_professor": student_data['is_professor']
            }

    # 3. Encontrar o resultado mais provável
    resultados = list(melhores_resultados_por_aluno.values())
    
    if not resultados:
        return {"mensagem": "Nenhuma correspondência válida encontrada após a comparação.", "mais_provavel": None}

    resultados_ordenados = sorted(resultados, key=lambda x: x['similaridade'], reverse=True)
    mais_provavel = resultados_ordenados[0]
    
    # 4. REGISTRAR A CHAMADA
    mensagem_chamada = "Nenhuma chamada registrada (similaridade abaixo do limiar)."
    
    if mais_provavel['similaridade'] >= SIMILARITY_THRESHOLD:
        
        registro = db_manager.create_attendance(
            student_id=mais_provavel['id'],
            session_tag=session_tag,
            confidence=mais_provavel['similaridade']
        )
        
        if registro:
             mensagem_chamada = f"Chamada registrada ({registro['id']}) em {registro['timestamp']}."
        
        
    return {
        "mensagem": "Reconhecimento concluído",
        "mais_provavel": mais_provavel,
        "mensagem_chamada": mensagem_chamada,
        "todos": resultados_ordenados 
    }
