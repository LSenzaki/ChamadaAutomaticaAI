"""
app/services/db_service.py
--------------------------
Database service for Supabase REST API communication.
Updated for new schema: turmas, professores, alunos, presencas, face_embeddings.
"""
from supabase import create_client, Client
from app.config import settings
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import pytz


def format_timestamp(ts_str: str, tz_name: str = "America/Sao_Paulo") -> str:
    """
    Convert UTC timestamp to local timezone and format for display.
    
    Args:
        ts_str: ISO format timestamp string
        tz_name: Timezone name (default: Brazil/Sao Paulo)
    
    Returns:
        Formatted timestamp: "YYYY-MM-DD HH:MM:SS"
    """
    if not ts_str:
        return None
    
    try:
        # Parse UTC timestamp
        dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        
        # Convert to local timezone
        local_tz = pytz.timezone(tz_name)
        local_dt = dt.astimezone(local_tz)
        
        # Format for display
        return local_dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        return ts_str  # Return original if parsing fails


def format_record_timestamps(record: Dict[str, Any]) -> Dict[str, Any]:
    """Format all timestamp fields in a record for better readability"""
    if not record:
        return record
    
    timestamp_fields = [
        'created_at', 'updated_at', 'data_hora', 
        'validado_em', 'timestamp'
    ]
    
    for field in timestamp_fields:
        if field in record and record[field]:
            record[field] = format_timestamp(record[field])
    
    return record


