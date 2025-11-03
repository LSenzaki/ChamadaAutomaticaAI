"""
app/schemas/student_schema.py
Esquemas Pydantic para validação de dados de Alunos (Students).
"""
from pydantic import BaseModel, Field
from typing import Optional

# Esquema base para a criação de um novo aluno (no POST)
class StudentCreate(BaseModel):
    name: str = Field(..., description="Nome completo do aluno.")
    registration_number: str = Field(..., description="Número de matrícula único do aluno.")
    
    # Exemplo de configuração Pydantic
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Maria Silva",
                "registration_number": "2024001"
            }
        }

# Esquema para o retorno da API (incluindo o ID gerado pelo Supabase)
class Student(StudentCreate):
    id: Optional[str] = Field(None, description="ID único do aluno gerado pelo Supabase.")
