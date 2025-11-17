PROJETO DE RECONHECIMENTO FACIAL DOS ALUNOS DO BIOPARK

OBJETIVO
O objetivo é conseguir integrar um sistema automático de reconhecimento dos alunos com o sistema usado pelos professores para automatizar o 
registro de presença dos alunos.

BIBLIOTECAS
**Sistema Híbrido**: face_recognition + DeepFace
(Combina velocidade do face_recognition com precisão de validação do DeepFace)

---

## 🚀 Sistema Híbrido de Reconhecimento (NOVO!)

O sistema agora utiliza uma **estratégia híbrida inteligente** que combina o melhor dos dois mundos:

### ⚡ Estratégia SMART (Padrão)
1. **Face Recognition primeiro** (rápido - 0.09s)
2. **Alta confiança (>60%)**: Aceita imediatamente
3. **Confiança média (40-60%)**: Valida com DeepFace
4. **Baixa confiança (<40%)**: DeepFace como autoridade
5. **Não encontrou**: DeepFace como fallback

**Resultado:** ~0.3s em média (vs 0.09s só FR ou 1.7s só DF)

### 📊 Modos Disponíveis
- **smart** (Recomendado): Velocidade + precisão balanceada
- **always_both**: Máxima precisão, sempre usa ambos
- **fallback**: Máxima velocidade, DF apenas em falhas

**📖 [Documentação Completa do Sistema Híbrido](HYBRID_SYSTEM.md)**

---

## 📊 Comparação Face Recognition vs DeepFace

Foi realizada uma comparação abrangente entre as bibliotecas **face_recognition** e **DeepFace**.

### 🏆 Vencedor: Face Recognition
- **Precisão: 77.6%** vs DeepFace 54.1%
- **F1 Score: 0.813** vs DeepFace 0.477
- **Velocidade: ~0.09s** vs DeepFace ~1.7s
- Melhor equilíbrio entre precisão e recall

**📂 Estrutura da Comparação:**
- **[📑 Índice & Navegação](tests/comparison_results/INDEX.md)** - Comece por aqui!
- **[📖 Documentação Completa](tests/comparison_results/README.md)** - Análise completa (30+ páginas)
- **[🚀 Guia de Início Rápido](tests/comparison_results/QUICKSTART.md)** - Reproduza o teste
- **[📊 Gráficos](tests/comparison_results/graphics/)** - 6 visualizações profissionais
- **[💾 Dados dos Resultados](tests/comparison_results/data/test_results.json)** - JSON estruturado

**Detalhes do Teste:**
- 429 imagens testadas (30 celebridades conhecidas + 15 desconhecidas)
- Face Recognition: 77.6% de precisão, 208 identificações corretas
- DeepFace: 54.1% de precisão, 90 identificações corretas (perdeu 68.5% dos rostos conhecidos)

---

ESTRUTURA DO PROJETO

project_root/app/                        # Código principal da aplicação FastAPI
project_root/app/main.py                 # Ponto de entrada da aplicação

project_root/app/routers/                     # Endpoints da API
project_root/app/routers/__init__.py     
project_root/app/routers/faces.py             # Rotas de reconhecimento facial
project_root/app/routers/students.py          # Rotas CRUD de estudantes e registros

project_root/app/services/                    # Regras de negócio
project_root/app/services/__init__.py
project_root/app/services/hybrid_face_service.py  # 🆕 Sistema híbrido FR + DF
project_root/app/services/face_service.py     # Funções que utilizam face_recognition
project_root/app/services/deepface_service.py # 🆕 Funções que utilizam DeepFace
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
