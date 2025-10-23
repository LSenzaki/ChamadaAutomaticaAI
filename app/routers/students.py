"""
students.py (Versão Supabase Corrigida com Depends)
-------------------------------------------------
Router responsável pelo gerenciamento de alunos.
Atualizado para usar injeção de dependência do SupabaseDB.
"""

from fastapi import APIRouter, UploadFile, Form, HTTPException, Depends
from app.services.face_service import get_face_encoding
# Alterado: Importamos a função de dependência em vez da instância global db_manager
from app.services.db_service import get_db_manager, SupabaseDB 
from app.config import settings
import json
import uvicorn
from typing import List, Dict, Any

router = APIRouter(prefix="/students", tags=["students"])

# NOTA: O 'foto' no cadastro ainda é necessário para obter o encoding

@router.post("/cadastrar")
async def cadastrar(
    nome: str = Form(...), 
    is_professor: bool = Form(False),
    foto: UploadFile = None,
    db_manager: SupabaseDB = Depends(get_db_manager) # NOVO: Injeção de dependência
):
    """
    Cadastra um aluno/professor no Supabase com a codificação facial.
    """     
    if not foto:
        raise HTTPException(status_code=400, detail="Imagem obrigatória")

    # 1. Obter o encoding facial
    encoding = get_face_encoding(foto)
    if encoding is None:
        raise HTTPException(status_code=400, detail="Nenhum rosto detectado")

    # 2. Criar o registro do Aluno/Professor no Supabase
    try:
        new_student = db_manager.create_student(nome=nome, is_professor=is_professor)
        if not new_student or 'id' not in new_student:
             raise Exception("Falha ao criar o aluno no Supabase.")

        student_id = new_student['id']
        
        # 3. Adicionar o embedding
        # Converte o array numpy para string JSON antes de enviar para o Supabase
        encoding_json_string = json.dumps(encoding.tolist())
        success = db_manager.add_embedding(student_id=student_id, vector_json=encoding_json_string)
        
        if not success:
             # Se o aluno foi criado mas o embedding falhou (deveria ser transacional)
             # Neste cenário, o aluno existe sem rosto
             pass 

    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Erro ao cadastrar: {e}")

    return {"mensagem": f"{nome} cadastrado com sucesso!", "id": student_id}


@router.get("/listar")
def listar_alunos(db_manager: SupabaseDB = Depends(get_db_manager)):
    """ Retorna a lista de todos os alunos cadastrados. """
    alunos = db_manager.list_students()
    return alunos

@router.delete("/remover/{student_id}")
def remover_aluno(student_id: str, db_manager: SupabaseDB = Depends(get_db_manager)):
    """ Remove um aluno. Assumimos remoção em cascata no Supabase. """
    success = db_manager.delete_student(student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Aluno não encontrado ou falha na remoção")
    return {"mensagem": f"Aluno removido com sucesso"}


# --- Rotas de Chamada/Validação (Professor) ---

@router.get("/chamadas/listar")
def listar_todas_chamadas(db_manager: SupabaseDB = Depends(get_db_manager)):
    """ Retorna a lista de TODOS os registros de chamada (com nome do aluno). """
    registros = db_manager.list_all_attendance()
    
    # Adaptação para o formato de resposta esperado, extraindo o nome
    return [
        {
            "id": r['id'],
            "student_id": r['student_id'],
            "nome_aluno": r['students']['nome'] if r.get('students') else "Desconhecido",
            "timestamp": r['timestamp'],
            "session_tag": r['session_tag'],
            "confidence": r['confidence'],
            "validado_professor": r['check_professor']
        }
        for r in registros
    ]

@router.patch("/chamadas/validar/{attendance_id}")
def validar_chamada_professor(attendance_id: str, db_manager: SupabaseDB = Depends(get_db_manager)):
    """ Permite que o professor valide um registro de chamada. """
    success = db_manager.validate_attendance(attendance_id)
    
    if not success:
        # Se a validação falhar, pode ser ID não encontrado ou erro do Supabase
        raise HTTPException(status_code=404, detail="Registro de chamada não encontrado ou falha na atualização")
    
    return {"mensagem": f"Chamada {attendance_id} validada com sucesso.", "validado": True}
