"""
db_models.py (Versão Atualizada)
---------------------------------
Modelos de dados para o sistema de chamada.
Utiliza tabelas separadas para Alunos (Student), Embeddings Faciais (FaceEmbedding)
e Registros de Chamada (AttendanceRecord).
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, ARRAY, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.db_session import Base # Importa a Base do SQLAlchemy

# Modelos do ORM (SQLAlchemy)

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True, nullable=True) # ID externo, se houver
    nome = Column(String, index=True, nullable=False)
    is_professor = Column(Boolean, default=False) # Mudado de check_professor para is_professor

    # Relação One-to-Many: Um aluno pode ter vários embeddings (rostos)
    embeddings = relationship("FaceEmbedding", back_populates="student", cascade="all, delete-orphan")
    
    # Relação One-to-Many: Um aluno pode ter vários registros de chamada
    attendance_records = relationship("AttendanceRecord", back_populates="student")

    def __repr__(self):
        return f"<Student(id={self.id}, nome='{self.nome}')>"

class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    
    # ATENÇÃO: Se você usa SQLite, o ARRAY não funciona nativamente.
    # A maneira mais segura é usar String (JSON) ou BLOB, como no seu modelo original.
    # Por enquanto, vou manter String (JSON) para compatibilidade com o modelo anterior.
    # Se você está usando PostgreSQL, pode usar o tipo ARRAY(Float).
    vector = Column(String) # O vetor de 128 floats salvo como String/JSON
    
    student = relationship("Student", back_populates="embeddings")

class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    session_tag = Column(String, nullable=False)
    confidence = Column(Float, nullable=True)
    
    # Coluna de Validação
    check_professor = Column(Boolean, default=False) # <-- ESTE CAMPO É ESSENCIAL
    
    student = relationship("Student", back_populates="attendance_records")