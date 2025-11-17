# Contribuindo para o Sistema de Reconhecimento Facial

Obrigado por considerar contribuir para este projeto! Este documento fornece diretrizes para contribuições.

## 📋 Índice

- [Código de Conduta](#código-de-conduta)
- [Como Posso Contribuir?](#como-posso-contribuir)
- [Processo de Desenvolvimento](#processo-de-desenvolvimento)
- [Padrões de Código](#padrões-de-código)
- [Commits e Pull Requests](#commits-e-pull-requests)
- [Testes](#testes)

## 📜 Código de Conduta

Este projeto adere a um código de conduta. Ao participar, espera-se que você mantenha este código.

### Nossos Padrões

- Usar linguagem acolhedora e inclusiva
- Respeitar pontos de vista e experiências diferentes
- Aceitar críticas construtivas graciosamente
- Focar no que é melhor para a comunidade
- Mostrar empatia com outros membros da comunidade

## 🤝 Como Posso Contribuir?

### Reportando Bugs

Antes de criar um relatório de bug, verifique se o problema já não foi reportado. Se encontrar um problema existente, adicione comentários relevantes.

**Ao criar um relatório de bug, inclua:**

- Descrição clara e descritiva do problema
- Passos para reproduzir o comportamento
- Comportamento esperado vs comportamento atual
- Screenshots (se aplicável)
- Informações do ambiente (SO, versão do Python/Node, etc.)

### Sugerindo Melhorias

Melhorias são rastreadas como issues do GitHub. Ao criar uma sugestão:

- Use um título claro e descritivo
- Forneça uma descrição detalhada da melhoria proposta
- Explique por que essa melhoria seria útil
- Liste exemplos de onde isso seria usado

### Pull Requests

1. Fork o repositório
2. Crie uma branch a partir de `Develop`
3. Faça suas alterações
4. Teste suas alterações
5. Commit com mensagens claras (veja convenções abaixo)
6. Push para sua branch
7. Abra um Pull Request

## 🔄 Processo de Desenvolvimento

### Estrutura de Branches

```
main         - Produção estável
  └── Develop       - Desenvolvimento ativo
      ├── feature/  - Novas funcionalidades
      ├── fix/      - Correções de bugs
      └── refactor/ - Refatorações
```

### Workflow

1. **Crie uma branch**:
   ```bash
   git checkout Develop
   git pull origin Develop
   git checkout -b feature/nome-da-funcionalidade
   ```

2. **Desenvolva e teste**:
   - Faça commits frequentes com mensagens descritivas
   - Execute testes localmente
   - Certifique-se de que o código segue os padrões

3. **Atualize sua branch**:
   ```bash
   git fetch origin
   git rebase origin/Develop
   ```

4. **Push e PR**:
   ```bash
   git push origin feature/nome-da-funcionalidade
   # Abra PR no GitHub apontando para Develop
   ```

## 💻 Padrões de Código

### Python (Backend)

**Estilo**: PEP 8

```python
# ✅ BOM
def calculate_confidence(distance: float) -> float:
    """
    Calcula a porcentagem de confiança baseada na distância.
    
    Args:
        distance: Distância euclidiana entre embeddings
        
    Returns:
        Porcentagem de confiança (0-100)
    """
    return max(0, 100 - (distance * 100))

# ❌ RUIM
def calc_conf(d):
    return max(0,100-(d*100))
```

**Regras**:
- Use type hints em todas as funções
- Docstrings em formato Google
- Máximo de 120 caracteres por linha
- Imports organizados: stdlib, third-party, local
- Use f-strings para formatação

### JavaScript/React (Frontend)

**Estilo**: ESLint + Prettier

```javascript
// ✅ BOM
/**
 * Captura um frame do vídeo e retorna como blob
 * @param {HTMLVideoElement} videoElement - Elemento de vídeo
 * @param {number} width - Largura da captura
 * @returns {Promise<Blob>} Blob da imagem
 */
const captureFrame = async (videoElement, width = 640) => {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  // ...
  return await canvas.toBlob();
};

// ❌ RUIM
const capture = (v, w) => {
  var c = document.createElement('canvas');
  c.width = w
  return c.toBlob()
}
```

**Regras**:
- Componentes funcionais com hooks
- PropTypes ou JSDoc para props
- 2 espaços de indentação
- Use const/let, nunca var
- Nomes descritivos para variáveis e funções

### SQL

```sql
-- ✅ BOM
CREATE TABLE IF NOT EXISTS presencas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aluno_id UUID NOT NULL REFERENCES alunos(id) ON DELETE CASCADE,
    turma_id UUID NOT NULL REFERENCES turmas(id) ON DELETE CASCADE,
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 100),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_presencas_aluno ON presencas(aluno_id);
CREATE INDEX idx_presencas_turma ON presencas(turma_id);
```

## 📝 Commits e Pull Requests

### Conventional Commits

Usamos o padrão Conventional Commits:

```
<tipo>[escopo opcional]: <descrição>

[corpo opcional]

[rodapé opcional]
```

**Tipos**:
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação (sem mudança de código)
- `refactor`: Refatoração de código
- `perf`: Melhoria de performance
- `test`: Adição ou correção de testes
- `chore`: Tarefas de manutenção

**Exemplos**:

```bash
feat(api): adiciona endpoint para edição de professor
fix(frontend): corrige cálculo de confiança duplicado
docs(readme): atualiza instruções de instalação
refactor(backend): reorganiza estrutura de pastas
test(services): adiciona testes para hybrid_face_service
```

### Pull Request

**Título**: Use Conventional Commits

**Descrição**: Inclua:
- O que foi mudado e por quê
- Como testar as mudanças
- Screenshots (se UI)
- Issues relacionadas (#123)

**Template**:

```markdown
## Descrição
Breve descrição das mudanças

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova funcionalidade
- [ ] Breaking change
- [ ] Documentação

## Como Testar
1. Passo 1
2. Passo 2

## Checklist
- [ ] Código segue os padrões do projeto
- [ ] Testes foram adicionados/atualizados
- [ ] Documentação foi atualizada
- [ ] Sem warnings de lint
- [ ] Todas as tests passam

## Issues Relacionadas
Fixes #123
```

## 🧪 Testes

### Backend (Python)

```bash
cd backend
source ../.venv/bin/activate
pytest tests/ -v
pytest tests/ --cov=app  # Com cobertura
```

**Estrutura de Teste**:

```python
# tests/test_face_service.py
import pytest
from app.services.face_service import calculate_confidence

def test_calculate_confidence_perfect_match():
    """Testa confiança com distância zero (match perfeito)"""
    assert calculate_confidence(0.0) == 100.0

def test_calculate_confidence_no_match():
    """Testa confiança com distância alta (sem match)"""
    assert calculate_confidence(1.0) == 0.0
```

### Frontend (Jest/React Testing Library)

```bash
cd frontend
npm test
npm test -- --coverage  # Com cobertura
```

**Estrutura de Teste**:

```javascript
// src/components/student/SelecionarTurma.test.js
import { render, screen, waitFor } from '@testing-library/react';
import SelecionarTurma from './SelecionarTurma';

test('renders turma selection title', () => {
  render(<SelecionarTurma />);
  const titleElement = screen.getByText(/Iniciar Chamada/i);
  expect(titleElement).toBeInTheDocument();
});

test('loads and displays turmas', async () => {
  // Mock fetch
  global.fetch = jest.fn(() =>
    Promise.resolve({
      json: () => Promise.resolve([{ id: 1, nome: 'Turma A' }]),
    })
  );

  render(<SelecionarTurma />);
  
  await waitFor(() => {
    expect(screen.getByText('Turma A')).toBeInTheDocument();
  });
});
```

## 📚 Recursos Adicionais

- [Documentação do Projeto](http://localhost:8001)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Python PEP 8](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

## ❓ Dúvidas?

Se tiver dúvidas, sinta-se à vontade para:
- Abrir uma issue com a tag `question`
- Entrar em contato com os mantenedores

Obrigado por contribuir! 🎉
