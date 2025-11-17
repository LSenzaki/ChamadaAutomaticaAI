# Arquitetura do Sistema

## Visão Geral

O sistema segue uma arquitetura cliente-servidor moderna, separando claramente frontend, backend e banco de dados.

```
┌─────────────────┐
│   Frontend      │  React + Tailwind CSS
│   (Port 3000)   │  Interface de Usuário
└────────┬────────┘
         │ HTTP/REST
         │
┌────────▼────────┐
│   Backend       │  FastAPI + Python
│   (Port 8000)   │  Lógica de Negócio
└────────┬────────┘
         │
    ┌────┴────┬──────────────┐
    │         │              │
┌───▼───┐ ┌──▼──────┐ ┌────▼─────────┐
│ Banco │ │ Face    │ │  DeepFace    │
│ Dados │ │ Recog.  │ │  (ML Model)  │
└───────┘ └─────────┘ └──────────────┘
Supabase   Biblioteca  Rede Neural
```

## Componentes Principais

### Frontend (React)
- **Tecnologia**: React 18 + Tailwind CSS
- **Porta**: 3000
- **Responsabilidades**:
  - Interface de usuário
  - Captura de vídeo/foto
  - Comunicação com API

### Backend (FastAPI)
- **Tecnologia**: FastAPI + Python 3.9
- **Porta**: 8000
- **Responsabilidades**:
  - API RESTful
  - Reconhecimento facial
  - Lógica de negócio
  - Gerenciamento de dados

### Banco de Dados (Supabase)
- **Tecnologia**: PostgreSQL (Supabase)
- **Responsabilidades**:
  - Armazenamento de dados
  - Embeddings faciais
  - Relacionamentos entre entidades

## Fluxo de Reconhecimento Facial

```
1. Frontend captura foto
         ↓
2. Envia para Backend (/alunos/reconhecer)
         ↓
3. Backend preprocessa imagem (300x300px)
         ↓
4. Sistema Híbrido:
   ├─ face_recognition (rápido)
   └─ DeepFace (validação se necessário)
         ↓
5. Busca no banco de dados
         ↓
6. Registra presença
         ↓
7. Retorna resultado ao Frontend
```

## Camadas da Aplicação

### Backend

#### 1. Routers (API Endpoints)
- `alunos.py`: Endpoints de alunos e reconhecimento
- `professores.py`: Gestão de professores
- `turmas.py`: Gestão de turmas
- `presencas.py`: Validação de presenças

#### 2. Services (Lógica de Negócio)
- `face_service.py`: Reconhecimento facial básico
- `deepface_service.py`: Reconhecimento com DeepFace
- `hybrid_face_service.py`: Sistema híbrido inteligente
- `db_service.py`: Operações de banco de dados

#### 3. Models (Dados)
- `db_models.py`: Modelos do banco de dados
- `pydantic_schemas.py`: Validação de dados

### Frontend

#### 1. Componentes
- `AlunoScreen`: Tela de reconhecimento
- `ProfessorScreen`: Validação de presenças
- `AdminScreen`: Gestão do sistema

#### 2. Features
- Captura de vídeo/foto
- Seleção de turma
- Validação de presença
- Gestão de cadastros

## Segurança

- ✅ CORS configurado
- ✅ Validação de dados com Pydantic
- ✅ Embeddings criptografados
- ✅ Conexão segura com banco de dados
