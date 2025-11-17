# Database Migration Guide

## What Was Done

### 1. Updated Database Models (`db_models.py`)
✅ **COMPLETED** - Replaced old schema with new structure:

**Old Schema (Removed):**
- `Student` - Single table for students with is_professor flag
- `FaceEmbedding` - Face data linked to Student
- `AttendanceRecord` - Attendance records

**New Schema (Implemented):**
- `Turma` - Class/course management
- `Professor` - Professor management with email and active status
- `TurmaProfessor` - Many-to-many relationship between professors and classes
- `Aluno` - Students with class assignment (turma_id foreign key)
- `FaceEmbedding` - Face embeddings linked to Aluno (changed from student_id to aluno_id)
- `Presenca` - Attendance records with validation tracking

**Key Changes:**
- Separated professors from students (no more is_professor flag)
- Added class assignment for students
- Many-to-many relationship: professors can teach multiple classes
- Enhanced attendance validation with professor tracking
- All timestamps use PostgreSQL TIMESTAMP with timezone
- Face embeddings now use LargeBinary (for numpy arrays)
- Added observacao (notes) field for attendance validation

**Legacy Support:**
- Added aliases `Student = Aluno` and `AttendanceRecord = Presenca` for backward compatibility

### 2. Updated Database Connection (`db_session.py`)
✅ **COMPLETED** - Migrated from SQLite to PostgreSQL (Supabase):

**Changes:**
- Replaced SQLite connection with PostgreSQL
- Reads SUPABASE_URL and SUPABASE_SENHA from .env
- Constructs PostgreSQL connection URL dynamically
- Added connection pooling (pool_size=10, max_overflow=20)
- Added pool_pre_ping for connection health checks
- Added create_tables() function for schema creation

**Connection Details:**
- Host: `db.{project_ref}.supabase.co`
- Port: `5432`
- Database: `postgres`
- User: `postgres`
- Password: From SUPABASE_SENHA env variable

---

## What Needs to Be Done

### STEP 1: Run SQL Schema in Supabase ⚠️ **REQUIRED**

**Location:** `backend/database_schema.sql`

**Instructions:**
1. Go to https://hhzrfesjunkbgxjkkpol.supabase.co
2. Navigate to SQL Editor
3. Create a new query
4. Copy and paste the entire content of `database_schema.sql`
5. Click "Run" to execute
6. Verify tables were created in Table Editor

**What This Creates:**
- 6 tables: turmas, professores, turmas_professores, alunos, face_embeddings, presencas
- 3 views: vw_alunos_completo, vw_professores_turmas, vw_presencas_completo
- 1 function: get_presencas_by_date(date)
- Indexes for performance
- Triggers for auto-updating timestamps
- Sample data (optional - can be removed)

---

### STEP 2: Install Required Python Package

The new models use `psycopg2` for PostgreSQL connection:

```bash
cd backend
source ../.venv/bin/activate
pip install psycopg2-binary
```

---

### STEP 3: Update API Routers

**Files to Update:**
- `backend/app/routers/students.py`
- `backend/app/routers/faces.py`
- `backend/app/routers/comparison.py`

**Required Changes:**

1. **Update imports:**
   ```python
   from app.models.db_models import Aluno, Turma, Professor, Presenca, FaceEmbedding
   from app.models.db_session import get_db
   from sqlalchemy.orm import Session
   ```

2. **Add new endpoints for classes (turmas):**
   ```python
   @router.post("/classes/")
   def create_class(nome: str, db: Session = Depends(get_db)):
       turma = Turma(nome=nome)
       db.add(turma)
       db.commit()
       return turma

   @router.get("/classes/")
   def list_classes(db: Session = Depends(get_db)):
       return db.query(Turma).all()

   @router.delete("/classes/{turma_id}")
   def delete_class(turma_id: int, db: Session = Depends(get_db)):
       turma = db.query(Turma).filter(Turma.id == turma_id).first()
       if turma:
           db.delete(turma)
           db.commit()
       return {"message": "Class deleted"}
   ```

3. **Add new endpoints for professors:**
   ```python
   @router.post("/professors/")
   def create_professor(nome: str, email: str, turma_ids: List[int], db: Session = Depends(get_db)):
       professor = Professor(nome=nome, email=email)
       db.add(professor)
       db.flush()  # Get professor.id
       
       # Assign classes
       for turma_id in turma_ids:
           assoc = TurmaProfessor(professor_id=professor.id, turma_id=turma_id)
           db.add(assoc)
       
       db.commit()
       return professor

   @router.get("/professors/")
   def list_professors(db: Session = Depends(get_db)):
       return db.query(Professor).all()
   ```

4. **Update student endpoints:**
   ```python
   @router.post("/students/")
   def create_student(nome: str, turma_id: Optional[int], db: Session = Depends(get_db)):
       aluno = Aluno(nome=nome, turma_id=turma_id)
       db.add(aluno)
       db.commit()
       return aluno

   @router.get("/students/")
   def list_students(turma_id: Optional[int] = None, db: Session = Depends(get_db)):
       query = db.query(Aluno)
       if turma_id:
           query = query.filter(Aluno.turma_id == turma_id)
       return query.all()
   ```

