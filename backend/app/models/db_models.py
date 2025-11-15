"""
db_models.py (Updated for Supabase Schema)
-------------------------------------------
Data models for the facial recognition attendance system.
Matches the PostgreSQL schema created in database_schema.sql
"""

from sqlalchemy import (
    Column, Integer, String, Boolean, ForeignKey,
    Float, LargeBinary, Text, TIMESTAMP
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.db_session import Base


# =====================================================
# MODEL: Turma (Class)
# =====================================================
class Turma(Base):
    __tablename__ = "turmas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    alunos = relationship("Aluno", back_populates="turma")
    presencas = relationship("Presenca", back_populates="turma")
    professores = relationship(
        "Professor",
        secondary="turmas_professores",
        back_populates="turmas"
    )

    def __repr__(self):
        return f"<Turma(id={self.id}, nome='{self.nome}')>"


# =====================================================
# MODEL: Professor
# =====================================================
class Professor(Base):
    __tablename__ = "professores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    ativo = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    turmas = relationship(
        "Turma",
        secondary="turmas_professores",
        back_populates="professores"
    )
    presencas_validadas = relationship(
        "Presenca",
        back_populates="validador",
        foreign_keys="Presenca.validado_por"
    )

    def __repr__(self):
        return (
            f"<Professor(id={self.id}, "
            f"nome='{self.nome}', email='{self.email}')>"
        )


# =====================================================
# MODEL: TurmaProfessor (Association Table)
# =====================================================
class TurmaProfessor(Base):
    __tablename__ = "turmas_professores"

    id = Column(Integer, primary_key=True, index=True)
    turma_id = Column(
        Integer,
        ForeignKey("turmas.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    professor_id = Column(
        Integer,
        ForeignKey("professores.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return (
            f"<TurmaProfessor(turma_id={self.turma_id}, "
            f"professor_id={self.professor_id})>"
        )


# =====================================================
# MODEL: Aluno (Student)
# =====================================================
class Aluno(Base):
    __tablename__ = "alunos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False, index=True)
    turma_id = Column(
        Integer,
        ForeignKey("turmas.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    check_professor = Column(Boolean, default=False, index=True)
    ativo = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    updated_at = Column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    turma = relationship("Turma", back_populates="alunos")
    embeddings = relationship(
        "FaceEmbedding",
        back_populates="aluno",
        cascade="all, delete-orphan"
    )
    presencas = relationship("Presenca", back_populates="aluno")

    def __repr__(self):
        return (
            f"<Aluno(id={self.id}, nome='{self.nome}', "
            f"turma_id={self.turma_id})>"
        )


# =====================================================
# MODEL: FaceEmbedding
# =====================================================
class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    aluno_id = Column(
        Integer,
        ForeignKey("alunos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    embedding = Column(LargeBinary, nullable=False)
    foto_nome = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Relationships
    aluno = relationship("Aluno", back_populates="embeddings")

    def __repr__(self):
        return (
            f"<FaceEmbedding(id={self.id}, aluno_id={self.aluno_id}, "
            f"foto='{self.foto_nome}')>"
        )


# =====================================================
# MODEL: Presenca (Attendance)
# =====================================================
class Presenca(Base):
    __tablename__ = "presencas"

    id = Column(Integer, primary_key=True, index=True)
    aluno_id = Column(
        Integer,
        ForeignKey("alunos.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    turma_id = Column(
        Integer,
        ForeignKey("turmas.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    data_hora = Column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow,
        index=True
    )
    confianca = Column(Float, nullable=True)
    check_professor = Column(Boolean, default=False, index=True)
    validado_em = Column(TIMESTAMP(timezone=True), nullable=True)
    validado_por = Column(
        Integer,
        ForeignKey("professores.id", ondelete="SET NULL"),
        nullable=True
    )
    observacao = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    # Relationships
    aluno = relationship("Aluno", back_populates="presencas")
    turma = relationship("Turma", back_populates="presencas")
    validador = relationship(
        "Professor",
        back_populates="presencas_validadas",
        foreign_keys=[validado_por]
    )

    def __repr__(self):
        return (
            f"<Presenca(id={self.id}, aluno_id={self.aluno_id}, "
            f"data_hora='{self.data_hora}', confianca={self.confianca})>"
        )


# =====================================================
# Legacy Models (For backward compatibility)
# =====================================================
# Aliases for old code that might still use these names
Student = Aluno
AttendanceRecord = Presenca
