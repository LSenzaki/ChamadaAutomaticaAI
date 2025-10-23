"""
db_services.py
--------------

Este módulo contém as funções responsáveis por **interagir diretamente com o banco de dados**
através da sessão do SQLAlchemy. Ele atua como a camada de serviços (CRUD), separando a lógica
de manipulação de dados da lógica de roteamento (FastAPI).

Responsável por:
- Criar, ler, atualizar e excluir registros no banco de dados (operações CRUD).
- Encapsular a lógica de consultas SQLAlchemy para manter os routers mais limpos.
- Fornecer funções reutilizáveis que podem ser chamadas em diferentes partes da aplicação.


"""

import os
from dataclasses import dataclass
from typing import Iterable, List, Optional
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import selectinload 
from app.models.db_models import Base, Student, FaceEmbedding, AttendanceRecord

@dataclass
class Settings:
    DATABASE_URL: str
    FACE_TOLERANCE: float = 0.6
    TEACHERS_WEBHOOK_URL: Optional[str] = None

    @staticmethod
    def from_env():
        return Settings(
            DATABASE_URL=os.getenv("DATABASE_URL", "sqlite:///./data/app.db"),
            FACE_TOLERANCE=float(os.getenv("FACE_TOLERANCE", "0.6")),
            TEACHERS_WEBHOOK_URL=os.getenv("TEACHERS_WEBHOOK_URL"),
        )

class Database:
    def __init__(self, settings: Settings):
        connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
        self.engine = create_engine(settings.DATABASE_URL, echo=False, future=True, connect_args=connect_args)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(self.engine, expire_on_commit=False, future=True)

    # --- Students
    def create_student(self, external_id: str, nome: str) -> Student: # Corrigi o nome do parâmetro da função
        with self.SessionLocal() as s, s.begin():
            st = Student(external_id=external_id, nome=nome) # 👈 Corrigi o nome do argumento do construtor
            s.add(st)
            s.flush()
        return st

    def get_student(self, student_id: int) -> Optional[Student]:
        with self.SessionLocal() as s:
            return s.get(Student, student_id)

    def get_student_by_external(self, external_id: str) -> Optional[Student]:
        with self.SessionLocal() as s:
            return s.execute(select(Student).where(Student.external_id == external_id)).scalar_one_or_none()

    def list_students(self) -> List[Student]:
        with self.SessionLocal() as s:
            return list(s.execute(select(Student)).scalars())

    # --- Embeddings
    def add_embedding(self, student_id: int, vector_json: str) -> int: # A função agora espera uma string
        """ Adiciona um único embedding facial (vetor JSON string) """
        with self.SessionLocal() as s, s.begin():
        # Salva a string JSON diretamente na coluna 'vector'
            s.add(FaceEmbedding(student_id=student_id, vector=vector_json))
            return 1 # Retorna 1 embedding adicionado

    def load_all_embeddings(self) -> List[FaceEmbedding]:
        """ Carrega todos os embeddings, incluindo os dados do aluno (JOIN). """
        with self.SessionLocal() as s:
            # Usa selectinload para carregar os detalhes do aluno junto com o embedding
            stmt = select(FaceEmbedding).options(selectinload(FaceEmbedding.student))
            # Retorna lista de objetos FaceEmbedding, cada um com .student preenchido
            return list(s.execute(stmt).scalars())

    # --- Attendance
    def create_attendance(self, student_id: int, session_tag: str, confidence: float) -> AttendanceRecord:
        with self.SessionLocal() as s, s.begin():
            rec = AttendanceRecord(student_id=student_id, session_tag=session_tag, confidence=confidence)
            s.add(rec)
            s.flush() # Garante que o ID seja gerado ANTES do commit
            s.commit() # Força o commit dentro do Context Manager
            s.refresh(rec) # Garante que o objeto tenha o ID e seja recarregado
            return rec

    def list_attendance_for_student(self, student_id: int) -> List[AttendanceRecord]:
        with self.SessionLocal() as s:
            return list(s.execute(select(AttendanceRecord).where(AttendanceRecord.student_id == student_id)).scalars())
    
    def list_all_attendance(self) -> List[AttendanceRecord]:
        """ Retorna todos os registros de chamada, incluindo os dados do aluno. """
        with self.SessionLocal() as s:
            # Carrega AttendanceRecord e faz JOIN para incluir os dados do Student
            stmt = select(AttendanceRecord).options(selectinload(AttendanceRecord.student))
            return list(s.execute(stmt).scalars())