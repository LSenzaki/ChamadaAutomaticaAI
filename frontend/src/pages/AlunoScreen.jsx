import React, { useState } from 'react';
import SelecionarTurma from './SelecionarTurma';
import TelaReconhecimento from './TelaReconhecimento';

/**
 * Tela principal do Aluno (Reconhecimento em Stream)
 */
const AlunoScreen = () => {
  const [turmaSelecionada, setTurmaSelecionada] = useState(null);
  const [chamadaIniciada, setChamadaIniciada] = useState(false);

  if (!chamadaIniciada) {
    return (
      <SelecionarTurma
        setTurmaSelecionada={setTurmaSelecionada}
        setChamadaIniciada={setChamadaIniciada}
      />
    );
  }

  return (
    <TelaReconhecimento
      turma={turmaSelecionada}
      setChamadaIniciada={setChamadaIniciada}
    />
  );
};

export default AlunoScreen;
