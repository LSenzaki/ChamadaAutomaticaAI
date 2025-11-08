"""
students.py
------------
Router responsável pelo gerenciamento de alunos.

Funcionalidades:
- Cadastro de alunos com foto (POST /students/cadastrar)
- Listagem de alunos cadastrados (GET /students/listar)
- Remoção de alunos (DELETE /students/remover/{aluno_id})
- Validação de alunos pelo professor (PUT /students/validar/{aluno_id})
"""

from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.face_service import get_face_encoding
from app.models.db_session import get_db
from app.models.response import ResultadoReconhecimento, ResultadoSimilaridade
from app.models.db_models import Student, FaceEmbedding
import json


router = APIRouter(prefix="/students", tags=["students"])

@router.post("/cadastrar")
async def cadastrar(nome: str = Form(...), foto: UploadFile = None,
                    db: Session = Depends(get_db)):
    """
    Cadastra um aluno no banco de dados.
    
    Parâmetros:
    - nome: str → nome do aluno
    - foto: UploadFile → imagem do rosto do aluno
    - db: Session → sessão do banco (injeção de dependência)

    Retorna:
    - Mensagem de sucesso e ID do aluno cadastrado
    """     
    if not foto:
        raise HTTPException(status_code=400, detail="Imagem obrigatória")

    encoding = get_face_encoding(foto)
    if encoding is None:
        raise HTTPException(status_code=400, detail="Nenhum rosto detectado")

    # Criar aluno
    aluno = Student(
        nome=nome,
        is_professor=False
    )
    db.add(aluno)
    db.commit()
    db.refresh(aluno)

    # Adicionar embedding
    embedding = FaceEmbedding(
        student_id=aluno.id,
        vector=json.dumps(encoding.tolist())
    )
    db.add(embedding)
    db.commit()

    return {"mensagem": f"{nome} cadastrado com sucesso!", "id": aluno.id}


@router.get("/listar")
def listar_alunos(db: Session = Depends(get_db)):
    """
    Retorna a lista de todos os alunos cadastrados.
    """
    alunos = db.query(Student).all()
    return [
        {
            "id": aluno.id,
            "nome": aluno.nome,
            "check_professor": aluno.is_professor
        }
        for aluno in alunos
    ]

@router.delete("/remover/{aluno_id}")
def remover_aluno(aluno_id: int, db: Session = Depends(get_db)):
    """
    Remove um aluno do banco pelo ID.
    """
    aluno = db.query(Student).filter(Student.id == aluno_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    db.delete(aluno)
    db.commit()
    return {"mensagem": f"Aluno '{aluno.nome}' removido com sucesso"}


@router.put("/validar/{aluno_id}")
def validar_aluno(aluno_id: int, validado: bool = True, db: Session = Depends(get_db)):
    """
    Valida ou invalida um aluno (atualiza is_professor).
    
    Parâmetros:
    - aluno_id: int → ID do aluno
    - validado: bool → True para validar, False para invalidar
    - db: Session → sessão do banco (injeção de dependência)
    
    Retorna:
    - Mensagem de sucesso
    """
    aluno = db.query(Student).filter(Student.id == aluno_id).first()
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    aluno.is_professor = validado
    db.commit()
    db.refresh(aluno)
    
    return {
        "mensagem": f"Aluno '{aluno.nome}' {'validado' if validado else 'invalidado'} com sucesso",
        "id": aluno.id,
        "check_professor": aluno.is_professor
    }