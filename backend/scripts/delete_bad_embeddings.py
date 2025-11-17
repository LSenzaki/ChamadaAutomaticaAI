"""
Quick script to delete all face embeddings.
Use this to clean up bad data, then re-register students.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.db_service import db_manager

print("=" * 60)
print("🗑️  DELETAR EMBEDDINGS CORROMPIDOS")
print("=" * 60)

try:
    # Delete all embeddings
    result = db_manager.client.table('face_embeddings').delete().neq('id', 0).execute()
    count = len(result.data)
    
    print(f"\n✅ {count} embeddings deletados com sucesso!")
    print("\n💡 Agora você pode:")
    print("   1. Acessar http://localhost:8000/docs")
    print("   2. Usar POST /alunos/cadastrar para recadastrar os alunos")
    print("   3. Enviar fotos novas que serão codificadas corretamente")
    print("\n" + "=" * 60)
    
except Exception as e:
    print(f"\n❌ Erro ao deletar: {e}")
    print("\n" + "=" * 60)
