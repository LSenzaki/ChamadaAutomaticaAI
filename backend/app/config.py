from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Obter o caminho para o diretório raiz do projeto (um nível acima de 'app/config.py')
# Isso garante que o Python encontre o .env, independentemente do CWD do uvicorn.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Carregamento explícito do .env ---
# Força a leitura do arquivo .env usando o caminho absoluto.
dotenv_path = BASE_DIR / ".env"
print(f"DEBUG: Tentando carregar .env de: {dotenv_path}")
load_success = load_dotenv(dotenv_path)
print(f"DEBUG: Carregamento do .env {'BEM SUCEDIDO' if load_success else 'FALHOU'}. Verifique se o arquivo existe e se as chaves estão corretas.")

# --- Definição das Configurações ---
class Settings(BaseSettings):
    # Campos Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # Campos da Aplicação
    APP_NAME: str = "Chamada Facial API"
    APP_VERSION: str = "1.0.0"
    SIMILARITY_THRESHOLD: float = 0.6  # Limiar de confiança (0.0 a 1.0)
    
    # Configuração Pydantic (Permite que o Pydantic leia .env, mas forçamos
    # o carregamento acima para garantir a ordem)
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file_encoding='utf-8',
        extra='ignore' # Ignora variáveis de ambiente não declaradas
    )

# Inicializa as configurações
settings = Settings()