def format_records_timestamps(
    records: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Format timestamps in a list of records"""
    return [format_record_timestamps(record) for record in records]


class SupabaseDB:
    """Manages communication with Supabase using REST API"""
    
    def __init__(self, url: str, key: str):
        self.client: Client = create_client(url, key)

    # ========================================
    # TURMAS (Classes)
    # ========================================
    
    def list_turmas(self) -> List[Dict[str, Any]]:
        """Get all classes"""
        response = self.client.table('turmas').select('*').execute()
        return format_records_timestamps(response.data)
    
    def create_turma(self, nome: str) -> Dict[str, Any]:
        """Create a new class"""
        response = self.client.table('turmas').insert({
            "nome": nome
        }).execute()
        return response.data[0] if response.data else {}
    
    def delete_turma(self, turma_id: int) -> bool:
        """Delete a class by ID"""
        response = self.client.table('turmas').delete().eq(
            'id', turma_id
        ).execute()
        return len(response.data) > 0

    # ========================================
    # PROFESSORES (Professors)
    # ========================================
    
    def list_professores(self) -> List[Dict[str, Any]]:
        """Get all professors"""
        response = self.client.table('professores').select('*').execute()
        return format_records_timestamps(response.data)
    
    def create_professor(
        self, nome: str, email: str, turma_ids: List[int]
    ) -> Dict[str, Any]:
        """Create a new professor and assign classes"""
        # Create professor
        prof_response = self.client.table('professores').insert({
            "nome": nome,
            "email": email
        }).execute()
        
        if not prof_response.data:
            return {}
        
        professor = prof_response.data[0]
        professor_id = professor['id']
        
        # Assign classes (turmas_professores)
        if turma_ids:
            associations = [
                {"professor_id": professor_id, "turma_id": tid}
                for tid in turma_ids
            ]
            self.client.table('turmas_professores').insert(
                associations
            ).execute()
        
        return professor
    
    def delete_professor(self, professor_id: int) -> bool:
        """Delete a professor by ID"""
        response = self.client.table('professores').delete().eq(
            'id', professor_id
        ).execute()
        return len(response.data) > 0

    # ========================================
    # ALUNOS (Students)
    # ========================================
    
    def list_alunos(
        self, turma_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get all students, optionally filtered by class"""
        query = self.client.table('alunos').select('*, turmas(nome)')
        if turma_id:
            query = query.eq('turma_id', turma_id)
        response = query.execute()
        return format_records_timestamps(response.data)
    
    def get_aluno_by_id(self, aluno_id: int) -> Optional[Dict[str, Any]]:
        """Get a student by ID"""
        response = self.client.table('alunos').select(
            '*, turmas(nome)'
        ).eq('id', aluno_id).single().execute()
        return response.data if response.data else None
    
    def get_aluno_by_name(self, nome: str) -> Optional[Dict[str, Any]]:
        """Get a student by name"""
        response = self.client.table('alunos').select(
            '*'
        ).eq('nome', nome).limit(1).execute()
        return response.data[0] if response.data else None
    
    def create_aluno(
        self, nome: str, turma_id: Optional[int] = None,
        check_professor: bool = False
    ) -> Dict[str, Any]:
        """Create a new student"""
        aluno_data = {
            "nome": nome,
            "turma_id": turma_id,
            "check_professor": check_professor
        }
        response = self.client.table('alunos').insert(
            aluno_data
        ).execute()
        return response.data[0] if response.data else {}
    
    def update_aluno(
        self, aluno_id: int, **fields
    ) -> Optional[Dict[str, Any]]:
        """Update student fields"""
        response = self.client.table('alunos').update(fields).eq(
            'id', aluno_id
        ).execute()
        return response.data[0] if response.data else None
    
    def delete_aluno(self, aluno_id: int) -> bool:
        """Delete a student by ID"""
        response = self.client.table('alunos').delete().eq(
            'id', aluno_id
        ).execute()
        return len(response.data) > 0

    # ========================================
    # FACE EMBEDDINGS
    # ========================================
    
    def get_all_faces(self) -> List[Dict[str, Any]]:
        """Get all face embeddings with student info"""
        response = self.client.table('face_embeddings').select(
            'aluno_id, embedding, foto_nome, alunos(nome, turma_id)'
        ).execute()
        return response.data
    
    def add_embedding(
        self, aluno_id: int, embedding_data: str, foto_nome: str = None
    ) -> bool:
        """Save face embedding for a student"""
        face_data = {
            "aluno_id": aluno_id,
            "embedding": embedding_data,
            "foto_nome": foto_nome
        }
        response = self.client.table('face_embeddings').insert(
            face_data
        ).execute()
        return len(response.data) > 0

    # ========================================
    # PRESENCAS (Attendance)
    # ========================================
    
    def list_presencas(
        self, data_inicio: str = None, data_fim: str = None,
        turma_id: int = None
    ) -> List[Dict[str, Any]]:
        """Get attendance records with filters"""
        query = self.client.table('presencas').select(
            '*, alunos(nome), turmas(nome)'
        )
        
        if data_inicio:
            query = query.gte('data_hora', data_inicio)
        if data_fim:
            query = query.lte('data_hora', data_fim)
        if turma_id:
            query = query.eq('turma_id', turma_id)
        
        response = query.order('data_hora', desc=True).execute()
        return format_records_timestamps(response.data)
    
    def create_presenca(
        self, aluno_id: int, turma_id: int, confianca: float = None
    ) -> Dict[str, Any]:
        """Register new attendance"""
        presenca_data = {
            "aluno_id": aluno_id,
            "turma_id": turma_id,
            "confianca": confianca
        }
        response = self.client.table('presencas').insert(
            presenca_data
        ).execute()
        return response.data[0] if response.data else {}
    
    def validate_presenca(
        self, presenca_id: int, professor_id: int,
        observacao: str = None
    ) -> bool:
        """Validate attendance by professor"""
        from datetime import datetime
        response = self.client.table('presencas').update({
            "check_professor": True,
            "validado_por": professor_id,
            "validado_em": datetime.utcnow().isoformat(),
            "observacao": observacao
        }).eq('id', presenca_id).execute()
        return len(response.data) > 0
    
    def get_presenca_by_id(
        self, presenca_id: int
    ) -> Optional[Dict[str, Any]]:
        """Get attendance record by ID"""
        response = self.client.table('presencas').select(
            '*, alunos(nome), turmas(nome)'
        ).eq('id', presenca_id).single().execute()
        return response.data if response.data else None

    # ========================================
    # LEGACY METHODS (backward compatibility)
    # ========================================
    
    def list_students(self) -> List[Dict[str, Any]]:
        """Legacy: use list_alunos instead"""
        return self.list_alunos()
    
    def get_students(self) -> List[Dict[str, Any]]:
        """Legacy: use list_alunos instead"""
        return self.list_alunos()
    
    def get_student_by_id(self, student_id: int) -> Optional[Dict[str, Any]]:
        """Legacy: use get_aluno_by_id instead"""
        return self.get_aluno_by_id(student_id)
    
    def create_student(
        self, nome: str, is_professor: bool
    ) -> Dict[str, Any]:
        """Legacy: use create_aluno or create_professor instead"""
        return self.create_aluno(nome, check_professor=is_professor)
    
    def delete_student(self, student_id: int) -> bool:
        """Legacy: use delete_aluno instead"""
        return self.delete_aluno(student_id)
    
    def list_all_attendance(self) -> List[Dict[str, Any]]:
        """Legacy: use list_presencas instead"""
        return self.list_presencas()
    
    def register_attendance(self, attendance_data: dict) -> Dict[str, Any]:
        """Legacy: use create_presenca instead"""
        # Support both old (student_id) and new (aluno_id) field names
        aluno_id = attendance_data.get('aluno_id') or attendance_data.get('student_id')
        return self.create_presenca(
            aluno_id=aluno_id,
            turma_id=attendance_data.get('turma_id'),
            confianca=attendance_data.get('confidence')
        )
    
    def validate_attendance(self, attendance_id: int) -> bool:
        """Legacy: use validate_presenca instead"""
        return self.validate_presenca(attendance_id, professor_id=None)
    
    def get_attendance_record_by_id(
        self, attendance_id: int
    ) -> Optional[Dict[str, Any]]:
        """Legacy: use get_presenca_by_id instead"""
        return self.get_presenca_by_id(attendance_id)
    
    def get_student_by_name(self, nome: str) -> Optional[Dict[str, Any]]:
        """Legacy: use get_aluno_by_name instead"""
        return self.get_aluno_by_name(nome)


# Global instance and FastAPI dependency
db_manager = SupabaseDB(
    url=settings.SUPABASE_URL,
    key=settings.SUPABASE_KEY
)


def get_db_manager() -> SupabaseDB:
    """Returns the global database manager instance"""
    return db_manager
