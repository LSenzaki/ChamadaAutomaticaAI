"""
app/services/face_service.py
----------------------------
Serviços para processamento de imagens e reconhecimento facial.
Depende das bibliotecas numpy, io e face_recognition.
"""
import numpy as np
import face_recognition
from fastapi import UploadFile
from typing import Optional, List, Dict, Tuple
import io

# Defina a tolerância de distância facial (quanto menor, mais rigoroso)
FACE_RECOGNITION_TOLERANCE = 0.6

def get_face_encoding(file: UploadFile) -> Optional[np.ndarray]:
    """
    Carrega o arquivo de imagem, encontra um rosto e retorna seu encoding (vetor).
    Retorna None se nenhum rosto for detectado.
    """
    # 1. Ler o conteúdo do arquivo
    image_bytes = file.file.read()

    # 2. Carregar a imagem a partir dos bytes
    image = face_recognition.load_image_file(io.BytesIO(image_bytes))

    # 3. Encontrar todos os encodings na imagem (pegamos apenas o primeiro)
    face_encodings = face_recognition.face_encodings(image)

    if face_encodings:
        return face_encodings[0]
    return None

def recognize_face(
    unknown_encoding: np.ndarray, 
    known_faces_data: List[Dict[str, any]]
) -> Optional[Tuple[int, float]]:
    """
    Compara o encoding de um rosto desconhecido com todos os rostos conhecidos.

    Args:
        unknown_encoding: O vetor numpy do rosto a ser identificado.
        known_faces_data: Uma lista de dicionários, cada um com 'aluno_id' e 'embedding'
                          (o vetor de rosto salvo como bytes pickle).

    Returns:
        Uma tupla (aluno_id, confidence) do rosto mais próximo, ou None.
    """
    if not known_faces_data:
        return None

    # 1. Preparar os dados conhecidos para a comparação
    known_encodings = []
    known_ids = []
    
    import pickle
    
    for face_record in known_faces_data:
        try:
            # Desserializar o embedding de bytes pickle para numpy array
            embedding_bytes = face_record['embedding']
            if isinstance(embedding_bytes, bytes):
                # Pickle deserialização
                embedding_array = pickle.loads(embedding_bytes)
            elif isinstance(embedding_bytes, memoryview):
                # Se vier como memoryview, converter para bytes primeiro
                embedding_array = pickle.loads(bytes(embedding_bytes))
            else:
                # Fallback: tentar converter diretamente
                embedding_array = np.array(embedding_bytes)
            
            known_encodings.append(embedding_array)
            known_ids.append(face_record['aluno_id'])
            
        except Exception as e:
            # Ignora registros mal formatados, mas imprime o erro para debug
            print(f"Erro ao processar embedding do aluno ID {face_record.get('aluno_id')}: {e}")
            continue

    if not known_encodings:
        return None
        
    # 2. Comparar o rosto desconhecido com todos os conhecidos
    # Retorna uma lista de distâncias. Quanto menor, mais parecido.
    face_distances = face_recognition.face_distance(known_encodings, unknown_encoding)

    # 3. Encontrar o rosto com a menor distância (mais parecido)
    best_match_index = np.argmin(face_distances)
    min_distance = face_distances[best_match_index]
    
   
    # 4. Verificar se a distância está dentro do limite de tolerância
    if min_distance <= FACE_RECOGNITION_TOLERANCE:
        # A similaridade é 1.0 - distância. Retornamos a similaridade (maior é melhor).
        matched_id = known_ids[best_match_index]
        confidence = 1.0 - min_distance # Calcula a similaridade (0 a 1)
    
        # Retorna a similaridade em porcentagem (0 a 100)
        return matched_id, float(confidence * 100) 
    
    return None # Nenhuma correspondência encontrada dentro da tolerância