# Estrutura do Projeto - Guia Completo

Este documento descreve a organização completa do projeto Sistema de Reconhecimento Facial.

## 📂 Visão Geral da Estrutura

```
Integrador/
├── 📄 Arquivos de Configuração Raiz
├── 🐍 backend/           # API FastAPI + Serviços de IA
├── ⚛️  frontend/          # Aplicação React
├── 📚 docs/              # Documentação MkDocs
└── 🔧 Scripts e Utilitários
```

## 📄 Arquivos Raiz

```
/
├── README.md              # Documentação principal do projeto
├── CONTRIBUTING.md        # Guia de contribuição
├── LICENSE                # Licença MIT
├── .gitignore            # Arquivos ignorados pelo Git
├── .editorconfig         # Configuração de editor universal
├── Makefile              # Comandos de automação
└── mkdocs.yml            # Configuração da documentação
```

### Propósito dos Arquivos

- **README.md**: Ponto de entrada, instalação, uso básico
- **CONTRIBUTING.md**: Padrões de código, processo de PR, convenções
- **LICENSE**: Termos de uso (MIT)
- **.editorconfig**: Mantém consistência de formatação entre editores
- **Makefile**: Automação de tarefas comuns (install, run, test)
- **mkdocs.yml**: Configuração do site de documentação

## 🐍 Backend (`/backend`)

```
backend/
├── app/                   # Código principal da aplicação
│   ├── __init__.py
│   ├── main.py           # 🚀 Entry point FastAPI
│   ├── config.py         # ⚙️ Configurações e variáveis de ambiente
│   │
│   ├── models/           # 🗄️ Modelos de Banco de Dados
│   │   ├── __init__.py
│   │   ├── db_models.py      # SQLAlchemy models (Aluno, Professor, Turma, Presenca)
│   │   ├── db_session.py     # Session factory e engine
│   │   └── response.py       # Modelos de resposta HTTP
│   │
│   ├── routers/          # 🛣️ Endpoints REST API
│   │   ├── __init__.py
│   │   ├── alunos.py         # CRUD de alunos + registro facial
│   │   ├── professores.py    # CRUD de professores
│   │   ├── turmas.py         # CRUD de turmas
│   │   └── presencas.py      # Gestão de presenças + validação
│   │
│   ├── schemas/          # 📋 Validação de Dados (Pydantic)
│   │   ├── __init__.py
│   │   ├── pydantic_schemas.py   # Schemas gerais
│   │   └── student_schema.py     # Schemas específicos de alunos
│   │
│   └── services/         # 🧠 Lógica de Negócio e IA
│       ├── __init__.py
│       ├── face_service.py       # Face Recognition (rápido)
│       ├── deepface_service.py   # DeepFace (preciso)
│       ├── hybrid_face_service.py # Sistema híbrido inteligente
│       ├── comparison_service.py  # Comparação de bibliotecas
│       └── db_service.py         # Operações de banco de dados
│
├── scripts/              # 🔧 Utilitários e Manutenção
│   ├── test_connection.py        # Testa conexão com Supabase
│   ├── fix_embeddings.py         # Corrige embeddings inválidos
│   └── delete_bad_embeddings.py  # Remove embeddings corrompidos
│
├── tests/                # 🧪 Testes e Datasets
│   ├── README.md
│   ├── test_celebrity_blind.py          # Teste cego com celebridades
│   ├── generate_comparison_graphics.py  # Gera gráficos de comparação
│   ├── resize_celebrity_dataset.py      # Preprocessa dataset
│   ├── celebrity_dataset/               # 429 imagens de 45 celebridades
│   ├── comparison_results/              # Resultados e gráficos
│   └── test_dataset/                    # Outros datasets de teste
│
├── migrations/           # 🗃️ Migrações do Banco (Alembic)
├── requirements.txt      # 📦 Dependências Python
├── .env                  # 🔐 Variáveis de ambiente (não versionado)
├── .gitignore
└── database_schema.sql   # 🗄️ Schema completo do PostgreSQL
```

### Detalhamento dos Módulos

#### `app/main.py` - Entry Point
- Inicializa aplicação FastAPI
- Registra routers
- Configura CORS
- Define middleware

#### `app/config.py` - Configurações
- Carrega variáveis de ambiente (.env)
- Configurações de banco de dados
- Parâmetros de reconhecimento facial
- URLs e credenciais

#### `app/models/` - Camada de Dados
- **db_models.py**: Define tabelas (Aluno, Professor, Turma, Presenca, TurmasProfessores, TurmasAlunos)
- **db_session.py**: Gerencia conexões com PostgreSQL/Supabase
- **response.py**: Padroniza respostas HTTP

#### `app/routers/` - API REST
Cada router define endpoints RESTful para um recurso:

**alunos.py**:
```
GET    /alunos/              - Lista todos os alunos
POST   /alunos/              - Cria novo aluno
GET    /alunos/{id}          - Busca aluno por ID
PUT    /alunos/{id}          - Atualiza aluno
DELETE /alunos/{id}          - Remove aluno
POST   /alunos/registrar     - Registra face do aluno (foto)
POST   /alunos/reconhecer    - Reconhece aluno (webcam stream)
```

