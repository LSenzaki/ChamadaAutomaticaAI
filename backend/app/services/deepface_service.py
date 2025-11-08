"""
app/services/deepface_service.py
---------------------------------
Serviços para reconhecimento facial usando DeepFace.
Oferece múltiplos modelos e backends para comparação.
"""
import numpy as np
from fastapi import UploadFile
from typing import Optional, List, Dict, Tuple
import io
from PIL import Image
from deepface import DeepFace
import json
import tempfile
import os

# Configurações do DeepFace
DEEPFACE_MODEL = "Facenet512"  # Opções: VGG-Face, Facenet, Facenet512, OpenFace, DeepFace, DeepID, ArcFace, Dlib, SFace
DEEPFACE_DETECTOR = "opencv"   # Opções: opencv, ssd, dlib, mtcnn, retinaface, mediapipe
DEEPFACE_DISTANCE_METRIC = "cosine"  # Opções: cosine, euclidean, euclidean_l2

# Thresholds para diferentes modelos (valores padrão do DeepFace)
DEEPFACE_THRESHOLDS = {
    "VGG-Face": {"cosine": 0.40, "euclidean": 0.60, "euclidean_l2": 0.86},
    "Facenet": {"cosine": 0.40, "euclidean": 10, "euclidean_l2": 0.80},
    "Facenet512": {"cosine": 0.30, "euclidean": 23.56, "euclidean_l2": 1.04},
    "ArcFace": {"cosine": 0.68, "euclidean": 4.15, "euclidean_l2": 1.13},
    "Dlib": {"cosine": 0.07, "euclidean": 0.6, "euclidean_l2": 0.4},
    "SFace": {"cosine": 0.593, "euclidean": 10.734, "euclidean_l2": 1.055},
    "OpenFace": {"cosine": 0.10, "euclidean": 0.55, "euclidean_l2": 0.55},
    "DeepFace": {"cosine": 0.23, "euclidean": 64, "euclidean_l2": 0.64},
    "DeepID": {"cosine": 0.015, "euclidean": 45, "euclidean_l2": 0.17}
}

def get_deepface_encoding(
    file: UploadFile, 
    model_name: str = DEEPFACE_MODEL,
    detector_backend: str = DEEPFACE_DETECTOR
) -> Optional[np.ndarray]:
    """
    Extrai o embedding facial usando DeepFace.
    
    Args:
        file: Arquivo de imagem enviado
        model_name: Modelo de reconhecimento facial a ser usado
        detector_backend: Backend de detecção de faces
    
    Returns:
        Array numpy com o embedding ou None se nenhum rosto for detectado
    """
    try:
        # Ler bytes da imagem
        image_bytes = file.file.read()
        
        # Converter para PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Salvar temporariamente (DeepFace trabalha melhor com arquivos)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            image.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            # Extrair embedding
            embedding_objs = DeepFace.represent(
                img_path=tmp_path,
                model_name=model_name,
                detector_backend=detector_backend,
                enforce_detection=True
            )
            
            # DeepFace.represent retorna uma lista de dicionários
            # Pegamos o primeiro rosto detectado
            if embedding_objs and len(embedding_objs) > 0:
                embedding = np.array(embedding_objs[0]["embedding"])
                return embedding
            
        finally:
            # Limpar arquivo temporário
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
        return None
        
    except Exception as e:
        print(f"Erro ao extrair embedding com DeepFace: {e}")
        return None

