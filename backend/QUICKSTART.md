# 🚀 Quick Start - Comparação de Modelos

Guia rápido para começar a comparar face_recognition vs DeepFace.

## ⚡ Setup Rápido (5 minutos)

### 1. Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

### 2. Preparar Dataset de Teste

Crie uma pasta com suas imagens de teste:

```
test_dataset/
├── aluno_1/
│   ├── foto1.jpg
│   ├── foto2.jpg
│   └── foto3.jpg
├── aluno_2/
│   ├── foto1.jpg
│   └── foto2.jpg
└── aluno_3/
    ├── foto1.jpg
    └── foto2.jpg
```

**Dica:** Use pelo menos 2-3 fotos por aluno para resultados confiáveis.

### 3. Iniciar o Servidor

```bash
python -m uvicorn app.main:app --reload --port 8001
```

### 4. Executar Comparação

**Opção A - Via Script Python:**
```bash
python run_comparison.py test_dataset exp_001 Facenet512
```

**Opção B - Via API (curl):**
```bash
# Validar dataset
curl "http://localhost:8001/comparison/dataset/validate?dataset_path=test_dataset"

# Executar teste
curl -X POST "http://localhost:8001/comparison/batch-test?dataset_path=test_dataset&comparison_id=exp_001&deepface_model=Facenet512"

# Ver resultados
curl "http://localhost:8001/comparison/results/exp_001"

# Gerar relatório
curl -X POST "http://localhost:8001/comparison/generate-report/exp_001"
```

**Opção C - Via Python requests:**
```python
import requests

API_URL = "http://localhost:8001"

# 1. Executar teste
response = requests.post(
    f"{API_URL}/comparison/batch-test",
    params={
        "dataset_path": "test_dataset",
        "comparison_id": "exp_001",
        "deepface_model": "Facenet512"
    }
)
print(response.json())

# 2. Ver resultados
response = requests.get(f"{API_URL}/comparison/results/exp_001")
results = response.json()

# 3. Gerar relatório
response = requests.post(f"{API_URL}/comparison/generate-report/exp_001")
print("Relatório gerado em:", response.json()["output_directory"])
```

## 📊 Interpretando Resultados

### Exemplo de Saída:

```
FACE RECOGNITION:
  Accuracy:           0.850 (85.0%)
  F1 Score (Macro):   0.830
  Cohen's Kappa:      0.780
  Avg Time:           0.0234s

DEEPFACE:
  Accuracy:           0.920 (92.0%)
  F1 Score (Macro):   0.910
  Cohen's Kappa:      0.880
  Avg Time:           0.3421s

COMPARAÇÃO:
  Diferença Accuracy:     +0.070
  Diferença F1 Macro:     +0.080
  Diferença Cohen Kappa:  +0.100
  Diferença Velocidade:   -0.3187s

VENCEDORES:
  Accuracy: DEEPFACE
  F1 Score: DEEPFACE
  Velocidade: FACE_RECOGNITION
```

### Decisão Simples:

**🎯 Use DeepFace se:**
- ✅ Precisão é mais importante que velocidade
- ✅ Você tem GPU disponível
- ✅ Pode aceitar ~300ms por imagem

**⚡ Use Face Recognition se:**
- ✅ Velocidade é crítica (tempo real)
- ✅ Recursos limitados (CPU básica)
- ✅ 85% de precisão é suficiente
- ✅ Necessita processar muitas imagens/segundo

## 🔍 Testando Diferentes Modelos

### Comparar Múltiplos Modelos DeepFace:

```python
import requests

API_URL = "http://localhost:8001"
models = ["Facenet512", "ArcFace", "VGG-Face", "Dlib"]

for model in models:
    print(f"\n🧪 Testando {model}...")
    
    response = requests.post(
        f"{API_URL}/comparison/batch-test",
        params={
            "dataset_path": "test_dataset",
            "comparison_id": f"test_{model}",
            "deepface_model": model
        }
    )
    
    if response.status_code == 200:
        # Ver resultados
        results = requests.get(f"{API_URL}/comparison/results/test_{model}").json()
        comp = results["results"]["comparison"]
        
        print(f"✓ Accuracy Winner: {comp['winner_accuracy']}")
        print(f"✓ F1 Winner: {comp['winner_f1']}")
        print(f"✓ Speed Winner: {comp['winner_speed']}")
        
        # Gerar relatório
        requests.post(f"{API_URL}/comparison/generate-report/test_{model}")
```

