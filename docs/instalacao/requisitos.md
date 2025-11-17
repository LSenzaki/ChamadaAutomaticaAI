# Requisitos do Sistema

## Requisitos de Hardware

### Mínimo
- **Processador**: Intel Core i3 ou equivalente (2 cores)
- **Memória RAM**: 4GB
- **Espaço em Disco**: 10GB disponíveis
- **Webcam**: Necessária para captura de imagens

### Recomendado
- **Processador**: Intel Core i5 ou superior (4+ cores)
- **Memória RAM**: 8GB ou mais
- **Espaço em Disco**: 20GB+ disponíveis
- **GPU**: Opcional, mas acelera o processamento do DeepFace
- **Webcam**: Full HD (1080p) para melhor qualidade

## Requisitos de Software

### Sistema Operacional
- **macOS**: 10.14 (Mojave) ou superior
- **Linux**: Ubuntu 18.04+ ou similar
- **Windows**: 10/11 (com WSL2 recomendado para melhor compatibilidade)

### Python
- **Versão**: 3.9, 3.10 ou 3.11
- **Virtual Environment**: venv ou conda

### Node.js
- **Versão**: 16.x ou superior
- **npm**: 8.x ou superior

### Banco de Dados
- **Supabase**: Conta gratuita ou paga
- **PostgreSQL**: 14+ (se usar localmente)

## Dependências do Sistema

### macOS
```bash
# Instalar Homebrew (se não tiver)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar dependências
brew install cmake
brew install python@3.9
brew install node
```

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y python3.9 python3.9-venv python3-pip
sudo apt-get install -y nodejs npm
sudo apt-get install -y cmake build-essential
sudo apt-get install -y libopencv-dev
```

### Windows (WSL2)
```bash
# Instalar Python
sudo apt-get install python3.9 python3.9-venv python3-pip

# Instalar Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt-get install -y nodejs

# Instalar dependências de compilação
sudo apt-get install cmake build-essential
```

## Verificação dos Requisitos

### Verificar Python
```bash
python3 --version
# Deve mostrar: Python 3.9.x ou superior
```

### Verificar Node.js
```bash
node --version
# Deve mostrar: v16.x.x ou superior

npm --version
# Deve mostrar: 8.x.x ou superior
```

### Verificar pip
```bash
pip3 --version
# Deve mostrar a versão do pip
```

## Conta Supabase

1. Acesse [supabase.com](https://supabase.com)
2. Crie uma conta gratuita
3. Crie um novo projeto
4. Anote:
   - URL do projeto
   - Chave de API (anon key)
   - Chave de serviço (service role key)

## Próximos Passos

Após verificar que todos os requisitos estão atendidos:

1. [Instalar Backend](backend.md)
2. [Instalar Frontend](frontend.md)
3. [Configurar Banco de Dados](banco-de-dados.md)
