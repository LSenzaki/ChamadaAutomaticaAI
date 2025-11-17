# Sistema de Reconhecimento Facial para Chamada Acadêmica

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18.0+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)

Sistema inteligente de controle de presença acadêmica utilizando reconhecimento facial híbrido (face_recognition + DeepFace) com interface web moderna e API RESTful.

## 🎯 Objetivo

Automatizar o registro de presença dos alunos através de reconhecimento facial em tempo real, integrando com o sistema de gestão acadêmica usado pelos professores.

## 🔬 Tecnologias

**Sistema Híbrido**: face_recognition + DeepFace  
(Combina velocidade do face_recognition com precisão de validação do DeepFace)

---

## 🚀 Sistema Híbrido de Reconhecimento (NOVO!)

O sistema agora utiliza uma **estratégia híbrida inteligente** que combina o melhor dos dois mundos:

### ⚡ Estratégia SMART (Padrão)
1. **Face Recognition primeiro** (rápido - 0.09s)
2. **Alta confiança (>60%)**: Aceita imediatamente
3. **Confiança média (40-60%)**: Valida com DeepFace
4. **Baixa confiança (<40%)**: DeepFace como autoridade
5. **Não encontrou**: DeepFace como fallback

**Resultado:** ~0.3s em média (vs 0.09s só FR ou 1.7s só DF)

### 📊 Modos Disponíveis
- **smart** (Recomendado): Velocidade + precisão balanceada
- **always_both**: Máxima precisão, sempre usa ambos
- **fallback**: Máxima velocidade, DF apenas em falhas

**📖 [Documentação Completa do Sistema Híbrido](HYBRID_SYSTEM.md)**

---

## 📊 Comparação Face Recognition vs DeepFace

Foi realizada uma comparação abrangente entre as bibliotecas **face_recognition** e **DeepFace**.

### 🏆 Vencedor: Face Recognition
- **Precisão: 77.6%** vs DeepFace 54.1%
- **F1 Score: 0.813** vs DeepFace 0.477
- **Velocidade: ~0.09s** vs DeepFace ~1.7s
- Melhor equilíbrio entre precisão e recall

**📂 Estrutura da Comparação:**
- **[📑 Índice & Navegação](tests/comparison_results/INDEX.md)** - Comece por aqui!
- **[📖 Documentação Completa](tests/comparison_results/README.md)** - Análise completa (30+ páginas)
- **[🚀 Guia de Início Rápido](tests/comparison_results/QUICKSTART.md)** - Reproduza o teste
- **[📊 Gráficos](tests/comparison_results/graphics/)** - 6 visualizações profissionais
- **[💾 Dados dos Resultados](tests/comparison_results/data/test_results.json)** - JSON estruturado

**Detalhes do Teste:**
- 429 imagens testadas (30 celebridades conhecidas + 15 desconhecidas)
- Face Recognition: 77.6% de precisão, 208 identificações corretas
- DeepFace: 54.1% de precisão, 90 identificações corretas (perdeu 68.5% dos rostos conhecidos)


---

## 📁 Estrutura do Projeto

```
Integrador/
├── backend/                      # API FastAPI
│   ├── app/
│   │   ├── main.py              # Entry point
│   │   ├── config.py            # Configurações
│   │   ├── models/              # Modelos do banco (SQLAlchemy)
│   │   ├── routers/             # Endpoints REST (alunos, professores, turmas, presencas)
│   │   ├── schemas/             # Pydantic schemas para validação
│   │   └── services/            # Lógica de negócio
│   │       ├── face_service.py           # Face Recognition
│   │       ├── deepface_service.py       # DeepFace
│   │       ├── hybrid_face_service.py    # Sistema Híbrido
│   │       └── db_service.py             # Database operations
│   ├── scripts/                 # Utilitários
│   ├── tests/                   # Testes e datasets
│   └── requirements.txt
│
├── frontend/                    # App React
│   ├── src/
│   │   ├── components/          # Componentes organizados por papel (student, professor, admin)
│   │   ├── pages/               # Páginas principais
│   │   ├── hooks/               # Custom hooks (useWebcam)
│   │   ├── utils/               # Helpers e funções auxiliares
│   │   └── constants/           # Configurações e constantes da API
│   └── package.json
│
├── docs/                        # Documentação MkDocs
└── README.md                    # Este arquivo
```

## 💻 Requisitos

- **Python**: 3.9+
- **Node.js**: 16.0+
- **PostgreSQL**: 13+ (Supabase recomendado)
- **Webcam**: Resolução mínima de 640x480

## 🚀 Instalação Rápida

### Backend

```bash
cd backend
python3 -m venv ../.venv
source ../.venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Configure suas credenciais
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm start
```

### Documentação

```bash
source .venv/bin/activate
mkdocs serve --dev-addr=127.0.0.1:8001
```

Acesse:
- **Backend**: http://localhost:8000 (Docs em /docs)
- **Frontend**: http://localhost:3000
- **Documentação**: http://localhost:8001

