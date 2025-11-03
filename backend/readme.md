PROJETO DE RECONHECIMENTO FACIAL DOS ALUNOS DO BIOPARK

OBJETIVO
O objetivo é conseguir integrar um sistema automático de reconhecimento dos alunos com o sistema usado pelos professores para automatizar o 
registro de presença dos alunos.

BIBLIOTECAS
Face Recognition

ESTRUTURA DO PROJETO

project_root/app/                        # Código principal da aplicação FastAPI
project_root/app/main.py                 # Ponto de entrada da aplicação

project_root/app/routers/                     # Endpoints da API
project_root/app/routers/__init__.py     
project_root/app/routers/faces.py             # Rotas de reconhecimento facial
project_root/app/routers/students.py          # Rotas CRUD de estudantes e registros

project_root/app/services/                    # Regras de negócio
project_root/app/services/__init__.py
project_root/app/services/face_service.py     # Funções que utilizam face_recognition
project_root/app/services/db_service.py       # Operações com o banco de dados

project_root/app/models/                      # Modelos do banco de dados
project_root/app/models/db_models.py          # Modelos SQLAlchemy

project_root/app/schemas/                     # Modelos de validação (Pydantic)
project_root/app/schemas/pydantic_schemas.py  # Schemas para entrada/saída da API

project_root/data/                            # Armazenamento de imagens

project_root/data/known_faces/                # Fotos conhecidas (para encoding)
project_root/data/unknown_faces/              # Fotos capturadas via webcam

project_root/requirements.txt                 # Dependências do projeto
project_root/Dockerfile                       # Arquivo para containerização (opcional)
project_root/README.md                        # Documentação do projeto

PROBLEMAS
1 - Instalação da biblioteca em windows e Mac:
31/08/25 - Conseguimos fazer funcionar no windows a biblioteca.

CONCLUSÃO
