# app/models/response.py (Exemplo de como deve ficar)

from pydantic import BaseModel
from typing import Optional, List, Any

class ResultadoSimilaridade(BaseModel):
    id: int
    nome: str
    similaridade: float
    check_professor: bool
    
    # NOVO CAMPO ADICIONADO:
    mensagem_chamada: Optional[str] = None # Campo opcional para o registro de sucesso

class ResultadoReconhecimento(BaseModel):
    mensagem: str
    mais_provavel: Optional[ResultadoSimilaridade]
    todos: List[ResultadoSimilaridade]

class ApiResponse(BaseModel):
    sucesso: bool
    mensagem: str
    dados: Optional[Any] = None