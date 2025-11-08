"""
example_comparison.py
---------------------
Exemplo prático de como usar o módulo de comparação.
"""
import requests
import json
import time

# Configuração
API_URL = "http://localhost:8001"
DATASET_PATH = "test_dataset"  # Altere para o caminho do seu dataset

def exemplo_simples():
    """Exemplo mais simples possível - teste completo em 4 passos."""
    print("=" * 70)
    print("EXEMPLO SIMPLES - Comparação em 4 Passos")
    print("=" * 70)
    
    # Passo 1: Validar dataset
    print("\n[1/4] Validando dataset...")
    try:
        response = requests.get(
            f"{API_URL}/comparison/dataset/validate",
            params={"dataset_path": DATASET_PATH}
        )
        if response.status_code == 200:
            stats = response.json()["statistics"]
            print(f"    ✓ {stats['total_students']} alunos, {stats['total_images']} imagens")
        else:
            print(f"    ✗ Erro: {response.text}")
            return
    except Exception as e:
        print(f"    ✗ Erro ao conectar: {e}")
        print("    → Certifique-se de que o servidor está rodando: python -m uvicorn app.main:app --reload --port 8001")
        return
    
    # Passo 2: Executar teste
    print("\n[2/4] Executando teste (isso pode demorar alguns minutos)...")
    response = requests.post(
        f"{API_URL}/comparison/batch-test",
        params={
            "dataset_path": DATASET_PATH,
            "comparison_id": "exemplo_simples",
            "deepface_model": "Facenet512"
        }
    )
    
    if response.status_code != 200:
        print(f"    ✗ Erro no teste: {response.text}")
        return
    
    summary = response.json()["summary"]
    print(f"    ✓ Processadas: {summary['processed']}/{summary['total_images']} imagens")
    
    # Passo 3: Ver resultados
    print("\n[3/4] Obtendo resultados...")
    response = requests.get(f"{API_URL}/comparison/results/exemplo_simples")
    results = response.json()["results"]
    
    fr = results["face_recognition"]
    df = results["deepface"]
    comp = results["comparison"]
    
    print("\n" + "="*70)
    print("RESULTADOS:")
    print("="*70)
    print(f"\nFace Recognition:")
    print(f"  Accuracy: {fr['accuracy']:.1%}")
    print(f"  F1 Score: {fr['f1_macro']:.3f}")
    print(f"  Tempo médio: {fr['avg_processing_time']:.4f}s")
    
    print(f"\nDeepFace (Facenet512):")
    print(f"  Accuracy: {df['accuracy']:.1%}")
    print(f"  F1 Score: {df['f1_macro']:.3f}")
    print(f"  Tempo médio: {df['avg_processing_time']:.4f}s")
    
    print(f"\nVencedor:")
    print(f"  Precisão: {comp['winner_accuracy'].upper()}")
    print(f"  Velocidade: {comp['winner_speed'].upper()}")
    
    # Passo 4: Gerar relatório
    print("\n[4/4] Gerando relatório com gráficos...")
    response = requests.post(f"{API_URL}/comparison/generate-report/exemplo_simples")
    
    if response.status_code == 200:
        data = response.json()
        print(f"    ✓ Relatório salvo em: {data['output_directory']}")
        print(f"    ✓ Arquivo JSON: {data['report_path']}")
    
    print("\n" + "="*70)
    print("✅ CONCLUÍDO!")
    print("="*70)
    print("\nPróximos passos:")
    print("1. Abra a pasta 'comparison_reports' para ver os gráficos")
    print("2. Analise as métricas acima para escolher o melhor modelo")
    print("3. Se DeepFace for melhor, atualize face_service.py para usá-lo")

def exemplo_multiplos_modelos():
    """Testa múltiplos modelos DeepFace e compara todos."""
    print("=" * 70)
    print("EXEMPLO AVANÇADO - Comparar Múltiplos Modelos")
    print("=" * 70)
    
    modelos = ["Facenet512", "ArcFace", "OpenFace"]
    resultados_resumo = []
    
    for i, modelo in enumerate(modelos, 1):
        print(f"\n[{i}/{len(modelos)}] Testando {modelo}...")
        
        comparison_id = f"modelo_{modelo.lower()}"
        
        # Executar teste
        response = requests.post(
            f"{API_URL}/comparison/batch-test",
            params={
                "dataset_path": DATASET_PATH,
                "comparison_id": comparison_id,
                "deepface_model": modelo
            }
        )
        
        if response.status_code != 200:
            print(f"    ✗ Erro com {modelo}")
            continue
        
        # Obter resultados
        response = requests.get(f"{API_URL}/comparison/results/{comparison_id}")
        results = response.json()["results"]
        
        df = results["deepface"]
        resultados_resumo.append({
            "modelo": modelo,
            "accuracy": df["accuracy"],
            "f1_macro": df["f1_macro"],
            "cohen_kappa": df["cohen_kappa"],
            "tempo": df["avg_processing_time"]
        })
        
        print(f"    ✓ Accuracy: {df['accuracy']:.1%}, Tempo: {df['avg_processing_time']:.4f}s")
        
        # Gerar relatório
        requests.post(f"{API_URL}/comparison/generate-report/{comparison_id}")
    
    # Resumo final
    print("\n" + "="*70)
    print("RESUMO - Todos os Modelos")
    print("="*70)
    print(f"\n{'Modelo':<15} {'Accuracy':<12} {'F1 Macro':<12} {'Kappa':<10} {'Tempo (s)':<10}")
    print("-" * 70)
    
    for res in resultados_resumo:
        print(f"{res['modelo']:<15} {res['accuracy']:<12.1%} {res['f1_macro']:<12.3f} "
              f"{res['cohen_kappa']:<10.3f} {res['tempo']:<10.4f}")
    
    # Encontrar melhor
    melhor_accuracy = max(resultados_resumo, key=lambda x: x["accuracy"])
    melhor_velocidade = min(resultados_resumo, key=lambda x: x["tempo"])
    
    print("\n" + "="*70)
    print("🏆 VENCEDORES:")
    print(f"  Melhor Precisão: {melhor_accuracy['modelo']} ({melhor_accuracy['accuracy']:.1%})")
    print(f"  Melhor Velocidade: {melhor_velocidade['modelo']} ({melhor_velocidade['tempo']:.4f}s)")
    print("="*70)

