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
) -> Optional[Tuple[str, float]]:
    """
    Compara o encoding de um rosto desconhecido com todos os rostos conhecidos.

    Args:
        unknown_encoding: O vetor numpy do rosto a ser identificado.
        known_faces_data: Uma lista de dicionários, cada um com 'student_id' e 'vector'
                          (o vetor de rosto salvo como string JSON, que precisamos converter).

    Returns:
        Uma tupla (student_id, confidence) do rosto mais próximo, ou None.
    """
    if not known_faces_data:
        return None

    # 1. Preparar os dados conhecidos para a comparação
    known_encodings = []
    known_ids = []
    
    for face_record in known_faces_data:
        try:
            # Converte a string JSON (que é uma lista Python) de volta para um array numpy
            # O .tolist() foi usado na rota de cadastro
            vector_list = face_record['vector']
            if isinstance(vector_list, str):
                # Se o Supabase não converter automaticamente, tentamos o json.loads
                import json
                vector_list = json.loads(vector_list)
            
            # Converte a lista de volta para um array numpy
            known_encodings.append(np.array(vector_list))
            known_ids.append(face_record['student_id'])
            
        except Exception as e:
            # Ignora registros mal formatados, mas imprime o erro para debug
            print(f"Erro ao processar vetor facial do ID {face_record.get('student_id')}: {e}")
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
        # A "confiança" é a inversa da distância (1.0 - distance), mas para fins práticos,
        # vamos retornar a distância real (menor é melhor) e o ID.
        matched_id = known_ids[best_match_index]
        return matched_id, float(min_distance)
    
    return None # Nenhuma correspondência encontrada dentro da tolerância