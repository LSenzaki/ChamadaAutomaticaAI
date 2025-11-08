# Guia de Comparação de Modelos de Reconhecimento Facial

Este guia explica como usar o módulo de comparação para testar e comparar **face_recognition** vs **DeepFace** usando métricas estatísticas robustas.

## 📋 Índice

1. [Instalação](#instalação)
2. [Estrutura do Dataset](#estrutura-do-dataset)
3. [Endpoints Disponíveis](#endpoints-disponíveis)
4. [Exemplos de Uso](#exemplos-de-uso)
5. [Métricas Calculadas](#métricas-calculadas)
6. [Interpretação dos Resultados](#interpretação-dos-resultados)

## 🔧 Instalação

### 1. Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

As principais bibliotecas adicionadas são:
- `face_recognition==1.3.0` - Biblioteca de reconhecimento facial baseada em dlib
- `deepface==0.0.93` - Framework com múltiplos modelos de deep learning
- `scikit-learn==1.3.2` - Para cálculo de métricas
- `pandas==2.1.4` - Manipulação de dados
- `matplotlib==3.8.2` e `seaborn==0.13.0` - Visualização
- `tf-keras==2.16.0` - Backend para DeepFace

### 2. Iniciar o Servidor

```bash
python -m uvicorn app.main:app --reload --port 8001
```

## 📁 Estrutura do Dataset

Para realizar a comparação, você precisa de um dataset estruturado:

```
test_dataset/
├── student_1/
│   ├── face_1.jpg
│   ├── face_2.jpg
│   └── face_3.jpg
├── student_2/
│   ├── face_1.jpg
│   ├── face_2.jpg
│   └── face_3.jpg
└── student_3/
    ├── face_1.jpg
    └── face_2.jpg
```

**Recomendações:**
- Mínimo de 2-3 imagens por aluno
- Imagens variadas (diferentes ângulos, expressões, iluminação)
- Formato: JPG, JPEG ou PNG
- Resolução mínima: 640x480px

## 🛠️ Endpoints Disponíveis

### 1. Testar Imagem Individual

```http
POST /comparison/test-single
```

Testa uma única imagem com ambos os modelos.

**Parâmetros:**
- `foto` (file): Imagem para teste
- `ground_truth_id` (int, opcional): ID real do aluno
- `deepface_model` (string): Modelo DeepFace (padrão: "Facenet512")
- `deepface_detector` (string): Detector (padrão: "opencv")
- `deepface_metric` (string): Métrica de distância (padrão: "cosine")

**Exemplo (curl):**
```bash
curl -X POST "http://localhost:8001/comparison/test-single" \
  -F "foto=@path/to/image.jpg" \
  -F "ground_truth_id=1" \
  -F "deepface_model=Facenet512"
```

### 2. Teste em Lote (Batch Test)

```http
POST /comparison/batch-test
```

Executa teste em lote usando um dataset completo.

**Parâmetros JSON:**
```json
{
  "dataset_path": "D:/Projetos/test_dataset",
  "comparison_id": "experiment_001",
  "deepface_model": "Facenet512",
  "deepface_detector": "opencv",
  "deepface_metric": "cosine",
  "images_per_student": null
}
```

**Exemplo (Python):**
```python
import requests

response = requests.post(
    "http://localhost:8001/comparison/batch-test",
    params={
        "dataset_path": "D:/Projetos/test_dataset",
        "comparison_id": "exp_001",
        "deepface_model": "Facenet512",
        "deepface_detector": "opencv",
        "deepface_metric": "cosine"
    }
)
print(response.json())
```

### 3. Obter Resultados

```http
GET /comparison/results/{comparison_id}
```

Retorna os resultados completos de uma comparação.

### 4. Gerar Relatório com Gráficos

```http
POST /comparison/generate-report/{comparison_id}
```

Gera relatório completo com gráficos e estatísticas.

**Exemplo:**
```bash
curl -X POST "http://localhost:8001/comparison/generate-report/exp_001?output_dir=comparison_reports"
```

### 5. Download do Relatório

```http
GET /comparison/download-report/{comparison_id}
```

Baixa o arquivo JSON com os resultados.

### 6. Validar Dataset

```http
GET /comparison/dataset/validate?dataset_path=D:/Projetos/test_dataset
```

Valida a estrutura do dataset antes de executar testes.

### 7. Listar Modelos Disponíveis

```http
GET /comparison/models/available
```

Lista todos os modelos DeepFace disponíveis e suas configurações.

**Modelos DeepFace Disponíveis:**
- VGG-Face
- Facenet
- Facenet512 (recomendado)
- OpenFace
- DeepFace
- DeepID
- ArcFace
- Dlib
- SFace

## 📊 Métricas Calculadas

### 1. Cohen's Kappa (κ)
**O que mede:** Concordância entre predições e ground truth, ajustado para concordância ao acaso.

**Interpretação:**
- κ < 0: Sem concordância
- 0.00 - 0.20: Concordância leve
- 0.21 - 0.40: Concordância razoável
- 0.41 - 0.60: Concordância moderada
- 0.61 - 0.80: Concordância substancial
- 0.81 - 1.00: Concordância quase perfeita

### 2. F1 Score (Macro)
**O que mede:** Média harmônica entre precisão e recall, calculada para cada classe separadamente.

**Fórmula:** F1 = 2 × (Precision × Recall) / (Precision + Recall)

**Interpretação:**
- 0.0 - 0.5: Desempenho ruim
- 0.5 - 0.7: Desempenho moderado
- 0.7 - 0.9: Bom desempenho
- 0.9 - 1.0: Excelente desempenho

### 3. Precision (Macro)
**O que mede:** Proporção de predições corretas entre todas as predições positivas.

**Quando usar:** Quando o custo de falsos positivos é alto.

### 4. Recall (Macro)
**O que mede:** Proporção de casos positivos reais que foram corretamente identificados.

**Quando usar:** Quando o custo de falsos negativos é alto.

### 5. Accuracy
**O que mede:** Proporção total de predições corretas.

**Limitação:** Pode ser enganosa em datasets desbalanceados.

### 6. Processing Time
**O que mede:** Tempo médio de processamento por imagem.

**Importância:** Crucial para aplicações em tempo real.

### 7. Confusion Matrix
**O que mostra:** Distribuição de verdadeiros positivos, falsos positivos, verdadeiros negativos e falsos negativos.

## 📈 Interpretação dos Resultados

### Exemplo de Resposta JSON

```json
{
  "face_recognition": {
    "accuracy": 0.85,
    "f1_macro": 0.83,
    "precision_macro": 0.84,
    "recall_macro": 0.82,
    "cohen_kappa": 0.78,
    "avg_processing_time": 0.0234,
    "total_predictions": 50,
    "valid_predictions": 48
  },
  "deepface": {
    "accuracy": 0.92,
    "f1_macro": 0.91,
    "precision_macro": 0.93,
    "recall_macro": 0.89,
    "cohen_kappa": 0.88,
    "avg_processing_time": 0.3421,
    "total_predictions": 50,
    "valid_predictions": 49
  },
  "comparison": {
    "accuracy_diff": 0.07,
    "f1_macro_diff": 0.08,
    "cohen_kappa_diff": 0.10,
    "speed_diff": -0.3187,
    "winner_accuracy": "deepface",
    "winner_f1": "deepface",
    "winner_speed": "face_recognition"
  }
}
```

### Análise do Exemplo

**Accuracy:**
- DeepFace: 92% vs Face Recognition: 85%
- **Vencedor:** DeepFace (+7%)

**F1 Macro:**
- DeepFace: 91% vs Face Recognition: 83%
- **Vencedor:** DeepFace (+8%)

**Cohen's Kappa:**
- DeepFace: 0.88 (concordância quase perfeita)
- Face Recognition: 0.78 (concordância substancial)
- **Vencedor:** DeepFace (+0.10)

**Processing Time:**
- Face Recognition: 23.4ms
- DeepFace: 342.1ms
- **Vencedor:** Face Recognition (14.6x mais rápido)

### Decisão

**Escolha DeepFace se:**
- Precisão é prioridade máxima
- Tempo de processamento não é crítico
- Você tem recursos computacionais (GPU recomendada)
- Poucos falsos positivos são essenciais

**Escolha Face Recognition se:**
- Velocidade é crítica (tempo real)
- Recursos limitados (CPU básica)
- Precisão de 85% é aceitável
- Aplicação em dispositivos móveis/edge

## 🖼️ Gráficos Gerados

O relatório gera automaticamente:

1. **metrics_comparison_[timestamp].png**
   - Comparação visual de Accuracy, F1, Precision, Recall

2. **kappa_time_[timestamp].png**
   - Cohen's Kappa e tempo de processamento

3. **confusion_matrices_[timestamp].png**
   - Matrizes de confusão lado a lado

## 🔬 Casos de Uso Práticos

### Caso 1: Validação Inicial do Sistema

```python
# 1. Validar dataset
response = requests.get(
    "http://localhost:8001/comparison/dataset/validate",
    params={"dataset_path": "test_dataset"}
)

# 2. Executar teste rápido (1 imagem por aluno)
response = requests.post(
    "http://localhost:8001/comparison/batch-test",
    params={
        "dataset_path": "test_dataset",
        "comparison_id": "quick_test",
        "images_per_student": 1
    }
)

# 3. Ver resultados
response = requests.get(
    "http://localhost:8001/comparison/results/quick_test"
)
```

### Caso 2: Comparação Completa de Modelos DeepFace

```python
models = ["Facenet512", "ArcFace", "VGG-Face"]

for model in models:
    response = requests.post(
        "http://localhost:8001/comparison/batch-test",
        params={
            "dataset_path": "test_dataset",
            "comparison_id": f"test_{model}",
            "deepface_model": model
        }
    )
    
    # Gerar relatório
    requests.post(
        f"http://localhost:8001/comparison/generate-report/test_{model}"
    )
```

### Caso 3: Teste A/B com Ground Truth

Cadastre alunos no sistema, depois teste reconhecimento:

```python
# Teste cada imagem e compare com ID cadastrado
for student_id, images in dataset.items():
    for img_path in images:
        with open(img_path, 'rb') as f:
            response = requests.post(
                "http://localhost:8001/comparison/test-single",
                files={"foto": f},
                data={"ground_truth_id": student_id}
            )
            print(response.json())
```

## 🎯 Recomendações

1. **Dataset de Teste:**
   - Mínimo 5 alunos com 3-5 imagens cada
   - Inclua variações (óculos, barba, iluminação diferente)
   - Separe treino (cadastro) e teste (validação)

2. **Configuração DeepFace:**
   - Para melhor precisão: `Facenet512` ou `ArcFace`
   - Para velocidade: `OpenFace` ou `Dlib`
   - Detector: `opencv` (rápido) ou `mtcnn` (preciso)

3. **Execução:**
   - Rode múltiplos testes para validar consistência
   - Use GPU para DeepFace se disponível
   - Compare diferentes thresholds

4. **Análise:**
   - Foque em Cohen's Kappa para avaliação geral
   - Use F1 Macro para datasets desbalanceados
   - Considere tempo de processamento para produção

## 🐛 Troubleshooting

### Erro: "No face detected"
- Verifique qualidade das imagens
- Tente outro detector (`mtcnn`, `retinaface`)
- Melhore iluminação das fotos

### Baixa Accuracy em ambos
- Dataset pode estar com labels incorretos
- Imagens muito diferentes entre treino e teste
- Verificar se faces estão cadastradas corretamente

### DeepFace muito lento
- Instale TensorFlow com GPU
- Use modelo mais leve (`OpenFace`)
- Reduza resolução das imagens

## 📝 Próximos Passos

Após a comparação, você pode:
1. Atualizar `face_service.py` para usar o modelo vencedor
2. Implementar sistema híbrido (rápido + preciso)
3. Ajustar thresholds baseado nas métricas
4. Criar pipeline de retreinamento contínuo

---

**Criado por:** Sistema de Comparação de Modelos
**Versão:** 1.0.0
**Data:** Novembro 2025