def exemplo_teste_unitario():
    """Testa uma única imagem rapidamente."""
    print("=" * 70)
    print("EXEMPLO - Teste de Imagem Única")
    print("=" * 70)
    
    # Substitua pelo caminho de uma imagem de teste
    imagem_path = "test_dataset/student_1/face_1.jpg"
    ground_truth_id = 1  # ID real do aluno
    
    print(f"\nTestando imagem: {imagem_path}")
    print(f"Ground truth ID: {ground_truth_id}")
    
    try:
        with open(imagem_path, 'rb') as f:
            response = requests.post(
                f"{API_URL}/comparison/test-single",
                files={"foto": f},
                data={
                    "ground_truth_id": ground_truth_id,
                    "deepface_model": "Facenet512"
                }
            )
        
        if response.status_code == 200:
            data = response.json()["dados"]
            
            print("\n" + "="*70)
            print("RESULTADOS:")
            print("="*70)
            
            # Face Recognition
            fr = data["face_recognition"]
            if fr.get("success"):
                print(f"\nFace Recognition:")
                print(f"  Predição: ID {fr['predicted_id']}")
                print(f"  Confiança: {fr['confidence']:.1f}%")
                print(f"  Correto: {'✓' if fr.get('correct') else '✗'}")
                print(f"  Tempo: {fr['processing_time']:.4f}s")
            else:
                print(f"\nFace Recognition: ✗ {fr.get('error', 'Falhou')}")
            
            # DeepFace
            df = data["deepface"]
            if df.get("success"):
                print(f"\nDeepFace:")
                print(f"  Predição: ID {df['predicted_id']}")
                print(f"  Confiança: {df['confidence']:.1f}%")
                print(f"  Correto: {'✓' if df.get('correct') else '✗'}")
                print(f"  Tempo: {df['processing_time']:.4f}s")
            else:
                print(f"\nDeepFace: ✗ {df.get('error', 'Falhou')}")
            
            print("\n" + "="*70)
        else:
            print(f"✗ Erro: {response.text}")
    
    except FileNotFoundError:
        print(f"\n✗ Erro: Arquivo não encontrado: {imagem_path}")
        print("   Altere a variável 'imagem_path' para uma imagem válida do seu dataset")

def menu():
    """Menu interativo para escolher exemplo."""
    print("\n" + "="*70)
    print(" "*20 + "EXEMPLOS DE COMPARAÇÃO")
    print("="*70)
    print("\nEscolha um exemplo:")
    print("  1 - Exemplo Simples (recomendado para começar)")
    print("  2 - Comparar Múltiplos Modelos DeepFace")
    print("  3 - Teste de Imagem Única")
    print("  0 - Sair")
    print("\n" + "="*70)
    
    escolha = input("\nSua escolha: ").strip()
    
    if escolha == "1":
        exemplo_simples()
    elif escolha == "2":
        exemplo_multiplos_modelos()
    elif escolha == "3":
        exemplo_teste_unitario()
    elif escolha == "0":
        print("\nAté logo!")
        return
    else:
        print("\n✗ Opção inválida!")
        menu()

if __name__ == "__main__":
    # Verificar se servidor está rodando
    try:
        response = requests.get(f"{API_URL}/comparison/models/available", timeout=2)
        if response.status_code == 200:
            print("✓ Servidor conectado!")
            menu()
        else:
            print("✗ Servidor não está respondendo corretamente")
    except Exception as e:
        print("\n" + "="*70)
        print("⚠️  SERVIDOR NÃO ESTÁ RODANDO")
        print("="*70)
        print("\nPor favor, inicie o servidor primeiro:")
        print("  cd backend")
        print("  python -m uvicorn app.main:app --reload --port 8001")
        print("\nDepois execute este script novamente.")
        print("="*70)
