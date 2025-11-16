"""
app/services/hybrid_face_service.py
------------------------------------
Serviço híbrido de reconhecimento facial que combina face_recognition e DeepFace
para obter a melhor combinação de velocidade e precisão.

Estratégia:
1. Usa face_recognition primeiro (rápido)
2. Se confiança alta: aceita resultado
3. Se confiança média/baixa: valida com DeepFace
4. Se não encontrar: tenta DeepFace como fallback
"""
import numpy as np
from fastapi import UploadFile
from typing import Optional, List, Dict, Tuple, Any
import io
from app.services.face_service import get_face_encoding, recognize_face
from app.services.deepface_service import get_deepface_encoding, recognize_face_deepface
import time

# Thresholds de confiança para a estratégia híbrida
HIGH_CONFIDENCE_THRESHOLD = 55.0  # Acima disto, aceita face_recognition diretamente
LOW_CONFIDENCE_THRESHOLD = 35.0   # Abaixo disto, usa apenas DeepFace

# Modo de operação
HYBRID_MODE = "smart"  # Opções: "smart", "always_both", "fallback"

class HybridRecognitionResult:
    """Classe para armazenar resultado do reconhecimento híbrido"""
    def __init__(
        self,
        aluno_id: Optional[int] = None,
        confidence: Optional[float] = None,
        method_used: Optional[str] = None,
        fr_result: Optional[Tuple] = None,
        df_result: Optional[Tuple] = None,
        processing_time: float = 0.0,
        agreement: Optional[bool] = None
    ):
        self.aluno_id = aluno_id
        self.confidence = confidence
        self.method_used = method_used
        self.fr_result = fr_result  # (id, confidence) from face_recognition
        self.df_result = df_result  # (id, confidence, distance) from deepface
        self.processing_time = processing_time
        self.agreement = agreement  # True if both models agree
    
    def to_dict(self) -> Dict:
        """Converte resultado para dicionário"""
        return {
            "aluno_id": self.aluno_id,
            "confidence": self.confidence,
            "method_used": self.method_used,
            "processing_time": round(self.processing_time, 3),
            "agreement": self.agreement,
            "details": {
                "face_recognition": {
                    "aluno_id": self.fr_result[0] if self.fr_result else None,
                    "confidence": round(self.fr_result[1], 2) if self.fr_result else None
                } if self.fr_result else None,
                "deepface": {
                    "aluno_id": self.df_result[0] if self.df_result else None,
                    "confidence": round(self.df_result[1], 2) if self.df_result else None,
                    "distance": round(self.df_result[2], 4) if self.df_result else None
                } if self.df_result else None
            }
        }