## 📈 Gráficos Gerados

Após `generate-report`, você terá:

1. **comparison_YYYYMMDD_HHMMSS.json** - Dados completos
2. **metrics_comparison_*.png** - Comparação visual
3. **kappa_time_*.png** - Kappa e tempo
4. **confusion_matrices_*.png** - Matrizes de confusão

Abra em `comparison_reports/`

## 🧪 Exemplo Completo: Do Zero ao Relatório

```python
import requests
import json

API_URL = "http://localhost:8001"

# Passo 1: Validar dataset
print("📁 Validando dataset...")
response = requests.get(
    f"{API_URL}/comparison/dataset/validate",
    params={"dataset_path": "test_dataset"}
)
stats = response.json()["statistics"]
print(f"   ✓ {stats['total_students']} alunos, {stats['total_images']} imagens")

# Passo 2: Listar modelos disponíveis
print("\n🔍 Modelos disponíveis:")
response = requests.get(f"{API_URL}/comparison/models/available")
models = response.json()["models"]["deepface"]["models"]
print(f"   ✓ {len(models)} modelos: {', '.join(models[:3])}...")

# Passo 3: Executar teste
print("\n🚀 Executando comparação...")
response = requests.post(
    f"{API_URL}/comparison/batch-test",
    params={
        "dataset_path": "test_dataset",
        "comparison_id": "my_test",
        "deepface_model": "Facenet512"
    }
)

if response.status_code == 200:
    summary = response.json()["summary"]
    print(f"   ✓ Processadas: {summary['processed']}/{summary['total_images']}")

# Passo 4: Ver resultados
print("\n📊 Resultados:")
response = requests.get(f"{API_URL}/comparison/results/my_test")
results = response.json()["results"]

fr = results["face_recognition"]
df = results["deepface"]
comp = results["comparison"]

print(f"   Face Recognition: {fr['accuracy']:.1%} accuracy, {fr['avg_processing_time']:.4f}s")
print(f"   DeepFace:         {df['accuracy']:.1%} accuracy, {df['avg_processing_time']:.4f}s")
print(f"   Vencedor:         {comp['winner_accuracy'].upper()}")

# Passo 5: Gerar relatório
print("\n📄 Gerando relatório...")
response = requests.post(f"{API_URL}/comparison/generate-report/my_test")
report_path = response.json()["report_path"]
print(f"   ✓ Relatório salvo: {report_path}")

print("\n✅ Concluído! Verifique a pasta 'comparison_reports'")
```

## 🎓 Próximos Passos

1. **Testar com mais imagens:** Quanto mais, melhor a estatística
2. **Variar condições:** Teste com diferentes iluminações, ângulos
3. **Ajustar thresholds:** Experimente diferentes valores
4. **Comparar detectores:** `opencv` vs `mtcnn` vs `retinaface`
5. **Métricas customizadas:** Adicione suas próprias métricas

## ❓ FAQ Rápido

**Q: Qual o mínimo de imagens necessário?**
A: 2-3 por aluno, mas 5+ é ideal.

**Q: Quanto tempo demora?**
A: ~0.02s/img com face_recognition, ~0.3s/img com DeepFace.

**Q: Preciso de GPU?**
A: Não, mas ajuda muito com DeepFace.

**Q: Posso usar meus próprios alunos cadastrados?**
A: Sim! O sistema busca automaticamente do banco de dados.

**Q: E se houver erro "No face detected"?**
A: Tente outro detector (`mtcnn`) ou melhore a qualidade das imagens.

## 📞 Suporte

- Ver logs detalhados: Terminal do uvicorn
- Debug: Adicione `print()` nos services
- Issues: Verifique COMPARISON_GUIDE.md

---

**Happy Testing! 🎉**
