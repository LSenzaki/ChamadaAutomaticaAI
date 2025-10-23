"""
faces.py (Versão Estabilizada)
--------
Router responsável pelo reconhecimento facial e registro de chamada.
"""

from fastapi import APIRouter, UploadFile, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from app.services.face_service import get_face_encoding, compare_encodings
from app.models.db_session import get_db
from app.models.response import ResultadoReconhecimento, ResultadoSimilaridade
from app.models import db_models
from app.services.db_service import Database, Settings
import json
import numpy as np 
from typing import List

# Inicializa o Database Service (assumindo que já está definido)
settings = Settings.from_env()
db_manager = Database(settings)

# Definindo o limite de similaridade para considerar o rosto reconhecido
SIMILARITY_THRESHOLD = 70.0 # Exemplo: 70% de similaridade

router = APIRouter(prefix="/faces", tags=["faces"])


@router.post("/reconhecer", response_model=ResultadoReconhecimento)
async def reconhecer(
    foto: UploadFile, 
    session_tag: str = Form("Default Session"),
    db: Session = Depends(get_db) # <-- Usando a sessão
) -> ResultadoReconhecimento:
    """
    Reconhece o aluno em uma foto e registra a chamada se a confiança for alta.
    """
    encoding = get_face_encoding(foto)
    if encoding is None or (isinstance(encoding, np.ndarray) and encoding.size == 0):
        raise HTTPException(status_code=400, detail="Nenhum rosto detectado na imagem enviada")

    # 1. Carregar todos os embeddings do banco de dados (usando db_service)
    # db_manager.load_all_embeddings retorna objetos FaceEmbedding
    face_embeddings_data = db_manager.load_all_embeddings()
    
    if not face_embeddings_data:
        return ResultadoReconhecimento(
            mensagem="Nenhum rosto cadastrado para comparação",
            mais_provavel=None,
            todos=[]
        )

    # Dicionário para armazenar o MELHOR resultado de similaridade por aluno (ID)
    melhores_resultados_por_aluno = {}
    
    # 2. Comparar com todos os rostos cadastrados
    for face_data in face_embeddings_data:
        
        student = face_data.student
        if not student:
            continue 
        
        student_id = student.id
        
        # --- NOVO BLOCO TRY/EXCEPT ---
        try:
            # 1. Desserialização JSON e conversão para numpy array
            emb_list = json.loads(face_data.vector)
            emb = np.array(emb_list)
            
            # 2. Comparação (usando 'emb' que acabou de ser definido)
            sim = compare_encodings(emb, encoding) 
            
        except json.JSONDecodeError:
            # Se o vetor JSON estiver corrompido no DB, pulamos este embedding
            continue 
        except Exception as e:
            # Captura qualquer outro erro (como falha na conversão para np.array) e pula
            print(f"Erro inesperado ao processar embedding {face_data.id}: {e}")
            continue

        # Armazena apenas se for a maior similaridade encontrada para este aluno
        if student_id not in melhores_resultados_por_aluno or sim > melhores_resultados_por_aluno[student_id]['similaridade']:
            
            melhores_resultados_por_aluno[student_id] = {
                "id": student.id,
                "nome": student.nome,
                "similaridade": sim,
                "check_professor": student.is_professor
            }

    # 3. Converter o dicionário de melhores resultados para a lista ResultadoSimilaridade
    resultados: List[ResultadoSimilaridade] = [
        ResultadoSimilaridade(**data)
        for data in melhores_resultados_por_aluno.values()
    ]
    
    if not resultados:
        # Retorna erro claro se o loop não encontrou nenhum match válido (e todos foram pulados)
        return ResultadoReconhecimento(mensagem="Erro ao processar embeddings: Nenhuma correspondência válida encontrada após a comparação.", mais_provavel=None, todos=[])

    # 4. Encontrar o resultado mais provável
    resultados_ordenados = sorted(resultados, key=lambda x: x.similaridade, reverse=True)
    mais_provavel = resultados_ordenados[0]
    
    # 5. REGISTRAR A CHAMADA (Lógica Principal)
    if mais_provavel.similaridade >= SIMILARITY_THRESHOLD:
        
        registro = db_manager.create_attendance(
            student_id=mais_provavel.id,
            session_tag=session_tag,
            confidence=mais_provavel.similaridade
        )
        
        mais_provavel.mensagem_chamada = f"Chamada registrada ({registro.id}) às {registro.timestamp.strftime('%H:%M:%S')}"
        
        
    return ResultadoReconhecimento(
        mensagem="Reconhecimento concluído",
        mais_provavel=mais_provavel,
        todos=resultados_ordenados 
    )