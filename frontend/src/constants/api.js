export const API_URL = 'http://localhost:8000';

export const ENDPOINTS = {
  // Alunos
  ALUNOS: '/alunos/',
  ALUNO_BY_ID: (id) => `/alunos/${id}`,
  ALUNO_REGISTRO: '/alunos/registrar',
  ALUNO_RECONHECIMENTO: '/alunos/reconhecer',
  
  // Professores
  PROFESSORES: '/professores/',
  PROFESSOR_BY_ID: (id) => `/professores/${id}`,
  
  // Turmas
  TURMAS: '/turmas/',
  TURMA_BY_ID: (id) => `/turmas/${id}`,
  TURMA_ALUNOS: (id) => `/turmas/${id}/alunos`,
  
  // Presenças
  PRESENCAS: '/presencas/',
  PRESENCAS_HOJE: '/presencas/hoje',
  PRESENCAS_TURMA: (turmaId) => `/presencas/turma/${turmaId}`,
  PRESENCA_BY_ID: (id) => `/presencas/${id}`,
};
