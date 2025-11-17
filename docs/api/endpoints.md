# Endpoints da API

## Visão Geral

A API RESTful do sistema oferece 21 endpoints organizados em 4 grupos principais:

- **Alunos**: Cadastro, reconhecimento e gestão de estudantes
- **Professores**: Cadastro e gestão de professores
- **Turmas**: Criação e gestão de turmas/classes
- **Presenças**: Validação e consulta de registros de presença

## Base URL

```
http://localhost:8000
```

## Documentação Interativa

Acesse a documentação Swagger em:
```
http://localhost:8000/docs
```

Ou ReDoc em:
```
http://localhost:8000/redoc
```

## Resumo dos Endpoints

### Alunos (`/alunos`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/alunos/` | Listar todos os alunos |
| GET | `/alunos/{id}` | Obter aluno por ID |
| POST | `/alunos/` | Criar novo aluno |
| PUT | `/alunos/{id}` | Atualizar aluno |
| DELETE | `/alunos/{id}` | Deletar aluno |
| POST | `/alunos/registrar` | Registrar aluno com fotos |
| POST | `/alunos/reconhecer` | Reconhecer rosto e registrar presença |
| POST | `/alunos/reconhecer/teste` | Testar reconhecimento sem registrar |
| GET | `/alunos/{id}/presencas/hoje` | Obter presenças do dia |
| DELETE | `/alunos/{id}/embeddings` | Deletar embeddings de um aluno |

### Professores (`/professores`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/professores/` | Listar todos os professores |
| GET | `/professores/{id}` | Obter professor por ID |
| POST | `/professores/` | Criar novo professor |
| PUT | `/professores/{id}` | Atualizar professor |
| DELETE | `/professores/{id}` | Deletar professor |

### Turmas (`/turmas`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/turmas/` | Listar todas as turmas |
| GET | `/turmas/{id}` | Obter turma por ID |
| POST | `/turmas/` | Criar nova turma |
| PUT | `/turmas/{id}` | Atualizar turma |
| DELETE | `/turmas/{id}` | Deletar turma |

### Presenças (`/presencas`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/presencas/` | Listar presenças com filtros |
| GET | `/presencas/hoje` | Obter presenças de hoje |
| GET | `/presencas/{id}` | Obter presença por ID |
| PUT | `/presencas/{id}/validate` | Validar presença |

## Autenticação

Atualmente, a API não requer autenticação. Para produção, recomenda-se implementar:

- **JWT Tokens**: Para autenticação de usuários
- **API Keys**: Para aplicações externas
- **OAuth2**: Para integração com sistemas existentes

## Rate Limiting

Não há rate limiting implementado. Para produção, considere:

- Limitar requisições por IP
- Implementar throttling
- Usar Redis para controle

## CORS

CORS está configurado para aceitar requisições de:
```
http://localhost:3000
```

Para produção, ajuste em `backend/app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://seu-dominio.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Status Codes

| Código | Significado |
|--------|-------------|
| 200 | Sucesso |
| 201 | Criado com sucesso |
| 400 | Requisição inválida |
| 404 | Não encontrado |
| 500 | Erro interno do servidor |

## Exemplos de Uso

### cURL

```bash
# Listar alunos
curl -X GET http://localhost:8000/alunos/

# Criar turma
curl -X POST http://localhost:8000/turmas/ \
  -H "Content-Type: application/json" \
  -d '{"nome": "Python Avançado"}'
```

### JavaScript (Fetch)

```javascript
// Listar professores
const response = await fetch('http://localhost:8000/professores/');
const professores = await response.json();

// Criar professor
const response = await fetch('http://localhost:8000/professores/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    nome: 'Prof. João',
    email: 'joao@escola.com',
    turma_ids: [1, 2]
  })
});
```

### Python (Requests)

```python
import requests

# Listar alunos
response = requests.get('http://localhost:8000/alunos/')
alunos = response.json()

# Reconhecer rosto
with open('foto.jpg', 'rb') as f:
    files = {'foto': f}
    response = requests.post(
        'http://localhost:8000/alunos/reconhecer',
        files=files
    )
    resultado = response.json()
```

## Próximos Passos

- [Endpoints de Alunos](alunos.md)
- [Endpoints de Professores](professores.md)
- [Endpoints de Turmas](turmas.md)
- [Endpoints de Presenças](presencas.md)
