# Documentação do Sistema

Esta documentação foi criada usando [MkDocs](https://www.mkdocs.org/) com o tema [Material](https://squidfunk.github.io/mkdocs-material/).

## Visualizar Documentação

### Desenvolvimento

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Iniciar servidor de documentação
mkdocs serve --dev-addr=127.0.0.1:8001
```

Acesse: http://127.0.0.1:8001

### Build para Produção

```bash
# Gerar site estático
mkdocs build

# Os arquivos estarão em: site/
```

## Estrutura

```
docs/
├── index.md                    # Página inicial
├── visao-geral/
│   ├── introducao.md          # Introdução ao sistema
│   ├── arquitetura.md         # Arquitetura técnica
│   └── tecnologias.md         # Stack tecnológico
├── instalacao/
│   ├── requisitos.md          # Pré-requisitos
│   ├── backend.md             # Setup do backend
│   ├── frontend.md            # Setup do frontend
│   └── banco-de-dados.md      # Configuração do BD
├── funcionalidades/
│   ├── reconhecimento.md      # Reconhecimento facial
│   ├── alunos.md              # Gestão de alunos
│   ├── professores.md         # Gestão de professores
│   ├── turmas.md              # Gestão de turmas
│   └── presencas.md           # Validação de presenças
├── api/
│   ├── endpoints.md           # Visão geral da API
│   ├── alunos.md              # Endpoints de alunos
│   ├── professores.md         # Endpoints de professores
│   ├── turmas.md              # Endpoints de turmas
│   └── presencas.md           # Endpoints de presenças
├── guias/
│   ├── teste-reconhecimento.md # Como testar
│   ├── preprocessamento.md     # Pré-processamento
│   └── sistema-hibrido.md      # Sistema híbrido
└── referencia/
    ├── configuracoes.md       # Configurações
    └── troubleshooting.md     # Solução de problemas
```

## Editar Documentação

1. Edite os arquivos Markdown em `docs/`
2. O servidor irá recarregar automaticamente
3. Visualize as mudanças em tempo real

## Deploy

### GitHub Pages

```bash
mkdocs gh-deploy
```

### Netlify

1. Conecte o repositório
2. Build command: `mkdocs build`
3. Publish directory: `site`

### Vercel

```bash
vercel --prod
```

## Personalização

Edite `mkdocs.yml` para:

- Mudar cores e tema
- Adicionar/remover seções
- Configurar plugins
- Customizar navegação
