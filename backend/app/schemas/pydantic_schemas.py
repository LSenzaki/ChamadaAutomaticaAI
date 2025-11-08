"""
pydantic_schemas.py
-------------------

Este módulo define os schemas do Pydantic, usados para validação e
serialização/deserialização de dados que transitam pela API.

Responsável por:
- Garantir que os dados recebidos pelas requisições sigam o formato esperado.
- Definir como os dados são retornados pelas respostas da API.
- Servir como contrato entre frontend e backend.

"""

from pydantic import BaseModel

class PessoaCreate(BaseModel):
    nome: str

class PessoaOut(BaseModel):
    id: int
    nome: str
    check_professor: bool
