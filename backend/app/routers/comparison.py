"""
app/routers/comparison.py
--------------------------
Rotas para comparação entre modelos de reconhecimento facial.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Dict, Optional
import time
import os
from pathlib import Path

from app.services import face_service, deepface_service
from app.services.comparison_service import ModelComparison
from app.services.test_dataset import TestDataset, prepare_comparison_dataset
from app.services import db_service
from app.models.response import ApiResponse

router = APIRouter(prefix="/comparison", tags=["Comparison"])

# Armazenar comparações em memória (pode ser movido para banco de dados)
active_comparisons: Dict[str, ModelComparison] = {}

@router.post("/test-single", response_model=ApiResponse)
async def test_single_image(
    foto: UploadFile = File(...),
    ground_truth_id: int = None,
    deepface_model: str = "Facenet512",
    deepface_detector: str = "opencv",
    deepface_metric: str = "cosine"
):
    """
    Testa uma única imagem com ambos os modelos.
    
    Args:
        foto: Imagem para teste
        ground_truth_id: ID real do aluno (opcional)
        deepface_model: Modelo DeepFace a usar
        deepface_detector: Detector DeepFace
        deepface_metric: Métrica de distância DeepFace
    """
    try:
        # Buscar rostos conhecidos do banco de dados
        faces_data = db_service.get_all_faces()
        
        if not faces_data:
            raise HTTPException(status_code=404, detail="Nenhum rosto cadastrado no banco de dados")
        
        results = {}
        
        # Teste com face_recognition
        foto.file.seek(0)  # Reset file pointer
        start_time = time.time()
        fr_encoding = face_service.get_face_encoding(foto)
        
        if fr_encoding is not None:
            fr_result = face_service.recognize_face(fr_encoding, faces_data)
            fr_time = time.time() - start_time
            
            if fr_result:
                results["face_recognition"] = {
                    "predicted_id": fr_result[0],
                    "confidence": fr_result[1],
                    "processing_time": fr_time,
                    "success": True
                }
            else:
                results["face_recognition"] = {
                    "predicted_id": None,
                    "confidence": 0.0,
                    "processing_time": fr_time,
                    "success": False,
                    "message": "Nenhuma correspondência encontrada"
                }
        else:
            results["face_recognition"] = {
                "success": False,
                "error": "Nenhum rosto detectado",
                "processing_time": time.time() - start_time
            }
        
        # Teste com DeepFace
        foto.file.seek(0)  # Reset file pointer
        start_time = time.time()
        df_encoding = deepface_service.get_deepface_encoding(
            foto, 
            model_name=deepface_model,
            detector_backend=deepface_detector
        )
        
        if df_encoding is not None:
            df_result = deepface_service.recognize_face_deepface(
                df_encoding, 
                faces_data,
                model_name=deepface_model,
                distance_metric=deepface_metric
            )
            df_time = time.time() - start_time
            
            if df_result:
                results["deepface"] = {
                    "predicted_id": df_result[0],
                    "confidence": df_result[1],
                    "distance": df_result[2],
                    "processing_time": df_time,
                    "success": True,
                    "model": deepface_model,
                    "detector": deepface_detector,
                    "metric": deepface_metric
                }
            else:
                results["deepface"] = {
                    "predicted_id": None,
                    "confidence": 0.0,
                    "processing_time": df_time,
                    "success": False,
                    "message": "Nenhuma correspondência encontrada",
                    "model": deepface_model
                }
        else:
            results["deepface"] = {
                "success": False,
                "error": "Nenhum rosto detectado",
                "processing_time": time.time() - start_time,
                "model": deepface_model
            }
        
        # Adicionar ground truth se fornecido
        if ground_truth_id is not None:
            results["ground_truth_id"] = ground_truth_id
            results["face_recognition"]["correct"] = (
                results["face_recognition"].get("predicted_id") == ground_truth_id
            )
            results["deepface"]["correct"] = (
                results["deepface"].get("predicted_id") == ground_truth_id
            )
        
        return ApiResponse(
            sucesso=True,
            mensagem="Teste individual concluído",
            dados=results
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no teste: {str(e)}")

@router.post("/batch-test")
async def batch_test(
    dataset_path: str,
    comparison_id: str = "default",
    deepface_model: str = "Facenet512",
    deepface_detector: str = "opencv",
    deepface_metric: str = "cosine",
    images_per_student: Optional[int] = None
):
    """
    Executa teste em lote usando um dataset estruturado.
    
    Args:
        dataset_path: Caminho para o dataset
        comparison_id: ID único para esta comparação
        deepface_model: Modelo DeepFace
        deepface_detector: Detector DeepFace
        deepface_metric: Métrica de distância
        images_per_student: Limitar número de imagens por aluno
    """
    try:
        # Carregar dataset
        dataset = TestDataset(dataset_path)
        test_pairs = dataset.get_test_pairs(images_per_student)
        
        if not test_pairs:
            raise HTTPException(status_code=404, detail="Nenhuma imagem encontrada no dataset")
        
        # Buscar rostos conhecidos
        faces_data = db_service.get_all_faces()
        
        if not faces_data:
            raise HTTPException(status_code=404, detail="Nenhum rosto cadastrado")
        
        # Criar comparação
        comparison = ModelComparison()
        comparison.save_metadata({
            "deepface_model": deepface_model,
            "deepface_detector": deepface_detector,
            "deepface_metric": deepface_metric
        })
        
        # Processar cada imagem
        results_summary = {
            "total_images": len(test_pairs),
            "processed": 0,
            "errors": 0
        }
        
        for img_path, student_name, student_id in test_pairs:
            try:
                # Criar UploadFile mock a partir do caminho
                with open(img_path, 'rb') as f:
                    file_content = f.read()
                
                # Teste com face_recognition
                from io import BytesIO
                from fastapi import UploadFile
                
                # Face Recognition
                foto_fr = UploadFile(filename=os.path.basename(img_path), file=BytesIO(file_content))
                start_time = time.time()
                fr_encoding = face_service.get_face_encoding(foto_fr)
                
                fr_pred_id = None
                fr_confidence = 0.0
                fr_error = None
                
                if fr_encoding is not None:
                    fr_result = face_service.recognize_face(fr_encoding, faces_data)
                    if fr_result:
                        fr_pred_id = fr_result[0]
                        fr_confidence = fr_result[1]
                else:
                    fr_error = "No face detected"
                
                fr_time = time.time() - start_time
                
                comparison.add_prediction(
                    "face_recognition",
                    fr_pred_id,
                    student_id,
                    fr_confidence,
                    fr_time,
                    fr_error
                )
                
                # DeepFace
                foto_df = UploadFile(filename=os.path.basename(img_path), file=BytesIO(file_content))
                start_time = time.time()
                df_encoding = deepface_service.get_deepface_encoding(
                    foto_df,
                    model_name=deepface_model,
                    detector_backend=deepface_detector
                )
                
                df_pred_id = None
                df_confidence = 0.0
                df_error = None
                
                if df_encoding is not None:
                    df_result = deepface_service.recognize_face_deepface(
                        df_encoding,
                        faces_data,
                        model_name=deepface_model,
                        distance_metric=deepface_metric
                    )
                    if df_result:
                        df_pred_id = df_result[0]
                        df_confidence = df_result[1]
                else:
                    df_error = "No face detected"
                
                df_time = time.time() - start_time
                
                comparison.add_prediction(
                    "deepface",
                    df_pred_id,
                    student_id,
                    df_confidence,
                    df_time,
                    df_error
                )
                
                results_summary["processed"] += 1
                
            except Exception as e:
                print(f"Erro processando {img_path}: {e}")
                results_summary["errors"] += 1
                continue
        
        # Salvar comparação
        active_comparisons[comparison_id] = comparison
        
        # Gerar relatório preliminar
        preliminary_report = comparison.compare_models()
        
        return {
            "success": True,
            "message": "Teste em lote concluído",
            "comparison_id": comparison_id,
            "summary": results_summary,
            "preliminary_results": preliminary_report
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no teste em lote: {str(e)}")

@router.get("/results/{comparison_id}")
async def get_comparison_results(comparison_id: str):
    """Obtém os resultados de uma comparação específica."""
    if comparison_id not in active_comparisons:
        raise HTTPException(status_code=404, detail="Comparação não encontrada")
    
    comparison = active_comparisons[comparison_id]
    results = comparison.compare_models()
    
    return {
        "success": True,
        "comparison_id": comparison_id,
        "results": results
    }

@router.post("/generate-report/{comparison_id}")
async def generate_full_report(
    comparison_id: str,
    output_dir: str = "comparison_reports"
):
    """
    Gera relatório completo com gráficos para uma comparação.
    
    Args:
        comparison_id: ID da comparação
        output_dir: Diretório de saída
    """
    if comparison_id not in active_comparisons:
        raise HTTPException(status_code=404, detail="Comparação não encontrada")
    
    try:
        comparison = active_comparisons[comparison_id]
        report_path = comparison.generate_report(output_dir)
        
        return {
            "success": True,
            "message": "Relatório gerado com sucesso",
            "report_path": report_path,
            "output_directory": output_dir
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")

@router.get("/download-report/{comparison_id}")
async def download_report(comparison_id: str):
    """Baixa o relatório JSON de uma comparação."""
    report_dir = "comparison_reports"
    
    # Procurar arquivo mais recente
    report_files = list(Path(report_dir).glob(f"comparison_*.json"))
    
    if not report_files:
        raise HTTPException(status_code=404, detail="Nenhum relatório encontrado")
    
    # Pegar o mais recente
    latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
    
    return FileResponse(
        path=str(latest_report),
        filename=latest_report.name,
        media_type="application/json"
    )

@router.get("/dataset/validate")
async def validate_dataset(dataset_path: str):
    """Valida um dataset de teste."""
    try:
        dataset = TestDataset(dataset_path)
        stats = dataset.validate_dataset()
        
        return {
            "success": True,
            "message": "Dataset validado",
            "statistics": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao validar dataset: {str(e)}")

@router.post("/dataset/prepare")
async def prepare_dataset(
    source_dir: str,
    output_dir: str,
    train_ratio: float = 0.7
):
    """Prepara um dataset dividindo em treino e teste."""
    try:
        train_path, test_path = prepare_comparison_dataset(
            source_dir,
            output_dir,
            train_ratio
        )
        
        return {
            "success": True,
            "message": "Dataset preparado",
            "train_path": train_path,
            "test_path": test_path
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao preparar dataset: {str(e)}")

@router.get("/models/available")
async def get_available_models():
    """Lista modelos e configurações disponíveis."""
    return {
        "success": True,
        "models": {
            "deepface": {
                "models": ["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "DeepID", "ArcFace", "Dlib", "SFace"],
                "detectors": ["opencv", "ssd", "dlib", "mtcnn", "retinaface", "mediapipe"],
                "metrics": ["cosine", "euclidean", "euclidean_l2"],
                "default": {
                    "model": "Facenet512",
                    "detector": "opencv",
                    "metric": "cosine"
                }
            },
            "face_recognition": {
                "tolerance": face_service.FACE_RECOGNITION_TOLERANCE,
                "model": "HOG + CNN"
            }
        }
    }

@router.delete("/comparison/{comparison_id}")
async def delete_comparison(comparison_id: str):
    """Remove uma comparação da memória."""
    if comparison_id in active_comparisons:
        del active_comparisons[comparison_id]
        return {"success": True, "message": "Comparação removida"}
    else:
        raise HTTPException(status_code=404, detail="Comparação não encontrada")

@router.get("/comparisons/list")
async def list_comparisons():
    """Lista todas as comparações ativas."""
    comparisons_info = {}
    
    for comp_id, comparison in active_comparisons.items():
        comparisons_info[comp_id] = {
            "total_tests": comparison.results["metadata"]["total_tests"],
            "timestamp": comparison.results["metadata"]["timestamp"],
            "deepface_config": {
                "model": comparison.results["metadata"].get("deepface_model"),
                "detector": comparison.results["metadata"].get("deepface_detector"),
                "metric": comparison.results["metadata"].get("deepface_metric")
            }
        }
    
    return {
        "success": True,
        "total_comparisons": len(comparisons_info),
        "comparisons": comparisons_info
    }
