# Testes - Comparação Face Recognition vs DeepFace

Esta pasta contém todos os arquivos relacionados à comparação, datasets e resultados.

## 📂 Estrutura

```
tests/
├── 📊 comparison_results/          # Documentação completa e resultados da comparação
│   ├── INDEX.md                    # Guia de navegação (COMECE AQUI!)
│   ├── README.md                   # Documentação completa (30+ páginas)
│   ├── QUICKSTART.md               # Guia passo a passo de reprodução
│   ├── STRUCTURE.md                # Visão geral da estrutura do projeto
│   ├── graphics/                   # 6 visualizações profissionais (PNG, 300 DPI)
│   └── data/                       # Resultados JSON estruturados
│
├── 🧪 Scripts de Teste
│   ├── test_celebrity_blind.py     # Teste principal de comparação
│   ├── generate_comparison_graphics.py  # Gerador de gráficos
│   └── resize_celebrity_dataset.py # Utilitário de pré-processamento de imagens
│
└── 📁 Datasets
    ├── test_dataset/               # Dados de treinamento (30 celebridades)
    └── celebrity_dataset/          # Dados de teste (429 imagens, 45 celebridades)
```

---

## 🚀 Início Rápido

### 1. Visualizar Resultados
```powershell
# Ler documentação
comparison_results/INDEX.md
```

### 2. Executar Teste de Comparação
```powershell
cd tests
python test_celebrity_blind.py test_dataset celebrity_dataset
```

### 3. Gerar Gráficos
```powershell
cd tests
python generate_comparison_graphics.py
```

---

## 📊 Resumo dos Resultados

**Vencedor:** Face Recognition 🏆

| Métrica | Face Recognition | DeepFace | 
|--------|------------------|----------|
| Precisão | **77.6%** | 54.1% |
| F1 Score | **0.813** | 0.477 |
| Recall | **72.7%** | 31.5% |

**Documentação completa:** [comparison_results/README.md](comparison_results/README.md)

---

## 📝 Descrição dos Arquivos

### Scripts de Teste
- **test_celebrity_blind.py**: Teste de reconhecimento cego com celebridades conhecidas/desconhecidas
- **generate_comparison_graphics.py**: Cria 6 gráficos profissionais de comparação
- **resize_celebrity_dataset.py**: Pré-processa imagens para 300×300 pixels

### Datasets
- **test_dataset/**: 30 celebridades conhecidas para treinamento (1-3 fotos cada)
- **celebrity_dataset/**: 45 celebridades para teste (30 conhecidas + 15 desconhecidas, ~10 fotos cada)

### Resultados
- **comparison_results/**: Documentação completa, gráficos e dados estruturados
  - Toda documentação em markdown
  - 6 gráficos PNG (300 DPI)
  - Arquivo JSON de resultados

---

## ⚙️ Requisitos

Todos os requisitos estão em `../requirements.txt`:
- face-recognition==1.3.0
- deepface==0.0.95
- tensorflow==2.20.0
- scikit-learn==1.7.2
- pandas==2.3.2
- matplotlib==3.10.6
- seaborn==0.13.2

---

## 🎯 Casos de Uso

### Reproduzir o Teste
1. Certifique-se de que os datasets estão no lugar (`test_dataset/` e `celebrity_dataset/`)
2. Execute: `python test_celebrity_blind.py test_dataset celebrity_dataset`
3. Visualize os resultados no terminal e em `comparison_results/`

### Criar Seu Próprio Teste
1. Prepare o dataset de treinamento (rostos conhecidos)
2. Prepare o dataset de teste (mix de conhecidos + desconhecidos)
3. Execute: `python test_celebrity_blind.py seu_treino seu_teste`

### Gerar Apenas Gráficos
1. Execute: `python generate_comparison_graphics.py`
2. Gráficos salvos em `comparison_results/graphics/`

---

## 📚 Documentação

**Comece aqui:** [comparison_results/INDEX.md](comparison_results/INDEX.md)

**Análise completa:** [comparison_results/README.md](comparison_results/README.md)

**Guia rápido:** [comparison_results/QUICKSTART.md](comparison_results/QUICKSTART.md)

---

**Esta pasta contém tudo o que é necessário para a comparação Face Recognition vs DeepFace!**