5. **Update attendance endpoints:**
   ```python
   @router.post("/attendance/")
   def create_attendance(aluno_id: int, turma_id: int, confianca: float, db: Session = Depends(get_db)):
       presenca = Presenca(
           aluno_id=aluno_id,
           turma_id=turma_id,
           confianca=confianca
       )
       db.add(presenca)
       db.commit()
       return presenca

   @router.put("/attendance/{presenca_id}/validate")
   def validate_attendance(presenca_id: int, professor_id: int, observacao: Optional[str], db: Session = Depends(get_db)):
       presenca = db.query(Presenca).filter(Presenca.id == presenca_id).first()
       if presenca:
           presenca.check_professor = True
           presenca.validado_por = professor_id
           presenca.validado_em = datetime.utcnow()
           presenca.observacao = observacao
           db.commit()
       return presenca
   ```

---

### STEP 4: Update Face Recognition Service

**File:** `backend/app/services/face_service.py` or similar

**Changes Needed:**
1. Update FaceEmbedding storage to use aluno_id instead of student_id
2. Store numpy arrays as binary (pickle or using numpy.tobytes())
3. Update attendance creation to include turma_id

**Example:**
```python
import numpy as np
import pickle

# When storing embedding
embedding_binary = pickle.dumps(face_encoding)
face_emb = FaceEmbedding(
    aluno_id=aluno_id,
    embedding=embedding_binary,
    foto_nome="photo1.jpg"
)

# When loading embedding
embedding = pickle.loads(face_emb.embedding)
face_array = np.array(embedding)
```

---

### STEP 5: Update Pydantic Schemas

**File:** `backend/app/schemas/pydantic_schemas.py`

**Add new schemas:**
```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TurmaCreate(BaseModel):
    nome: str

class TurmaResponse(BaseModel):
    id: int
    nome: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProfessorCreate(BaseModel):
    nome: str
    email: str
    turma_ids: List[int]

class ProfessorResponse(BaseModel):
    id: int
    nome: str
    email: str
    ativo: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class AlunoCreate(BaseModel):
    nome: str
    turma_id: Optional[int] = None

class AlunoResponse(BaseModel):
    id: int
    nome: str
    turma_id: Optional[int]
    check_professor: bool
    ativo: bool
    
    class Config:
        from_attributes = True

class PresencaCreate(BaseModel):
    aluno_id: int
    turma_id: int
    confianca: float

class PresencaResponse(BaseModel):
    id: int
    aluno_id: int
    turma_id: Optional[int]
    data_hora: datetime
    confianca: Optional[float]
    check_professor: bool
    validado_em: Optional[datetime]
    validado_por: Optional[int]
    
    class Config:
        from_attributes = True
```

---

### STEP 6: Test Database Connection

**Create a test script:** `backend/test_connection.py`

```python
from app.models.db_session import engine, SessionLocal
from app.models.db_models import Turma, Professor, Aluno
from sqlalchemy import text

def test_connection():
    # Test raw connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print("PostgreSQL version:", result.fetchone()[0])
    
    # Test session and query
    db = SessionLocal()
    try:
        turmas = db.query(Turma).all()
        print(f"Found {len(turmas)} classes in database")
        
        professores = db.query(Professor).all()
        print(f"Found {len(professores)} professors in database")
        
        alunos = db.query(Aluno).all()
        print(f"Found {len(alunos)} students in database")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_connection()
```

**Run test:**
```bash
cd backend
python test_connection.py
```

---

### STEP 7: Update Frontend API Calls

The frontend already expects the new schema structure! ✅

**Existing frontend code already prepared for:**
- `/classes/` endpoints
- `/professors/` endpoints
- `/students/` with turma_id parameter
- `/attendance/` with validation

**What to verify:**
- API base URL matches backend (localhost:8000)
- Endpoint paths match router definitions
- Request/response formats match Pydantic schemas

---

## Migration Checklist

- [ ] **Step 1:** Run SQL schema in Supabase SQL Editor
- [ ] **Step 2:** Install psycopg2-binary package
- [ ] **Step 3:** Update API routers (students, faces, comparison)
- [ ] **Step 4:** Update face recognition service
- [ ] **Step 5:** Update Pydantic schemas
- [ ] **Step 6:** Test database connection
- [ ] **Step 7:** Verify frontend API calls
- [ ] **Step 8:** Test full flow: register student → take photo → mark attendance → validate

---

## Rollback Plan

If issues occur, you can rollback to old schema:

1. **Restore old models:**
   ```bash
   git checkout HEAD~1 backend/app/models/db_models.py
   git checkout HEAD~1 backend/app/models/db_session.py
   ```

2. **Switch back to SQLite:**
   - Old db_session.py uses `sqlite:///./sql_app.db`
   - No Supabase connection needed

---

## Additional Resources

- **Supabase Dashboard:** https://hhzrfesjunkbgxjkkpol.supabase.co
- **Database Schema:** `backend/database_schema.sql`
- **Setup Guide:** `backend/DATABASE_SETUP.md`
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org/
- **FastAPI Docs:** https://fastapi.tiangolo.com/

---

## Next Steps After Migration

1. **Enable Row Level Security (RLS)** in Supabase for production
2. **Add Alembic** for database migrations
3. **Add authentication** (JWT tokens)
4. **Add API documentation** (FastAPI auto-generates /docs)
5. **Add logging** for debugging
6. **Add error handling** for database operations
7. **Add tests** for all endpoints

---

## Support

If you encounter issues:
1. Check `backend/DATABASE_SETUP.md` for troubleshooting
2. Verify .env file has correct credentials
3. Check Supabase dashboard for connection limits
4. Review FastAPI logs for detailed errors
