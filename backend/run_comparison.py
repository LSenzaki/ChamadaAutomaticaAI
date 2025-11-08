"""
run_comparison.py
-----------------
Script para executar comparação de modelos facilmente via linha de comando.
"""
import requests
import json
import sys
import os
from pathlib import Path
import time

API_URL = "http://localhost:8001"

def print_section(title):
    """Imprime uma seção formatada."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def validate_dataset(dataset_path):
    """Valida o dataset antes de executar testes."""
    print_section("VALIDANDO DATASET")
    
    response = requests.get(
        f"{API_URL}/comparison/dataset/validate",
        params={"dataset_path": dataset_path}
    )
    
    if response.status_code == 200:
        data = response.json()
        stats = data.get("statistics", {})
        
        print(f"✓ Total de alunos: {stats.get('total_students', 0)}")
        print(f"✓ Total de imagens: {stats.get('total_images', 0)}")
        print(f"✓ Média de imagens por aluno: {stats.get('avg_images_per_student', 0):.1f}")
        print(f"✓ Mín/Máx: {stats.get('min_images_per_student', 0)} / {stats.get('max_images_per_student', 0)}")
        
        warnings = stats.get('warnings', [])
        if warnings:
            print("\n⚠️  Avisos:")
            for warning in warnings:
                print(f"   - {warning}")
        
        return True
    else:
        print(f"✗ Erro ao validar dataset: {response.text}")
        return False

def list_available_models():
    """Lista modelos disponíveis."""
    print_section("MODELOS DISPONÍVEIS")
    
    response = requests.get(f"{API_URL}/comparison/models/available")
    
    if response.status_code == 200:
        data = response.json()
        deepface = data.get("models", {}).get("deepface", {})
        
        print("DeepFace Models:")
        for model in deepface.get("models", []):
            print(f"  - {model}")
        
        print("\nDetectors:")
        for detector in deepface.get("detectors", []):
            print(f"  - {detector}")
        
        print("\nDistance Metrics:")
        for metric in deepface.get("metrics", []):
            print(f"  - {metric}")
        
        default = deepface.get("default", {})
        print(f"\nConfigurações Padrão:")
        print(f"  Model: {default.get('model')}")
        print(f"  Detector: {default.get('detector')}")
        print(f"  Metric: {default.get('metric')}")
        
        return True
    else:
        print(f"✗ Erro ao listar modelos: {response.text}")
        return False

def run_batch_test(dataset_path, comparison_id, deepface_model="Facenet512", 
                   deepface_detector="opencv", deepface_metric="cosine",
                   images_per_student=None):
    """Executa teste em lote."""
    print_section(f"EXECUTANDO TESTE EM LOTE - {comparison_id}")
    
    print(f"Dataset: {dataset_path}")
    print(f"DeepFace Model: {deepface_model}")
    print(f"Detector: {deepface_detector}")
    print(f"Metric: {deepface_metric}")
    
    if images_per_student:
        print(f"Imagens por aluno: {images_per_student}")
    
    print("\nProcessando... (isso pode demorar alguns minutos)")
    
    start_time = time.time()
    
    response = requests.post(
        f"{API_URL}/comparison/batch-test",
        params={
            "dataset_path": dataset_path,
            "comparison_id": comparison_id,
            "deepface_model": deepface_model,
            "deepface_detector": deepface_detector,
            "deepface_metric": deepface_metric,
            "images_per_student": images_per_student
        }
    )
    
    elapsed_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        summary = data.get("summary", {})
        
        print(f"\n✓ Teste concluído em {elapsed_time:.1f} segundos")
        print(f"✓ Total de imagens: {summary.get('total_images', 0)}")
        print(f"✓ Processadas: {summary.get('processed', 0)}")
        print(f"✓ Erros: {summary.get('errors', 0)}")
        
        return True, data
    else:
        print(f"\n✗ Erro no teste: {response.text}")
        return False, None

def get_results(comparison_id):
    """Obtém e exibe resultados da comparação."""
    print_section(f"RESULTADOS - {comparison_id}")
    
    response = requests.get(f"{API_URL}/comparison/results/{comparison_id}")
    
    if response.status_code == 200:
        data = response.json()
        results = data.get("results", {})
        
        # Face Recognition
        fr = results.get("face_recognition", {})
        print("FACE RECOGNITION:")
        print(f"  Accuracy:           {fr.get('accuracy', 0):.3f} ({fr.get('accuracy', 0)*100:.1f}%)")
        print(f"  F1 Score (Macro):   {fr.get('f1_macro', 0):.3f}")
        print(f"  Precision (Macro):  {fr.get('precision_macro', 0):.3f}")
        print(f"  Recall (Macro):     {fr.get('recall_macro', 0):.3f}")
        print(f"  Cohen's Kappa:      {fr.get('cohen_kappa', 0):.3f}")
        print(f"  Avg Time:           {fr.get('avg_processing_time', 0):.4f}s")
        print(f"  Valid Predictions:  {fr.get('valid_predictions', 0)}/{fr.get('total_predictions', 0)}")
        
        # DeepFace
        df = results.get("deepface", {})
        print("\nDEEPFACE:")
        print(f"  Accuracy:           {df.get('accuracy', 0):.3f} ({df.get('accuracy', 0)*100:.1f}%)")
        print(f"  F1 Score (Macro):   {df.get('f1_macro', 0):.3f}")
        print(f"  Precision (Macro):  {df.get('precision_macro', 0):.3f}")
        print(f"  Recall (Macro):     {df.get('recall_macro', 0):.3f}")
        print(f"  Cohen's Kappa:      {df.get('cohen_kappa', 0):.3f}")
        print(f"  Avg Time:           {df.get('avg_processing_time', 0):.4f}s")
        print(f"  Valid Predictions:  {df.get('valid_predictions', 0)}/{df.get('total_predictions', 0)}")
        
        # Comparação
        comp = results.get("comparison", {})
        print("\nCOMPARAÇÃO:")
        print(f"  Diferença Accuracy:     {comp.get('accuracy_diff', 0):+.3f}")
        print(f"  Diferença F1 Macro:     {comp.get('f1_macro_diff', 0):+.3f}")
        print(f"  Diferença Cohen Kappa:  {comp.get('cohen_kappa_diff', 0):+.3f}")
        print(f"  Diferença Velocidade:   {comp.get('speed_diff', 0):+.4f}s")
        
        print("\nVENCEDORES:")
        print(f"  Accuracy: {comp.get('winner_accuracy', 'N/A').upper()}")
        print(f"  F1 Score: {comp.get('winner_f1', 'N/A').upper()}")
        print(f"  Velocidade: {comp.get('winner_speed', 'N/A').upper()}")
        
        # Recomendação
        print("\nRECOMENDAÇÃO:")
        if comp.get('winner_accuracy') == 'deepface' and comp.get('winner_f1') == 'deepface':
            print("  → Use DEEPFACE se precisão é prioridade")
            print(f"    Ganho de accuracy: +{comp.get('accuracy_diff', 0)*100:.1f}%")
        else:
            print("  → Use FACE_RECOGNITION para melhor balanço")
        
        if comp.get('winner_speed') == 'face_recognition':
            speed_factor = abs(df.get('avg_processing_time', 1) / fr.get('avg_processing_time', 1))
            print(f"  → Face Recognition é {speed_factor:.1f}x mais rápido")
        
        return True, results
    else:
        print(f"✗ Erro ao obter resultados: {response.text}")
        return False, None

def generate_report(comparison_id, output_dir="comparison_reports"):
    """Gera relatório completo com gráficos."""
    print_section(f"GERANDO RELATÓRIO - {comparison_id}")
    
    response = requests.post(
        f"{API_URL}/comparison/generate-report/{comparison_id}",
        params={"output_dir": output_dir}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Relatório gerado com sucesso!")
        print(f"✓ Arquivo JSON: {data.get('report_path')}")
        print(f"✓ Diretório: {data.get('output_directory')}")
        print(f"\nGráficos salvos:")
        print(f"  - metrics_comparison_*.png")
        print(f"  - kappa_time_*.png")
        print(f"  - confusion_matrices_*.png")
        return True
    else:
        print(f"✗ Erro ao gerar relatório: {response.text}")
        return False

def main():
    """Função principal."""
    print("\n" + "="*70)
    print(" "*15 + "COMPARAÇÃO DE MODELOS DE RECONHECIMENTO FACIAL")
    print(" "*20 + "Face Recognition vs DeepFace")
    print("="*70)
    
    # Configuração
    if len(sys.argv) < 2:
        print("\nUso:")
        print("  python run_comparison.py <dataset_path> [comparison_id] [deepface_model]")
        print("\nExemplo:")
        print("  python run_comparison.py D:/Projetos/test_dataset exp_001 Facenet512")
        print("\nModelos disponíveis:")
        print("  Facenet512 (padrão), ArcFace, VGG-Face, Dlib, OpenFace")
        sys.exit(1)
    
    dataset_path = sys.argv[1]
    comparison_id = sys.argv[2] if len(sys.argv) > 2 else f"comparison_{int(time.time())}"
    deepface_model = sys.argv[3] if len(sys.argv) > 3 else "Facenet512"
    
    # Verificar se dataset existe
    if not Path(dataset_path).exists():
        print(f"\n✗ Erro: Dataset não encontrado em {dataset_path}")
        sys.exit(1)
    
    # Listar modelos disponíveis
    list_available_models()
    
    # Validar dataset
    if not validate_dataset(dataset_path):
        sys.exit(1)
    
    # Executar teste
    success, test_data = run_batch_test(
        dataset_path=dataset_path,
        comparison_id=comparison_id,
        deepface_model=deepface_model
    )
    
    if not success:
        sys.exit(1)
    
    # Obter resultados
    success, results = get_results(comparison_id)
    
    if not success:
        sys.exit(1)
    
    # Gerar relatório
    generate_report(comparison_id)
    
    print_section("CONCLUÍDO")
    print(f"✓ Comparação '{comparison_id}' finalizada com sucesso!")
    print(f"✓ Verifique o diretório 'comparison_reports' para gráficos e relatórios.")
    print()

if __name__ == "__main__":
    main()
