# 🔬 Módulo de Comparação: Face Recognition vs DeepFace

## 📌 Visão Geral

Este módulo permite comparar o desempenho de dois sistemas de reconhecimento facial:
- **face_recognition**: Biblioteca rápida baseada em dlib
- **DeepFace**: Framework com 9 modelos de deep learning

### Métricas Calculadas:
✅ **Cohen's Kappa** - Concordância ajustada ao acaso  
✅ **F1 Score (Macro)** - Média harmônica precision/recall  
✅ **Precision & Recall** - Macro e weighted  
✅ **Accuracy** - Acurácia geral  
✅ **Confusion Matrix** - Matriz de confusão  
✅ **Processing Time** - Tempo de processamento  

## 🚀 Início Rápido (3 comandos)

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Iniciar servidor
python -m uvicorn app.main:app --reload --port 8001

# 3. Executar comparação
python run_comparison.py test_dataset exp_001
```

## 📁 Estrutura do Dataset

```
test_dataset/
├── aluno_1/
│   ├── foto1.jpg
│   ├── foto2.jpg
│   └── foto3.jpg
├── aluno_2/
│   └── ...
└── aluno_3/
    └── ...
```

## 📚 Documentação

| Arquivo | Descrição |
|---------|-----------|
| **QUICKSTART.md** | Guia rápido - comece aqui! |
| **COMPARISON_GUIDE.md** | Documentação completa e detalhada |
| **COMPARISON_SUMMARY.md** | Resumo técnico com todas as métricas |
| **example_comparison.py** | Scripts de exemplo prontos para usar |
| **run_comparison.py** | CLI para executar comparações |

## 🎯 Uso Básico

### Opção 1: Script Python Interativo

```bash
python example_comparison.py
```

Menu com 3 exemplos:
1. Comparação simples
2. Múltiplos modelos
3. Teste de imagem única

### Opção 2: CLI

```bash
python run_comparison.py <dataset_path> [id] [model]

# Exemplos:
python run_comparison.py test_dataset exp_001 Facenet512
python run_comparison.py test_dataset exp_002 ArcFace
```

### Opção 3: API Direta

```python
import requests

# Executar teste
response = requests.post(
    "http://localhost:8001/comparison/batch-test",
    params={
        "dataset_path": "test_dataset",
        "comparison_id": "my_test",
        "deepface_model": "Facenet512"
    }
)

# Ver resultados
response = requests.get(
    "http://localhost:8001/comparison/results/my_test"
)
print(response.json())
```

## 📊 Exemplo de Resultado

```
FACE RECOGNITION:
  Accuracy:           85.0%
  F1 Score (Macro):   0.830
  Cohen's Kappa:      0.780
  Avg Time:           0.0234s

DEEPFACE (Facenet512):
  Accuracy:           92.0%
  F1 Score (Macro):   0.910
  Cohen's Kappa:      0.880
  Avg Time:           0.3421s

VENCEDORES:
  Precisão: DEEPFACE (+7%)
  Velocidade: FACE_RECOGNITION (14.6x mais rápido)