**professores.py**:
```
GET    /professores/         - Lista professores
POST   /professores/         - Cria professor
GET    /professores/{id}     - Busca professor
PUT    /professores/{id}     - Atualiza professor
DELETE /professores/{id}     - Remove professor
```

**turmas.py**:
```
GET    /turmas/              - Lista turmas
POST   /turmas/              - Cria turma
GET    /turmas/{id}          - Busca turma
PUT    /turmas/{id}          - Atualiza turma
DELETE /turmas/{id}          - Remove turma
GET    /turmas/{id}/alunos   - Lista alunos da turma
```

**presencas.py**:
```
GET    /presencas/           - Lista presenças
POST   /presencas/           - Registra presença
GET    /presencas/hoje       - Presenças do dia (para validação)
GET    /presencas/turma/{id} - Presenças por turma
DELETE /presencas/{id}       - Remove presença
```

#### `app/schemas/` - Validação
Define contratos de entrada/saída usando Pydantic:
- Validação automática de tipos
- Conversão de dados
- Documentação automática no Swagger

#### `app/services/` - Lógica de Negócio

**face_service.py**: Face Recognition Library
- Encoding facial rápido (~0.09s)
- Preprocessamento de imagens (300x300px)
- Threshold: 0.55 (otimizado)

**deepface_service.py**: DeepFace Library
- Encoding preciso (~1.7s)
- Modelos: VGG-Face, Facenet, etc.
- Backup para casos difíceis

**hybrid_face_service.py**: Sistema Híbrido Inteligente
- Estratégia SMART (padrão)
- Confiança alta (>55%): aceita direto
- Confiança média (35-55%): valida com DeepFace
- Performance média: ~0.3s

**db_service.py**: Database Operations
- CRUD genérico
- Consultas otimizadas
- Transações seguras

## ⚛️ Frontend (`/frontend`)

```
frontend/
├── public/               # Arquivos estáticos
│   ├── index.html
│   ├── manifest.json
│   └── robots.txt
│
├── src/
│   ├── components/       # 🧩 Componentes Reutilizáveis
│   │   ├── student/      # Componentes do Aluno
│   │   │   ├── SelecionarTurma.jsx
│   │   │   ├── TelaReconhecimento.jsx
│   │   │   └── index.js
│   │   │
│   │   ├── professor/    # Componentes do Professor
│   │   │   ├── ProfessorMenu.jsx
│   │   │   ├── ValidarAlunos.jsx
│   │   │   ├── ValidarPresencas.jsx
│   │   │   └── index.js
│   │   │
│   │   ├── admin/        # Componentes do Admin
│   │   │   ├── AdminMenu.jsx
│   │   │   ├── RegistrarAluno.jsx
│   │   │   ├── RegistrarProfessor.jsx
│   │   │   ├── CriarTurmas.jsx
│   │   │   ├── GerenciarAlunos.jsx
│   │   │   └── index.js
│   │   │
│   │   └── common/       # Componentes Compartilhados
│   │       ├── Button.jsx
│   │       ├── Input.jsx
│   │       ├── Modal.jsx
│   │       └── index.js
│   │
│   ├── pages/            # 📄 Páginas Principais
│   │   ├── AlunoScreen.jsx
│   │   ├── ProfessorScreen.jsx
│   │   ├── AdminScreen.jsx
│   │   └── index.js
│   │
│   ├── hooks/            # 🪝 Custom Hooks
│   │   ├── useWebcam.js       # Gerencia webcam (start/stop)
│   │   ├── useFetch.js        # Wrapper para fetch API
│   │   └── index.js
│   │
│   ├── utils/            # 🔧 Funções Auxiliares
│   │   ├── helpers.js         # Funções gerais
│   │   ├── imageProcessing.js # Manipulação de imagens
│   │   ├── dateUtils.js       # Formatação de datas
│   │   └── index.js
│   │
│   ├── constants/        # 📌 Constantes e Configurações
│   │   ├── api.js            # URLs e endpoints
│   │   ├── config.js         # Configurações globais
│   │   └── index.js
│   │
│   ├── App.js            # 🎯 Componente Principal
│   ├── App.css           # Estilos do App
│   ├── index.js          # 🚀 Entry Point React
│   ├── index.css         # Estilos globais + Tailwind
│   └── setupTests.js     # Configuração de testes
│
├── package.json          # Dependências e scripts
├── tailwind.config.js    # Configuração Tailwind CSS
├── postcss.config.js     # PostCSS para Tailwind
└── .gitignore
```

### Arquitetura Frontend

#### Hierarquia de Componentes

```
App
├── AlunoScreen
│   ├── SelecionarTurma
│   └── TelaReconhecimento (com useWebcam)
│
├── ProfessorScreen
│   ├── ProfessorMenu
│   ├── ValidarAlunos
│   └── ValidarPresencas
│
└── AdminScreen
    ├── AdminMenu
    ├── RegistrarAluno (com useWebcam)
    ├── RegistrarProfessor
    ├── CriarTurmas
    ├── ListarTurmasAlunos
    └── GerenciarAlunos
```

