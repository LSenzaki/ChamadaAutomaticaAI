# Instalação do Frontend

## 1. Navegar para o Diretório

```bash
cd frontend
```

## 2. Instalar Dependências

```bash
npm install
```

### Dependências Principais

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "lucide-react": "^0.263.1",
    "tailwindcss": "^3.3.0"
  }
}
```

## 3. Configurar API URL

Verifique o arquivo `src/App.js`:

```javascript
const API_URL = 'http://localhost:8000';
```

Se o backend estiver em outro endereço, altere conforme necessário.

## 4. Iniciar o Servidor de Desenvolvimento

```bash
npm start
```

O frontend será iniciado em:
```
http://localhost:3000
```

### Opções Disponíveis

```bash
# Desenvolvimento
npm start

# Build para produção
npm run build

# Rodar testes
npm test

# Ejetar configuração (não recomendado)
npm run eject
```

## 5. Verificar Instalação

1. Acesse `http://localhost:3000`
2. Deve aparecer a tela de seleção de perfil:
   - Aluno
   - Professor
   - Admin

## Estrutura de Diretórios

```
frontend/
├── public/
│   ├── index.html
│   ├── manifest.json
│   └── robots.txt
├── src/
│   ├── App.js              # Componente principal
│   ├── App.css             # Estilos principais
│   ├── index.js            # Entry point
│   ├── index.css           # Estilos globais
│   └── setupTests.js       # Configuração de testes
├── package.json            # Dependências e scripts
├── tailwind.config.js      # Configuração do Tailwind
└── postcss.config.js       # Configuração do PostCSS
```

## Configuração do Tailwind CSS

O Tailwind já está configurado. Arquivo `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

## Build para Produção

### 1. Criar Build

```bash
npm run build
```

### 2. Testar Build Localmente

```bash
# Instalar servidor estático (se não tiver)
npm install -g serve

# Servir build
serve -s build -p 3000
```

### 3. Deploy

#### Vercel (Recomendado)
```bash
# Instalar Vercel CLI
npm install -g vercel

# Deploy
vercel
```

#### Netlify
```bash
# Instalar Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod
```

#### Nginx
```nginx
server {
    listen 80;
    server_name seu-dominio.com;
    
    root /caminho/para/frontend/build;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

## Troubleshooting

### Erro: "npm ERR! code ELIFECYCLE"

**Solução**: Limpar cache e reinstalar

```bash
rm -rf node_modules package-lock.json
npm install
```

### Erro: "Port 3000 is already in use"

**Solução**: Usar outra porta

```bash
PORT=3001 npm start
```

Ou no Windows:
```bash
set PORT=3001 && npm start
```

### Erro: "Failed to compile"

**Solução**: Verificar erros de sintaxe no console

- Geralmente indica erro de JavaScript/JSX
- Verificar import/export statements
- Verificar sintaxe do componente

### CORS Error ao chamar API

**Solução**: Verificar configuração CORS no backend

Em `backend/app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Próximos Passos

1. [Configurar Banco de Dados](banco-de-dados.md)
2. [Testar Sistema Completo](../guias/teste-reconhecimento.md)
3. [Explorar Funcionalidades](../funcionalidades/reconhecimento.md)
