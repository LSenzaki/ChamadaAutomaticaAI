"""
db_session.py
-------------

Este módulo é responsável pela **configuração e gerenciamento da conexão com o banco de dados** 
utilizando SQLAlchemy. Ele cria a engine, a sessão de conexão e fornece utilitários para que 
outros módulos possam interagir com o banco de forma segura.

Responsabilidades:
- Definir a `engine` de conexão com o banco (SQLite, PostgreSQL, etc.).
- Criar a `SessionLocal`, que gera sessões independentes para cada request.
- Fornecer a função `get_db()` usada como dependência nos endpoints do FastAPI.
- Garantir abertura e fechamento corretos das conexões com o banco.

"""


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"  # ajuste para seu banco real

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base global para os models herdarem
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

