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
from PIL import Image

# Defina a tolerância de distância facial (quanto menor, mais rigoroso)
FACE_RECOGNITION_TOLERANCE = 0.55

# Tamanho padrão para preprocessamento de imagens (melhor performance)
TARGET_IMAGE_SIZE = (300, 300)


def preprocess_image(image_bytes: bytes) -> bytes:
    """
    Preprocessa a imagem redimensionando para 300x300px.
    Mantém a proporção e adiciona padding se necessário.
    
    Args:
        image_bytes: Bytes da imagem original
        
    Returns:
        Bytes da imagem processada em 300x300px
    """
    # Carregar imagem
    img = Image.open(io.BytesIO(image_bytes))
    
    # Converter para RGB se necessário (remove canal alpha)
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        mask = img.split()[-1] if img.mode in ('RGBA', 'LA') else None
        background.paste(img, mask=mask)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Calcular proporções mantendo aspect ratio
    width, height = img.size
    target_width, target_height = TARGET_IMAGE_SIZE
    
    # Calcular escala para fit
    scale = min(target_width / width, target_height / height)
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    # Redimensionar mantendo aspect ratio
    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Criar imagem final com padding centralizado
    final_img = Image.new('RGB', TARGET_IMAGE_SIZE, (255, 255, 255))
    paste_x = (target_width - new_width) // 2
    paste_y = (target_height - new_height) // 2
    final_img.paste(img, (paste_x, paste_y))
    
    # Converter de volta para bytes
    output = io.BytesIO()
    final_img.save(output, format='JPEG', quality=95)
    output.seek(0)
    
    return output.read()


def get_face_encoding(
    file: UploadFile,
    preprocess: bool = True
) -> Optional[np.ndarray]:
    """
    Carrega o arquivo de imagem, encontra um rosto e retorna seu
    encoding (vetor). Retorna None se nenhum rosto for detectado.
    
    Args:
        file: Arquivo de imagem enviado
        preprocess: Se True, redimensiona para 300x300px (padrão: True)
    
    Returns:
        np.ndarray com o encoding do rosto ou None
    """
    # 1. Ler o conteúdo do arquivo
    image_bytes = file.file.read()
    
    # 2. Preprocessar imagem se solicitado
    if preprocess:
        image_bytes = preprocess_image(image_bytes)

    # 3. Carregar a imagem a partir dos bytes
    image = face_recognition.load_image_file(io.BytesIO(image_bytes))

    # 4. Encontrar todos os encodings na imagem (pegamos apenas o primeiro)
    face_encodings = face_recognition.face_encodings(image)

    if face_encodings:
        return face_encodings[0]
    return None


def recognize_face(
    unknown_encoding: np.ndarray,
    known_faces_data: List[Dict[str, any]]
) -> Optional[Tuple[int, float]]:
    """
    Compara o encoding de um rosto desconhecido com todos os rostos
    conhecidos.

    Args:
        unknown_encoding: O vetor numpy do rosto a ser identificado.
        known_faces_data: Uma lista de dicionários, cada um com
                          'aluno_id' e 'embedding' (o vetor de rosto
                          salvo como bytes pickle).

    Returns:
        Uma tupla (aluno_id, confidence) do rosto mais próximo, ou None.
    """
    if not known_faces_data:
        return None

    # 1. Preparar os dados conhecidos para a comparação
    known_encodings = []
    known_ids = []
    
    import pickle
    import base64
    
    for face_record in known_faces_data:
        try:
            # Desserializar o embedding de bytes pickle para numpy array
            embedding_data = face_record['embedding']
            
            # Check if it's a hex-encoded string from Supabase BYTEA
            is_hex = (isinstance(embedding_data, str) and
                      embedding_data.startswith('\\x'))
            if is_hex:
                # Remove \x prefix and decode hex to get original base64
                hex_str = embedding_data.replace('\\x', '')
                embedding_bytes = bytes.fromhex(hex_str)
                # The result is the base64 string as bytes, decode to str
                embedding_b64_str = embedding_bytes.decode('utf-8')
                # Now decode base64 to get pickle bytes
                pickle_bytes = base64.b64decode(embedding_b64_str)
                # Finally unpickle to numpy array
                embedding_array = pickle.loads(pickle_bytes)
            elif isinstance(embedding_data, str):
                # Decode base64 string to bytes first
                embedding_bytes = base64.b64decode(embedding_data)
                # Then unpickle to numpy array
                embedding_array = pickle.loads(embedding_bytes)
            elif isinstance(embedding_data, bytes):
                # Direct pickle deserialização
                embedding_array = pickle.loads(embedding_data)
            elif isinstance(embedding_data, memoryview):
                # Se vier como memoryview, converter para bytes primeiro
                embedding_array = pickle.loads(bytes(embedding_data))
            else:
                # Fallback: tentar converter diretamente
                embedding_array = np.array(embedding_data)
            
            known_encodings.append(embedding_array)
            known_ids.append(face_record['aluno_id'])
            
        except Exception as e:
            # Ignora registros mal formatados, mas imprime erro para debug
            aluno_id = face_record.get('aluno_id')
            print(f"Erro ao processar embedding do aluno ID {aluno_id}: {e}")
            print(f"Tipo do embedding: {type(face_record.get('embedding'))}")
            continue

    if not known_encodings:
        return None
        
    # 2. Comparar o rosto desconhecido com todos os conhecidos
    # Retorna uma lista de distâncias. Quanto menor, mais parecido.
    face_distances = face_recognition.face_distance(
        known_encodings, unknown_encoding
    )

    # 3. Encontrar o rosto com a menor distância (mais parecido)
    best_match_index = np.argmin(face_distances)
    min_distance = face_distances[best_match_index]
    
    # 4. Verificar se a distância está dentro do limite de tolerância
    if min_distance <= FACE_RECOGNITION_TOLERANCE:
        # A similaridade é 1.0 - distância
        # Retornamos a similaridade (maior é melhor)
        matched_id = known_ids[best_match_index]
        confidence = 1.0 - min_distance  # Calcula a similaridade (0 a 1)
    
        # Retorna a similaridade em porcentagem (0 a 100)
        return matched_id, float(confidence * 100)
    
    # Nenhuma correspondência encontrada dentro da tolerância
    return None
