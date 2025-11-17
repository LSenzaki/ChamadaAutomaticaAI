# Instalação do Backend

## 1. Clonar o Repositório

```bash
git clone <url-do-repositorio>
cd Integrador
```

## 2. Criar Ambiente Virtual

```bash
# Criar ambiente virtual
python3 -m venv .venv

# Ativar ambiente virtual
# No macOS/Linux:
source .venv/bin/activate

# No Windows:
.venv\Scripts\activate
```

## 3. Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

### Dependências Principais

```txt
fastapi==0.115.0
uvicorn==0.34.0
supabase==2.14.0
face-recognition==1.3.0
deepface==0.0.93
pillow==11.3.0
opencv-python==4.10.0.84
numpy==1.26.4
pydantic==2.11.1
```

## 4. Configurar Variáveis de Ambiente

Crie um arquivo `.env` no diretório `backend`:

```bash
cd backend
nano .env
```

Adicione as seguintes variáveis:

```env
# Supabase Configuration
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-anon
SUPABASE_SERVICE_KEY=sua-service-role-key

# Server Configuration (opcional)
HOST=0.0.0.0
PORT=8000
```

## 5. Testar Conexão com Banco

```bash
python test_connection.py
```

Deve exibir:
```
✅ Conexão com Supabase estabelecida com sucesso!
```

## 6. Iniciar o Servidor

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Opções do Comando

- `--reload`: Recarrega automaticamente ao detectar mudanças
- `--host 0.0.0.0`: Permite acesso externo
- `--port 8000`: Define a porta do servidor

## 7. Verificar Instalação

Acesse no navegador:
```
http://localhost:8000/docs
```

Deve abrir a documentação interativa do Swagger.

## Estrutura de Diretórios

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicação principal
│   ├── config.py            # Configurações
│   ├── models/              # Modelos de dados
│   │   ├── db_models.py
│   │   └── response.py
│   ├── routers/             # Endpoints da API
│   │   ├── alunos.py
│   │   ├── professores.py
│   │   ├── turmas.py
│   │   └── presencas.py
│   ├── schemas/             # Schemas Pydantic
│   │   └── pydantic_schemas.py
│   └── services/            # Lógica de negócio
│       ├── db_service.py
│       ├── face_service.py
│       ├── deepface_service.py
│       └── hybrid_face_service.py
├── .env                     # Variáveis de ambiente
├── requirements.txt         # Dependências Python
└── test_connection.py       # Teste de conexão
```

## Troubleshooting

### Erro: "No module named 'face_recognition'"

**Solução**: Instalar dependências do sistema

**macOS**:
```bash
brew install cmake
pip install face-recognition
```

**Ubuntu**:
```bash
sudo apt-get install cmake build-essential
pip install face-recognition
```

### Erro: "Connection refused" ao acessar Supabase

**Solução**: Verificar credenciais no `.env`
- URL deve começar com `https://`
- Keys devem estar corretas
- Projeto Supabase deve estar ativo

### Erro: "Port 8000 already in use"

**Solução**: Mudar a porta ou matar o processo

```bash
# Encontrar processo na porta 8000
lsof -ti:8000

# Matar processo
kill -9 $(lsof -ti:8000)

# Ou usar outra porta
python -m uvicorn app.main:app --reload --port 8001
```

## Próximos Passos

1. [Configurar Banco de Dados](banco-de-dados.md)
2. [Instalar Frontend](frontend.md)
3. [Testar API](../api/endpoints.md)
