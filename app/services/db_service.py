"""
app/services/db_service.py
--------------------------
Serviço de gerenciamento da conexão com o Supabase, incluindo métodos para
alunos, faces e registro de chamadas.
"""
from postgrest import APIResponse
from supabase import create_client, Client
from app.config import settings, Settings
from typing import List, Dict, Any

# Classe que gerencia a comunicação com o Supabase
class SupabaseDB:
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)

    # --- Métodos de Students (Alunos) ---

    def list_students(self) -> List[Dict[str, Any]]:
        """Retorna todos os registros da tabela 'students' como lista de dicionários."""
        response: APIResponse = self.client.table('students').select('*').execute()
        return response.data

    def get_students(self) -> List[Dict[str, Any]]:
        """Alias para list_students para compatibilidade com o router."""
        return self.list_students()

    def create_student(self, nome: str, is_professor: bool) -> Dict[str, Any]:
        """
        Cria um registro de aluno/professor no Supabase.
        Aceita 'nome' e 'is_professor' (alinhado com o router).
        """
        # Mapeia 'nome' para a coluna 'name' (ou 'nome', se for o caso na sua DB)
        student_data = {
            "nome": nome, 
            "is_professor": is_professor
        }
        response: APIResponse = self.client.table('students').insert(student_data).execute()
        return response.data[0] if response.data else {}

    def delete_student(self, student_id: str) -> bool:
        """Deleta um aluno pelo ID."""
        response: APIResponse = self.client.table('students').delete().eq('id', student_id).execute()
        return len(response.data) > 0

    # --- Métodos de Attendance (Chamada) ---

    def list_all_attendance(self) -> List[Dict[str, Any]]:
        """
        Retorna todos os registros da tabela 'attendance_records' como lista de dicionários.
        """
        # Assume que o nome da coluna do aluno para o JOIN é 'nome'
        response: APIResponse = self.client.table('attendance_records').select('*, students(nome)').execute()
        return response.data

    def register_attendance(self, attendance_data: dict) -> APIResponse:
        """Registra uma nova chamada na tabela 'attendance_records'."""
        return self.client.table('attendance_records').insert(attendance_data).execute()

    def validate_attendance(self, attendance_id: str) -> bool:
        """Atualiza o campo 'check_professor' para True."""
        response: APIResponse = self.client.table('attendance_records').update({"check_professor": True}).eq('id', attendance_id).execute()
        return len(response.data) > 0

    # --- Métodos de Faces (Reconhecimento Facial) ---

    def get_all_faces(self) -> List[Dict[str, Any]]:
        """
        Recupera todos os embeddings de faces e o student_id associado.
        CORRIGIDO: Referência à tabela 'face_embeddings' e coluna 'vector'.
        """
        # COLUNA AJUSTADA DE 'embedding' PARA 'vector'
        response: APIResponse = self.client.table('face_embeddings').select('student_id, vector').execute()
        return response.data

    def add_embedding(self, student_id: str, vector_json: str) -> bool:
        """
        Salva o embedding facial associado a um aluno.
        CORRIGIDO: Referência à tabela 'face_embeddings' e coluna 'vector'.
        """
        face_data = {
            "student_id": student_id,
            "vector": vector_json  # COLUNA AJUSTADA DE 'embedding' PARA 'vector'
        }
        response: APIResponse = self.client.table('face_embeddings').insert(face_data).execute()
        return len(response.data) > 0


# --- Instância Global e Dependência FastAPI ---

# 1. Cria a instância do gerenciador de banco de dados
db_manager = SupabaseDB(
    url=settings.SUPABASE_URL,
    key=settings.SUPABASE_KEY
)

# 2. Função de dependência para injeção no FastAPI
def get_db_manager() -> SupabaseDB:
    """Retorna a instância global do gerenciador de banco de dados."""
    return db_manager