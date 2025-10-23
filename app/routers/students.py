"""
students.py
------------
Router responsável pelo gerenciamento de alunos.
Atualizado para usar os modelos Student e FaceEmbedding.
"""

from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException
from sqlalchemy.orm import Session # Mantemos o Depends(get_db) por enquanto
from app.services.face_service import get_face_encoding
from app.models.db_session import get_db
from app.models import db_models # Importar o módulo db_models para usar os modelos
from app.services.db_service import Database, Settings
import json
import uvicorn # Adicionei uvicorn aqui para evitar erro de import circular em main.py

# Inicializa o Database Service globalmente
# Nota: Em apps maiores, isso deve ser injetado como dependência
settings = Settings.from_env()
db_manager = Database(settings)

router = APIRouter(prefix="/students", tags=["students"])

@router.post("/cadastrar")
async def cadastrar(
    nome: str = Form(...), 
    is_professor: bool = Form(False), # Novo campo para verificar se é professor
    foto: UploadFile = None,
    db: Session = Depends(get_db) # Mantive a sessão para compatibilidade, mas vamos usar db_manager
):
    """
    Cadastra um aluno (ou professor) no banco de dados com a codificação facial.
    """     
    if not foto:
        raise HTTPException(status_code=400, detail="Imagem obrigatória")

    # 1. Obter o encoding facial
    encoding = get_face_encoding(foto)
    if encoding is None:
        raise HTTPException(status_code=400, detail="Nenhum rosto detectado")

    # 2. Criar o registro do Aluno/Professor (usando a função do db_service)
    # Nota: db_service que você enviou não tem 'is_professor', vamos adaptar a chamada
    try:
        # Tenta usar o serviço para criar o aluno
        new_student = db_manager.create_student(
            external_id=None, # Podemos definir uma lógica para isso depois
            nome=nome
        )
        # NOVO students.py (dentro de cadastrar):
        # ...
        # 3. Adicionar o embedding
        # O embedding deve ser enviado como uma string JSON para o db_service.
        # FaceEncoding é um array, transformamos em lista, serializamos em JSON string,
        # e colocamos em uma lista (porque add_embeddings espera List[List[float]]).
        # Vamos simplificar: o db_service deve receber a lista de embeddings prontos para salvar.

        # 1. Obter o encoding facial (numpy array)
        encoding = get_face_encoding(foto) 

        # 2. Converte o encoding (numpy array) para uma string JSON
        encoding_json_string = json.dumps(encoding.tolist()) 

        # 3. Chamar a função de serviço com a string JSON
        # Nota: precisamos adaptar o db_service para receber a string em vez da lista
        db_manager.add_embedding(student_id=new_student.id, vector_json=encoding_json_string) 
        # ...
        
        # 4. (Opcional) Se houver necessidade de salvar o is_professor:
        # Como o db_service.create_student não tem o parâmetro 'is_professor',
        # vamos fazer o update manual (ou atualizar o db_service para incluir o parâmetro)
        # Vamos assumir que você prefere a função mais simples por enquanto.
        # Se precisar de update de professor, comente ou avise para adaptar.

    except Exception as e:
         # Logar o erro 'e' para debug real
         raise HTTPException(status_code=500, detail=f"Erro ao cadastrar: {e}")


    return {"mensagem": f"{nome} cadastrado com sucesso!", "id": new_student.id}


@router.get("/chamadas/listar")
def listar_todas_chamadas(db: Session = Depends(get_db)):
    """
    Retorna a lista de TODOS os registros de chamada.
    Ideal para o painel de visualização do professor.
    """
    registros = db_manager.list_all_attendance()
    
    if not registros:
        return []

    return [
        {
            "id": r.id,
            "student_id": r.student_id,
            "nome_aluno": r.student.nome, # Usando a relação carregada
            "timestamp": r.timestamp.isoformat(),
            "session_tag": r.session_tag,
            "confidence": r.confidence,
            # Assumindo que você tem 'is_validated' ou 'check_professor' na AttendanceRecord
            "validado_professor": r.check_professor if hasattr(r, 'check_professor') else False 
        }
        for r in registros
    ]


# O endpoint de remover precisa ser adaptado também para usar o db_service.
# Como você não me enviou a função de remoção no db_service, vamos usar uma versão
# simplificada por enquanto.
@router.delete("/remover/{aluno_id}")
def remover_aluno(aluno_id: int, db: Session = Depends(get_db)):
    """
    Remove um aluno e todos os seus embeddings e registros de chamada associados.
    """
    # A remoção em cascata (cascade="all, delete-orphan") garante que o ORM remova
    # embeddings e chamadas quando o student é removido.
    aluno = db.query(db_models.Student).filter(db_models.Student.id == aluno_id).first()
    
    if not aluno:
        raise HTTPException(status_code=404, detail="Aluno não encontrado")
    
    db.delete(aluno)
    db.commit()
    return {"mensagem": f"Aluno '{aluno.nome}' removido com sucesso"}

@router.patch("/chamadas/validar/{chamada_id}")
def validar_chamada_professor(chamada_id: int, db: Session = Depends(get_db)):
    # ...
    
    # Busca o registro de chamada usando .get()
    # O chamda_id já deve ser um INT devido à assinatura da função.
    chamada = db.get(db_models.AttendanceRecord, chamada_id) 

    if not chamada:
        # Se a busca falhar, levanta o 404 que você está vendo
        raise HTTPException(status_code=404, detail="Registro de chamada não encontrado")
    
    # 2. Verifica se já está validado (opcional)
    if chamada.check_professor is True:
        return {"mensagem": f"Chamada {chamada_id} já está validada."}

    # 3. Altera o status e salva
    chamada.check_professor = True
    
    db.add(chamada) # Sinaliza ao ORM que o objeto foi modificado
    db.commit()
    db.refresh(chamada)
    
    return {
        "mensagem": f"Chamada {chamada_id} validada pelo professor.",
        "id": chamada.id,
        "validado": chamada.check_professor,
        "aluno_id": chamada.student_id
    }