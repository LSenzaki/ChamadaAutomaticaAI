# Configuração do Banco de Dados

## Supabase Setup

### 1. Criar Projeto no Supabase

1. Acesse [supabase.com](https://supabase.com)
2. Faça login ou crie uma conta
3. Clique em "New Project"
4. Preencha:
   - **Name**: nome-do-projeto
   - **Database Password**: senha forte
   - **Region**: escolha a região mais próxima
5. Aguarde a criação do projeto (1-2 minutos)

### 2. Obter Credenciais

No painel do projeto:

1. Vá em **Settings** → **API**
2. Copie:
   - **URL**: `https://seu-projeto.supabase.co`
   - **anon public**: chave pública
   - **service_role**: chave de serviço (mantenha segura!)

### 3. Executar SQL Schema

1. No painel do Supabase, vá em **SQL Editor**
2. Clique em **New query**
3. Cole o conteúdo do arquivo `backend/database_schema.sql`
4. Clique em **Run** ou pressione `Ctrl+Enter`

### 4. Verificar Tabelas Criadas

No **Table Editor**, você deve ver:

- ✅ `turmas` - Classes/Turmas
- ✅ `professores` - Professores
- ✅ `turmas_professores` - Relacionamento Many-to-Many
- ✅ `alunos` - Alunos/Estudantes
- ✅ `face_embeddings` - Embeddings faciais
- ✅ `presencas` - Registros de presença

## Schema do Banco de Dados

### Diagrama ER

```
┌──────────────┐
│   turmas     │
│──────────────│
│ id (PK)      │
│ nome         │
│ created_at   │
│ updated_at   │
└──────┬───────┘
       │
       │ 1:N
       │
┌──────▼───────────────────┐
│   turmas_professores      │
│───────────────────────────│
│ id (PK)                   │
│ turma_id (FK)            │
│ professor_id (FK)        │
│ created_at               │
└──────┬───────────────────┘
       │
       │ N:1
       │
┌──────▼───────┐           ┌──────────────┐
│ professores  │           │   alunos     │
│──────────────│           │──────────────│
│ id (PK)      │           │ id (PK)      │
│ nome         │           │ nome         │
│ email        │◄──────────┤ turma_id(FK) │
│ ativo        │  valida   │ check_prof   │
│ created_at   │           │ ativo        │
└──────────────┘           └──────┬───────┘
                                  │
                        ┌─────────┼─────────┐
                        │                   │
                        │ 1:N               │ 1:N
                        │                   │
               ┌────────▼─────────┐ ┌──────▼────────┐
               │ face_embeddings  │ │  presencas    │
               │──────────────────│ │───────────────│
               │ id (PK)          │ │ id (PK)       │
               │ aluno_id (FK)    │ │ aluno_id (FK) │
               │ embedding        │ │ turma_id (FK) │
               │ foto_nome        │ │ data_hora     │
               │ created_at       │ │ confianca     │
               └──────────────────┘ │ check_prof    │
                                    │ validado_em   │
                                    │ validado_por  │
                                    └───────────────┘
```

### Tabelas Detalhadas

#### turmas
```sql
CREATE TABLE turmas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### professores
```sql
CREATE TABLE professores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### alunos
```sql
CREATE TABLE alunos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    turma_id INTEGER REFERENCES turmas(id) ON DELETE SET NULL,
    check_professor BOOLEAN DEFAULT FALSE,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### face_embeddings
```sql
CREATE TABLE face_embeddings (
    id SERIAL PRIMARY KEY,
    aluno_id INTEGER NOT NULL REFERENCES alunos(id) ON DELETE CASCADE,
    embedding BYTEA NOT NULL,
    foto_nome VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### presencas
```sql
CREATE TABLE presencas (
    id SERIAL PRIMARY KEY,
    aluno_id INTEGER NOT NULL REFERENCES alunos(id) ON DELETE CASCADE,
    turma_id INTEGER REFERENCES turmas(id) ON DELETE SET NULL,
    data_hora TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    confianca NUMERIC(5,2) CHECK (confianca >= 0 AND confianca <= 100),
    check_professor BOOLEAN DEFAULT FALSE,
    validado_em TIMESTAMP WITH TIME ZONE,
    validado_por INTEGER REFERENCES professores(id) ON DELETE SET NULL,
    observacao TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Dados de Exemplo

O schema já inclui dados de exemplo:

```sql
-- Turmas
INSERT INTO turmas (nome) VALUES 
    ('IA 1º Ano'),
    ('Data Science 3º Ano'),
    ('Machine Learning 2º Ano');

-- Professores
INSERT INTO professores (nome, email) VALUES 
    ('Prof. Maria Santos', 'maria.santos@escola.com'),
    ('Prof. João Silva', 'joao.silva@escola.com');
```

## Backup e Restore

### Backup

```bash
# Via Supabase Dashboard
# Settings → Database → Database Backups

# Ou via pg_dump (se tiver acesso direto)
pg_dump -h db.seu-projeto.supabase.co -U postgres -d postgres > backup.sql
```

### Restore

```bash
psql -h db.seu-projeto.supabase.co -U postgres -d postgres < backup.sql
```

## Troubleshooting

### Erro: "Could not find the 'xxx' column"

**Solução**: Re-executar o schema
1. Deletar todas as tabelas
2. Executar `database_schema.sql` novamente

### Erro: "Permission denied"

**Solução**: Verificar RLS (Row Level Security)
1. Vá em **Table Editor**
2. Selecione a tabela
3. Desabilite RLS temporariamente (apenas desenvolvimento)

### Conexão lenta

**Solução**: Verificar região do projeto
- Escolher região mais próxima geograficamente
- Considerar upgrade do plano Supabase

## Próximos Passos

1. [Testar Conexão Backend](backend.md)
2. [Iniciar Servidores](backend.md)
3. [Explorar API](../api/endpoints.md)
