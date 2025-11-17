# Tecnologias Utilizadas

## Backend

### FastAPI
- **Versão**: 0.115.0
- **Descrição**: Framework web moderno e rápido para Python
- **Uso**: Criação da API RESTful

### Python
- **Versão**: 3.9+
- **Bibliotecas Principais**:
  - `face-recognition 1.3.0`: Reconhecimento facial básico
  - `DeepFace 0.0.93`: Reconhecimento facial avançado com redes neurais
  - `Pillow 11.3.0`: Processamento de imagens
  - `OpenCV 4.10.0`: Manipulação de vídeo e imagem
  - `numpy 1.26.4`: Operações matemáticas
  - `supabase 2.14.0`: Cliente do banco de dados

### Supabase (PostgreSQL)
- **Descrição**: Plataforma de banco de dados como serviço
- **Uso**: Armazenamento de dados e embeddings

## Frontend

### React
- **Versão**: 18.x
- **Descrição**: Biblioteca JavaScript para construção de interfaces
- **Uso**: Interface de usuário

### Tailwind CSS
- **Versão**: 3.x
- **Descrição**: Framework CSS utilitário
- **Uso**: Estilização da interface

### Lucide React
- **Descrição**: Biblioteca de ícones
- **Uso**: Ícones da interface

## Reconhecimento Facial

### face_recognition
- **Base**: dlib
- **Modelo**: CNN (Convolutional Neural Network)
- **Encoding**: 128 dimensões
- **Vantagens**: 
  - Rápido
  - Leve
  - Boa precisão

### DeepFace
- **Modelos Disponíveis**:
  - VGG-Face
  - Facenet
  - OpenFace
  - DeepFace
  - ArcFace
- **Encoding**: 512 dimensões (Facenet)
- **Vantagens**:
  - Alta precisão
  - Robusto a variações

## Infraestrutura

### Desenvolvimento
- **Sistema Operacional**: macOS/Linux
- **Python**: Ambiente virtual (venv)
- **Node.js**: Para o frontend React

### Produção (Recomendado)
- **Backend**: Docker + Uvicorn
- **Frontend**: Nginx ou Vercel
- **Banco de Dados**: Supabase (Cloud)

## Ferramentas de Desenvolvimento

- **Git**: Controle de versão
- **VS Code**: IDE recomendada
- **Postman**: Teste de APIs
- **MkDocs**: Documentação

## Requisitos de Sistema

### Mínimo
- **CPU**: 2 cores
- **RAM**: 4GB
- **Disco**: 10GB
- **Python**: 3.9+
- **Node.js**: 16+

### Recomendado
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Disco**: 20GB+
- **GPU**: Opcional (acelera DeepFace)
