"""
Test Database Connection
-------------------------
Simple script to verify PostgreSQL/Supabase connection and test queries.
Run this after setting up the database schema.

Usage:
    cd backend
    python test_connection.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.models.db_session import engine, SessionLocal
from app.models.db_models import Turma, Professor, Aluno, Presenca
from sqlalchemy import text


def test_raw_connection():
    """Test raw PostgreSQL connection"""
    print("\n" + "="*60)
    print("Testing PostgreSQL Connection...")
    print("="*60)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print("✅ Connection successful!")
            print(f"PostgreSQL version: {version[:50]}...")
            return True
    except Exception as e:
        print("❌ Connection failed!")
        print(f"Error: {str(e)}")
        return False


def test_tables():
    """Test if tables exist and can be queried"""
    print("\n" + "="*60)
    print("Testing Database Tables...")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Test Turmas (Classes)
        turmas = db.query(Turma).all()
        print(f"✅ Turmas table: {len(turmas)} records found")
        for turma in turmas[:3]:  # Show first 3
            print(f"   - ID {turma.id}: {turma.nome}")
        
        # Test Professores
        professores = db.query(Professor).all()
        print(f"✅ Professores table: {len(professores)} records found")
        for prof in professores[:3]:
            print(f"   - ID {prof.id}: {prof.nome} ({prof.email})")
        
        # Test Alunos (Students)
        alunos = db.query(Aluno).all()
        print(f"✅ Alunos table: {len(alunos)} records found")
        for aluno in alunos[:3]:
            turma_nome = (
                db.query(Turma.nome)
                .filter(Turma.id == aluno.turma_id)
                .scalar() if aluno.turma_id else "No class"
            )
            print(f"   - ID {aluno.id}: {aluno.nome} (Class: {turma_nome})")
        
        # Test Presencas (Attendance)
        presencas = db.query(Presenca).all()
        print(
            f"✅ Presencas table: {len(presencas)} records found"
        )
        for pres in presencas[:3]:
            aluno_nome = (
                db.query(Aluno.nome)
                .filter(Aluno.id == pres.aluno_id)
                .scalar()
            )
            print(
                f"   - ID {pres.id}: {aluno_nome} - "
                f"{pres.data_hora.strftime('%Y-%m-%d %H:%M')} "
                f"(Confidence: {pres.confianca})"
            )
        
        return True
        
    except Exception as e:
        print(f"❌ Table query failed!")
        print(f"Error: {str(e)}")
        return False
    finally:
        db.close()


def test_relationships():
    """Test SQLAlchemy relationships"""
    print("\n" + "="*60)
    print("Testing Relationships...")
    print("="*60)
    
    db = SessionLocal()
    try:
        # Test Turma -> Alunos relationship
        turma = db.query(Turma).first()
        if turma:
            print(f"✅ Class '{turma.nome}' has {len(turma.alunos)} students")
            for aluno in turma.alunos[:3]:
                print(f"   - {aluno.nome}")
        
        # Test Professor -> Turmas relationship
        professor = db.query(Professor).first()
        if professor:
            print(
                f"✅ Professor '{professor.nome}' "
                f"teaches {len(professor.turmas)} classes"
            )
            for turma in professor.turmas[:3]:
                print(f"   - {turma.nome}")
        
        # Test Aluno -> Presencas relationship
        aluno = db.query(Aluno).first()
        if aluno:
            print(
                f"✅ Student '{aluno.nome}' "
                f"has {len(aluno.presencas)} attendance records"
            )
        
        return True
        
    except Exception as e:
        print(f"❌ Relationship test failed!")
        print(f"Error: {str(e)}")
        return False
    finally:
        db.close()


def main():
    """Run all tests"""
    print("\n" + "#"*60)
    print("#" + " "*58 + "#")
    print("#" + "  DATABASE CONNECTION TEST".center(58) + "#")
    print("#" + " "*58 + "#")
    print("#"*60)
    
    results = []
    
    # Test 1: Raw connection
    results.append(test_raw_connection())
    
    # Test 2: Tables
    if results[-1]:
        results.append(test_tables())
    else:
        print("\n⚠️  Skipping table tests (connection failed)")
        results.append(False)
    
    # Test 3: Relationships
    if results[-1]:
        results.append(test_relationships())
    else:
        print("\n⚠️  Skipping relationship tests (table queries failed)")
        results.append(False)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✅ All tests passed! Database is ready to use.")
        print("\nNext steps:")
        print("1. Update API routers to use new models")
        print("2. Update face recognition service")
        print("3. Test frontend integration")
    else:
        print("\n❌ Some tests failed. Check the errors above.")
        print("\nTroubleshooting:")
        print("1. Make sure you ran database_schema.sql in Supabase")
        print("2. Check your .env file has correct credentials")
        print("3. Verify Supabase project is accessible")
    
    print("\n" + "#"*60 + "\n")


if __name__ == "__main__":
    main()
