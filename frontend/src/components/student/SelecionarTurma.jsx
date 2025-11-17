import React, { useState, useEffect } from 'react';
import { BookOpen, Search } from 'lucide-react';
import { API_URL } from '../../constants';

/**
 * Componente para seleção de turma antes de iniciar a chamada
 */
const SelecionarTurma = ({ setTurmaSelecionada, setChamadaIniciada }) => {
  const [turmas, setTurmas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busca, setBusca] = useState('');

  useEffect(() => {
    carregarTurmas();
  }, []);

  const carregarTurmas = async () => {
    try {
      const response = await fetch(`${API_URL}/turmas/`);
      const data = await response.json();
      setTurmas(data);
    } catch (err) {
      alert('Erro ao carregar turmas: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const iniciarChamada = (turma) => {
    setTurmaSelecionada(turma);
    setChamadaIniciada(true);
  };

  const turmasFiltradas = turmas.filter(turma => 
    turma.nome.toLowerCase().includes(busca.toLowerCase())
  );

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
          <BookOpen className="w-6 h-6" />
          Iniciar Chamada - Selecione a Turma
        </h2>

        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Buscar turma..."
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            />
          </div>
        </div>

        {loading ? (
          <p className="text-center py-8 text-gray-500">Carregando turmas...</p>
        ) : turmasFiltradas.length === 0 ? (
          <div className="text-center py-8 text-gray-500 bg-gray-50 rounded-lg">
            <p className="font-semibold">Nenhuma turma encontrada</p>
            {busca && <p className="text-sm mt-2">Tente buscar com outros termos</p>}
          </div>
        ) : (
          <div className="grid gap-3 max-h-[500px] overflow-y-auto">
            {turmasFiltradas.map(turma => (
              <button
                key={turma.id}
                onClick={() => iniciarChamada(turma)}
                className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all text-left group"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-bold text-gray-800 group-hover:text-blue-600">
                      {turma.nome}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">
                      ID: {turma.id}
                    </p>
                  </div>
                  <div className="text-blue-500 opacity-0 group-hover:opacity-100 transition-opacity">
                    →
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SelecionarTurma;