def recognize_face_hybrid(
    file: UploadFile,
    known_faces_data: List[Dict[str, Any]],
    mode: str = HYBRID_MODE
) -> HybridRecognitionResult:
    """
    Realiza reconhecimento facial usando estratégia híbrida.
    
    Args:
        file: Arquivo de imagem
        known_faces_data: Lista de rostos conhecidos
        mode: Modo de operação ("smart", "always_both", "fallback")
    
    Returns:
        HybridRecognitionResult com informações detalhadas
    """
    start_time = time.time()
    result = HybridRecognitionResult()
    
    if not known_faces_data:
        result.processing_time = time.time() - start_time
        return result
    
    # PASSO 1: Tentar face_recognition primeiro (sempre mais rápido)
    print("🚀 Iniciando reconhecimento com face_recognition...")
    try:
        fr_encoding = get_face_encoding(file)
        
        if fr_encoding is not None:
            fr_match = recognize_face(fr_encoding, known_faces_data)
            result.fr_result = fr_match
            
            if fr_match:
                fr_id, fr_confidence = fr_match
                print(f"✅ face_recognition encontrou: {fr_id} (confiança: {fr_confidence:.2f}%)")
                
                # MODO 1: SMART - Decide baseado na confiança
                if mode == "smart":
                    # Alta confiança: aceita direto
                    if fr_confidence >= HIGH_CONFIDENCE_THRESHOLD:
                        print(f"✨ Alta confiança ({fr_confidence:.2f}%), aceitando resultado")
                        result.aluno_id = fr_id
                        result.confidence = fr_confidence
                        result.method_used = "face_recognition_only"
                        result.processing_time = time.time() - start_time
                        return result
                    
                    # Confiança média: validar com DeepFace
                    elif fr_confidence >= LOW_CONFIDENCE_THRESHOLD:
                        print(f"⚠️ Confiança média ({fr_confidence:.2f}%), validando com DeepFace...")
                        df_result = _validate_with_deepface(file, known_faces_data)
                        result.df_result = df_result
                        
                        if df_result:
                            df_id, df_confidence, df_distance = df_result
                            
                            # Ambos concordam?
                            if df_id == fr_id:
                                print(f"✅ Ambos concordam! ID: {fr_id}")
                                result.aluno_id = fr_id
                                # Usa média ponderada (face_recognition tem mais peso por ser mais rápido e confiável)
                                result.confidence = (fr_confidence * 0.6) + (df_confidence * 0.4)
                                result.method_used = "hybrid_validated"
                                result.agreement = True
                            else:
                                print(f"❌ Divergência! FR: {fr_id} vs DF: {df_id}")
                                # Usa o de maior confiança
                                if fr_confidence >= df_confidence:
                                    result.aluno_id = fr_id
                                    result.confidence = fr_confidence
                                    result.method_used = "face_recognition_priority"
                                else:
                                    result.aluno_id = df_id
                                    result.confidence = df_confidence
                                    result.method_used = "deepface_priority"
                                result.agreement = False
                        else:
                            # DeepFace não encontrou, mas face_recognition sim
                            print("⚠️ DeepFace não confirmou, usando face_recognition")
                            result.aluno_id = fr_id
                            result.confidence = fr_confidence * 0.8  # Reduz confiança
                            result.method_used = "face_recognition_unvalidated"
                            result.agreement = False
                    
                    # Baixa confiança: tentar DeepFace como autoridade
                    else:
                        print(f"⚠️ Baixa confiança ({fr_confidence:.2f}%), priorizando DeepFace...")
                        df_result = _validate_with_deepface(file, known_faces_data)
                        result.df_result = df_result
                        
                        if df_result:
                            df_id, df_confidence, df_distance = df_result
                            result.aluno_id = df_id
                            result.confidence = df_confidence
                            result.method_used = "deepface_priority"
                            result.agreement = (df_id == fr_id)
                        else:
                            # Nenhum dos dois teve certeza
                            print("❌ Nenhum modelo teve certeza suficiente")
                            result.method_used = "both_uncertain"
                
                # MODO 2: ALWAYS_BOTH - Sempre usa ambos
                elif mode == "always_both":
                    print("🔄 Modo always_both: executando DeepFace...")
                    df_result = _validate_with_deepface(file, known_faces_data)
                    result.df_result = df_result
                    
                    if df_result:
                        df_id, df_confidence, df_distance = df_result
                        
                        if df_id == fr_id:
                            result.aluno_id = fr_id
                            result.confidence = (fr_confidence + df_confidence) / 2
                            result.method_used = "both_agree"
                            result.agreement = True
                        else:
                            # Usa o de maior confiança
                            if fr_confidence >= df_confidence:
                                result.aluno_id = fr_id
                                result.confidence = fr_confidence
                                result.method_used = "face_recognition_priority"
                            else:
                                result.aluno_id = df_id
                                result.confidence = df_confidence
                                result.method_used = "deepface_priority"
                            result.agreement = False
                    else:
                        result.aluno_id = fr_id
                        result.confidence = fr_confidence
                        result.method_used = "face_recognition_only"
                
                # MODO 3: FALLBACK - Só usa DeepFace se face_recognition falhar
                elif mode == "fallback":
                    result.aluno_id = fr_id
                    result.confidence = fr_confidence
                    result.method_used = "face_recognition_only"
            
            else:
                # face_recognition não encontrou match
                print("❌ face_recognition não encontrou correspondência")
                
                if mode in ["smart", "fallback"]:
                    print("🔄 Tentando DeepFace como fallback...")
                    df_result = _validate_with_deepface(file, known_faces_data)
                    result.df_result = df_result
                    
                    if df_result:
                        df_id, df_confidence, df_distance = df_result
                        result.aluno_id = df_id
                        result.confidence = df_confidence
                        result.method_used = "deepface_fallback"
                    else:
                        print("❌ DeepFace também não encontrou")
                        result.method_used = "both_no_match"
        else:
            print("❌ Nenhum rosto detectado por face_recognition")
            # Tentar DeepFace se não detectou rosto
            df_result = _validate_with_deepface(file, known_faces_data)
            result.df_result = df_result
            
            if df_result:
                df_id, df_confidence, df_distance = df_result
                result.aluno_id = df_id
                result.confidence = df_confidence
                result.method_used = "deepface_only"
    
    except Exception as e:
        print(f"❌ Erro no reconhecimento híbrido: {e}")
        result.method_used = "error"
    
    result.processing_time = time.time() - start_time
    return result


def _validate_with_deepface(
    file: UploadFile, 
    known_faces_data: List[Dict[str, Any]]
) -> Optional[Tuple[str, float, float]]:
    """
    Função auxiliar para validar com DeepFace.
    Retorna (student_id, confidence, distance) ou None.
    """
    try:
        # Reset file pointer
        file.file.seek(0)
        
        df_encoding = get_deepface_encoding(file)
        
        if df_encoding is not None:
            df_match = recognize_face_deepface(df_encoding, known_faces_data)
            return df_match
        
    except Exception as e:
        print(f"Erro ao validar com DeepFace: {e}")
    
    return None


def get_hybrid_statistics(results: List[HybridRecognitionResult]) -> Dict:
    """
    Gera estatísticas sobre o desempenho do sistema híbrido.
    
    Args:
        results: Lista de resultados de reconhecimento
    
    Returns:
        Dicionário com estatísticas
    """
    if not results:
        return {}
    
    total = len(results)
    methods = {}
    agreements = {"true": 0, "false": 0, "null": 0}
    total_time = 0.0
    
    for result in results:
        # Contar métodos usados
        method = result.method_used or "unknown"
        methods[method] = methods.get(method, 0) + 1
        
        # Contar concordância
        if result.agreement is True:
            agreements["true"] += 1
        elif result.agreement is False:
            agreements["false"] += 1
        else:
            agreements["null"] += 1
        
        total_time += result.processing_time
    
    return {
        "total_recognitions": total,
        "average_time": round(total_time / total, 3) if total > 0 else 0,
        "methods_distribution": {k: f"{(v/total)*100:.1f}%" for k, v in methods.items()},
        "agreement_rate": f"{(agreements['true']/total)*100:.1f}%" if total > 0 else "0%",
        "disagreement_rate": f"{(agreements['false']/total)*100:.1f}%" if total > 0 else "0%"
    }