#### Fluxo de Dados

```
User Interaction → Component State → API Call (fetch) → Backend → Database
                                   ↓
                            Update Component State → Re-render
```

#### Padrões Utilizados

- **Componentes Funcionais**: Sem classes, apenas hooks
- **Custom Hooks**: Lógica reutilizável (useWebcam, useFetch)
- **Composition**: Componentes pequenos e componíveis
- **Props Drilling**: Evitado com composição adequada
- **Styled Components**: Tailwind CSS utility-first

## 📚 Documentação (`/docs`)

```
docs/
├── index.md              # Homepage da documentação
├── README.md             # Guia de manutenção da docs
│
├── visao-geral/          # Visão Geral do Sistema
│   ├── introducao.md
│   ├── arquitetura.md
│   └── tecnologias.md
│
├── instalacao/           # Guias de Instalação
│   ├── requisitos.md
│   ├── backend.md
│   ├── frontend.md
│   └── banco-de-dados.md
│
├── funcionalidades/      # Funcionalidades Detalhadas
│   ├── reconhecimento.md
│   ├── alunos.md
│   ├── professores.md
│   ├── turmas.md
│   └── presencas.md
│
├── api/                  # Referência da API
│   ├── endpoints.md
│   ├── alunos.md
│   ├── professores.md
│   ├── turmas.md
│   └── presencas.md
│
├── guias/                # Guias de Desenvolvimento
│   ├── teste-reconhecimento.md
│   ├── preprocessamento.md
│   ├── sistema-hibrido.md
│   ├── IMAGE_PREPROCESSING.md
│   └── TESTING_GUIDE.md
│
└── referencia/           # Referências Técnicas
    ├── configuracoes.md
    ├── troubleshooting.md
    ├── DATABASE_SETUP.md
    ├── HYBRID_SYSTEM.md
    ├── MIGRATION_GUIDE.md
    ├── INTEGRATION_STATUS.md
    └── SUMMARY.md
```

## 🔄 Fluxo de Trabalho

### Desenvolvimento Local

1. **Backend**: `make run-backend` → http://localhost:8000
2. **Frontend**: `make run-frontend` → http://localhost:3000
3. **Docs**: `make run-docs` → http://localhost:8001

### Ciclo de Desenvolvimento

```
1. Feature Branch: git checkout -b feature/nova-funcionalidade
2. Desenvolvimento: Codificar + Testar localmente
3. Commit: git commit -m "feat: adiciona nova funcionalidade"
4. Push: git push origin feature/nova-funcionalidade
5. Pull Request: Criar PR para branch Develop
6. Review: Code review + Testes automáticos
7. Merge: Merge para Develop
8. Deploy: Release para main quando estável
```

## 📦 Dependências Principais

### Backend
- **FastAPI**: Framework web moderno
- **SQLAlchemy**: ORM para PostgreSQL
- **face_recognition**: Reconhecimento facial rápido
- **DeepFace**: Reconhecimento facial preciso
- **Pillow**: Manipulação de imagens
- **python-multipart**: Upload de arquivos

### Frontend
- **React**: Library UI
- **Tailwind CSS**: Utility-first CSS
- **Lucide React**: Ícones
- **React Webcam**: Acesso à webcam

### Documentação
- **MkDocs**: Gerador de sites estáticos
- **Material for MkDocs**: Tema profissional

## 🎯 Boas Práticas

### Organização de Código

1. **Separação de Responsabilidades**: Cada arquivo tem um propósito claro
2. **DRY (Don't Repeat Yourself)**: Código reutilizável em utils/hooks
3. **Nomenclatura Consistente**: snake_case (Python), camelCase (JS)
4. **Documentação**: Docstrings e JSDoc em funções públicas
5. **Type Safety**: Type hints em Python, PropTypes/JSDoc em React

### Estrutura de Arquivos

- **Um componente por arquivo** (frontend)
- **Um router por recurso** (backend)
- **Índice de exportação** (index.js/py para fácil import)
- **Testes próximos ao código** (co-located tests)

### Commits e Versionamento

- **Conventional Commits**: feat, fix, docs, refactor, test
- **Branches descritivas**: feature/, fix/, refactor/
- **PRs pequenos**: Mudanças incrementais e revisáveis

## 🚀 Próximos Passos

### Melhorias Planejadas

1. **TypeScript no Frontend**: Type safety completo
2. **Docker Compose**: Containerização completa
3. **CI/CD**: GitHub Actions para testes e deploy
4. **Autenticação**: JWT e controle de acesso
5. **WebSocket**: Notificações em tempo real
6. **Mobile**: React Native ou PWA

### Refatorações Futuras

- Extrair componentes restantes de App.js
- Adicionar Context API para estado global
- Implementar testes E2E com Playwright
- Adicionar Storybook para componentes

---

**Última atualização**: 16 de novembro de 2025  
**Versão**: 2.0.0  
**Mantenedor**: Lucas Senzaki
