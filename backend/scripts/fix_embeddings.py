"""
Script to check and fix embeddings in the database.
Run this to verify and repair any malformed base64 embeddings.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.db_service import db_manager
import base64
import pickle

def check_embeddings():
    """Check all embeddings in the database"""
    print("🔍 Checking embeddings in database...")
    
    faces = db_manager.get_all_faces()
    
    if not faces:
        print("❌ No face embeddings found in database")
        return
    
    print(f"✅ Found {len(faces)} face embeddings\n")
    
    for idx, face in enumerate(faces, 1):
        aluno_id = face.get('aluno_id')
        embedding_data = face.get('embedding')
        foto_nome = face.get('foto_nome', 'unknown')
        
        print(f"\n[{idx}] Aluno ID: {aluno_id} | Foto: {foto_nome}")
        print(f"    Tipo: {type(embedding_data)}")
        
        if isinstance(embedding_data, str):
            print(f"    Tamanho: {len(embedding_data)} caracteres")
            
            # Check if base64 is valid
            try:
                # Try to decode
                embedding_bytes = base64.b64decode(embedding_data)
                embedding_array = pickle.loads(embedding_bytes)
                print(f"    ✅ Base64 válido! Array shape: {embedding_array.shape}")
            except Exception as e:
                print(f"    ❌ ERRO ao decodificar: {e}")
                
                # Check padding
                padding_needed = (4 - len(embedding_data) % 4) % 4
                if padding_needed > 0:
                    print(f"    ⚠️  Padding faltando: {padding_needed} caracteres '='")
        else:
            print(f"    ⚠️  Tipo inesperado: {type(embedding_data)}")


def fix_embeddings():
    """Try to fix malformed embeddings by adding padding"""
    print("\n🔧 Tentando corrigir embeddings...\n")
    
    faces = db_manager.get_all_faces()
    
    if not faces:
        print("❌ No face embeddings found")
        return
    
    fixed_count = 0
    
    for face in faces:
        aluno_id = face.get('aluno_id')
        embedding_data = face.get('embedding')
        
        if not isinstance(embedding_data, str):
            continue
        
        # Check if needs padding
        padding_needed = (4 - len(embedding_data) % 4) % 4
        
        if padding_needed > 0:
            print(f"Aluno ID {aluno_id}: Adicionando {padding_needed} padding...")
            
            # Add padding
            fixed_embedding = embedding_data + ('=' * padding_needed)
            
            # Verify it works
            try:
                test_bytes = base64.b64decode(fixed_embedding)
                test_array = pickle.loads(test_bytes)
                print(f"  ✅ Corrigido! Shape: {test_array.shape}")
                
                # Update in database would require a new method in db_service
                # For now, just report what needs fixing
                fixed_count += 1
                
            except Exception as e:
                print(f"  ❌ Não foi possível corrigir: {e}")
    
    if fixed_count > 0:
        print(f"\n⚠️  {fixed_count} embeddings precisam ser corrigidos")
        print("💡 Solução: Recadastrar os alunos com fotos novas")
    else:
        print("\n✅ Todos os embeddings estão corretos!")


def delete_all_embeddings():
    """Delete all face embeddings (use with caution!)"""
    response = input("\n⚠️  ATENÇÃO: Isso vai deletar TODOS os embeddings! Confirma? (sim/não): ")
    
    if response.lower() != 'sim':
        print("❌ Operação cancelada")
        return
    
    try:
        # This would require a delete method in db_service
        result = db_manager.client.table('face_embeddings').delete().neq('id', 0).execute()
        print(f"✅ {len(result.data)} embeddings deletados")
        print("💡 Agora você pode recadastrar os alunos com fotos novas")
    except Exception as e:
        print(f"❌ Erro ao deletar: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 FERRAMENTA DE DIAGNÓSTICO DE EMBEDDINGS")
    print("=" * 60)
    
    # Check embeddings
    check_embeddings()
    
    # Try to fix
    fix_embeddings()
    
    # Option to delete all
    print("\n" + "=" * 60)
    delete_all_embeddings()