```

## 🎨 Gráficos Gerados

Após `generate-report`, você terá:
- 📊 **metrics_comparison_*.png** - Comparação visual de métricas
- ⏱️ **kappa_time_*.png** - Cohen's Kappa e tempo
- 🔲 **confusion_matrices_*.png** - Matrizes de confusão
- 📄 **comparison_*.json** - Dados completos em JSON

## 🛠️ Modelos DeepFace Disponíveis

| Modelo | Precisão | Velocidade | Recomendado Para |
|--------|----------|------------|------------------|
| **Facenet512** ⭐ | Alta | Média | Uso geral (recomendado) |
| ArcFace | Muito Alta | Média | Máxima precisão |
| VGG-Face | Alta | Lenta | Benchmarks |
| Dlib | Média | Rápida | Tempo real |
| OpenFace | Média | Rápida | Edge devices |

## 🎓 Casos de Uso

### 1. Validação Inicial
Verificar se o sistema funciona antes de produção.

### 2. Escolha de Modelo
Decidir qual modelo usar baseado em métricas objetivas.

### 3. Otimização
Comparar diferentes configurações e escolher a melhor.

### 4. Análise de Falhas
Usar confusion matrix para identificar problemas.

## 💡 Decisão Rápida

**Use DeepFace se:**
- ✅ Precisão é prioridade máxima
- ✅ Tem GPU disponível
- ✅ Pode aceitar ~300ms por imagem
- ✅ Precisa minimizar falsos positivos

**Use Face Recognition se:**
- ✅ Velocidade é crítica (tempo real)
- ✅ Recursos limitados (CPU básica)
- ✅ 85% de precisão é suficiente
- ✅ Precisa processar muitas imagens/segundo

## 🔧 Endpoints da API

```
POST   /comparison/test-single          # Testa imagem individual
POST   /comparison/batch-test           # Teste em lote
GET    /comparison/results/{id}         # Obter resultados
POST   /comparison/generate-report/{id} # Gerar relatório
GET    /comparison/download-report/{id} # Download JSON
GET    /comparison/dataset/validate     # Validar dataset
GET    /comparison/models/available     # Listar modelos
GET    /comparison/comparisons/list     # Listar comparações
DELETE /comparison/{id}                 # Remover comparação
```

Documentação completa: http://localhost:8001/docs

## 📦 Arquivos do Módulo

### Services
- `app/services/deepface_service.py` - Wrapper DeepFace
- `app/services/comparison_service.py` - Lógica de comparação
- `app/services/test_dataset.py` - Gerenciamento de datasets

### Router
- `app/routers/comparison.py` - Endpoints da API

### Utilitários
- `run_comparison.py` - CLI script
- `example_comparison.py` - Exemplos interativos

### Documentação
- `README_COMPARISON.md` - Este arquivo
- `QUICKSTART.md` - Início rápido
- `COMPARISON_GUIDE.md` - Guia completo
- `COMPARISON_SUMMARY.md` - Resumo técnico

## 🐛 Troubleshooting

### "No face detected"
- Tente outro detector: `mtcnn` ou `retinaface`
- Verifique qualidade das imagens
- Melhore iluminação

### DeepFace muito lento
- Instale TensorFlow com GPU
- Use modelo mais leve: `OpenFace`
- Reduza resolução das imagens

### Baixa accuracy em ambos
- Verifique labels do dataset
- Use mais imagens variadas
- Ajuste thresholds

### Erro de conexão
```bash
# Certifique-se de que o servidor está rodando:
python -m uvicorn app.main:app --reload --port 8001
```

## 📈 Próximos Passos

1. ✅ Execute `python example_comparison.py`
2. ✅ Analise os resultados e gráficos
3. ✅ Escolha o melhor modelo para seu caso
4. ✅ Atualize `face_service.py` se necessário
5. ✅ Documente sua decisão

## 🤝 Contribuindo

Para adicionar novos modelos ou métricas:
1. Edite `comparison_service.py` para novas métricas
2. Edite `deepface_service.py` para novos modelos
3. Atualize a documentação

## 📞 Suporte

- 📖 Leia `COMPARISON_GUIDE.md` para detalhes
- 🚀 Use `QUICKSTART.md` para começar rápido
- 💡 Execute `example_comparison.py` para exemplos
- 🔍 Veja logs no terminal do uvicorn

## ✨ Features

✅ Comparação automatizada de modelos  
✅ 7 métricas estatísticas robustas  
✅ Geração automática de gráficos  
✅ Suporte a 9 modelos DeepFace  
✅ API REST completa  
✅ CLI script  
✅ Exemplos interativos  
✅ Documentação detalhada  
✅ Export para JSON/DataFrame  
✅ Validação de dataset  

---

**Versão:** 1.0.0  
**Criado:** Novembro 2025  
**Licença:** MIT  

**Happy Comparing! 🎉**