def calculate_distance(embedding1: np.ndarray, embedding2: np.ndarray, metric: str = DEEPFACE_DISTANCE_METRIC) -> float:
    """
    Calcula a distância entre dois embeddings usando a métrica especificada.
    
    Args:
        embedding1: Primeiro embedding
        embedding2: Segundo embedding
        metric: Métrica de distância (cosine, euclidean, euclidean_l2)
    
    Returns:
        Distância calculada
    """
    if metric == "cosine":
        # Distância cosseno
        from sklearn.metrics.pairwise import cosine_distances
        return float(cosine_distances([embedding1], [embedding2])[0][0])
    
    elif metric == "euclidean":
        # Distância euclidiana
        return float(np.linalg.norm(embedding1 - embedding2))
    
    elif metric == "euclidean_l2":
        # Distância euclidiana L2 normalizada
        return float(np.linalg.norm(
            embedding1 / np.linalg.norm(embedding1) - 
            embedding2 / np.linalg.norm(embedding2)
        ))
    
    else:
        raise ValueError(f"Métrica desconhecida: {metric}")

def recognize_face_deepface(
    unknown_encoding: np.ndarray, 
    known_faces_data: List[Dict[str, any]],
    model_name: str = DEEPFACE_MODEL,
    distance_metric: str = DEEPFACE_DISTANCE_METRIC
) -> Optional[Tuple[str, float, float]]:
    """
    Compara o embedding de um rosto desconhecido com todos os rostos conhecidos usando DeepFace.
    
    Args:
        unknown_encoding: O embedding do rosto a ser identificado
        known_faces_data: Lista de dicionários com 'student_id' e 'vector'
        model_name: Modelo usado (para determinar threshold)
        distance_metric: Métrica de distância
    
    Returns:
        Tupla (student_id, confidence, distance) do melhor match, ou None
    """
    if not known_faces_data:
        return None
    
    # Preparar embeddings conhecidos
    known_encodings = []
    known_ids = []
    
    for face_record in known_faces_data:
        try:
            vector_list = face_record['vector']
            if isinstance(vector_list, str):
                import json
                vector_list = json.loads(vector_list)
            
            known_encodings.append(np.array(vector_list))
            known_ids.append(face_record['student_id'])
            
        except Exception as e:
            print(f"Erro ao processar vetor facial do ID {face_record.get('student_id')}: {e}")
            continue
    
    if not known_encodings:
        return None
    
    # Calcular distâncias
    distances = [calculate_distance(unknown_encoding, known_enc, distance_metric) 
                 for known_enc in known_encodings]
    
    # Encontrar o melhor match
    best_match_index = np.argmin(distances)
    min_distance = distances[best_match_index]
    
    # Obter threshold apropriado
    threshold = DEEPFACE_THRESHOLDS.get(model_name, {}).get(distance_metric, 0.4)
    
    # Verificar se está dentro do threshold
    if min_distance <= threshold:
        matched_id = known_ids[best_match_index]
        
        # Calcular confiança (inverso da distância normalizado)
        # Para distância cosseno: confidence = (1 - distance) * 100
        if distance_metric == "cosine":
            confidence = (1 - min_distance) * 100
        else:
            # Para euclidiana, normalizar baseado no threshold
            confidence = max(0, (1 - min_distance / threshold) * 100)
        
        return matched_id, float(confidence), float(min_distance)
    
    return None

def verify_faces_deepface(
    img1_path: str,
    img2_path: str,
    model_name: str = DEEPFACE_MODEL,
    detector_backend: str = DEEPFACE_DETECTOR,
    distance_metric: str = DEEPFACE_DISTANCE_METRIC
) -> Dict:
    """
    Verifica se duas imagens contêm a mesma pessoa usando DeepFace.verify.
    
    Args:
        img1_path: Caminho para primeira imagem
        img2_path: Caminho para segunda imagem
        model_name: Modelo de reconhecimento facial
        detector_backend: Backend de detecção
        distance_metric: Métrica de distância
    
    Returns:
        Dicionário com resultado da verificação
    """
    try:
        result = DeepFace.verify(
            img1_path=img1_path,
            img2_path=img2_path,
            model_name=model_name,
            detector_backend=detector_backend,
            distance_metric=distance_metric,
            enforce_detection=True
        )
        return result
    except Exception as e:
        print(f"Erro na verificação DeepFace: {e}")
        return {"verified": False, "error": str(e)}
