import React, { useState, useRef, useEffect } from 'react';
import { Camera, Users, UserCheck, Upload, Trash2, CheckCircle, XCircle, Video, VideoOff, BookOpen, Search, Calendar } from 'lucide-react';

const API_URL = 'http://localhost:8000';

// Componente: Tela do Aluno (Reconhecimento em Stream)
const AlunoScreen = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [streaming, setStreaming] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (streaming) {
      startCamera();
    } else {
      stopCamera();
    }
    return () => stopCamera();
  }, [streaming]);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      alert('Erro ao acessar câmera: ' + err.message);
      setStreaming(false);
    }
  };

  const stopCamera = () => {
    if (videoRef.current?.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
  };

  const capturarEReconhecer = async () => {
    if (!videoRef.current) return;
    
    const canvas = canvasRef.current;
    const video = videoRef.current;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    
    canvas.toBlob(async (blob) => {
      setLoading(true);
      const formData = new FormData();
      formData.append('foto', blob, 'captura.jpg');

      try {
        const response = await fetch(`${API_URL}/faces/reconhecer`, {
          method: 'POST',
          body: formData
        });
        const data = await response.json();
        setResultado(data);
      } catch (err) {
        alert('Erro ao reconhecer: ' + err.message);
      } finally {
        setLoading(false);
      }
    });
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
          <Camera className="w-6 h-6" />
          Reconhecimento de Presença
        </h2>
        
        <div className="mb-4">
          <button
            onClick={() => setStreaming(!streaming)}
            className={`px-6 py-3 rounded-lg font-semibold flex items-center gap-2 ${
              streaming ? 'bg-red-500 hover:bg-red-600' : 'bg-blue-500 hover:bg-blue-600'
            } text-white`}
          >
            {streaming ? <VideoOff className="w-5 h-5" /> : <Video className="w-5 h-5" />}
            {streaming ? 'Parar Câmera' : 'Iniciar Câmera'}
          </button>
        </div>

        {streaming && (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-full rounded-lg mb-4 bg-black"
            />
            <button
              onClick={capturarEReconhecer}
              disabled={loading}
              className="w-full bg-green-500 hover:bg-green-600 text-white font-semibold py-3 rounded-lg disabled:opacity-50"
            >
              {loading ? 'Reconhecendo...' : 'Registrar Presença'}
            </button>
          </>
        )}
        
        <canvas ref={canvasRef} className="hidden" />
        
        {resultado && (
          <div className={`mt-6 p-4 rounded-lg ${
            resultado.mais_provavel ? 'bg-green-50 border-2 border-green-500' : 'bg-red-50 border-2 border-red-500'
          }`}>
            {resultado.mais_provavel ? (
              <>
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                  <h3 className="text-xl font-bold text-green-800">Presença Registrada!</h3>
                </div>
                <p className="text-lg">Nome: <strong>{resultado.mais_provavel.nome}</strong></p>
                <p className="text-sm text-gray-600">
                  Confiança: {resultado.mais_provavel.similaridade}%
                </p>
              </>
            ) : (
              <>
                <div className="flex items-center gap-2 mb-2">
                  <XCircle className="w-6 h-6 text-red-600" />
                  <h3 className="text-xl font-bold text-red-800">Não Reconhecido</h3>
                </div>
                <p>{resultado.mensagem || 'Aluno não encontrado'}</p>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Componente: Tela do Professor
const ProfessorScreen = () => {
  const [menuAtual, setMenuAtual] = useState('menu');
  
  return (
    <div className="p-6 max-w-7xl mx-auto">
      {menuAtual === 'menu' ? (
        <ProfessorMenu setMenuAtual={setMenuAtual} />
      ) : menuAtual === 'validar-alunos' ? (
        <ValidarAlunos setMenuAtual={setMenuAtual} />
      ) : menuAtual === 'validar-presencas' ? (
        <ValidarPresencas setMenuAtual={setMenuAtual} />
      ) : null}
    </div>
  );
};

// Menu Principal do Professor
const ProfessorMenu = ({ setMenuAtual }) => {
  const menuItems = [
    { id: 'validar-alunos', titulo: 'Validar Alunos', descricao: 'Aprovar cadastro de novos alunos', icon: UserCheck, cor: 'blue' },
    { id: 'validar-presencas', titulo: 'Validar Presenças', descricao: 'Revisar e validar presenças por data', icon: CheckCircle, cor: 'green' }
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-3xl font-bold mb-8 text-center text-gray-800">Painel do Professor</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
        {menuItems.map(item => {
          const Icon = item.icon;
          const bgColor = item.cor === 'blue' ? 'bg-blue-50 hover:bg-blue-100 border-blue-200 hover:border-blue-400' : 
                          'bg-green-50 hover:bg-green-100 border-green-200 hover:border-green-400';
          const iconColor = item.cor === 'blue' ? 'text-blue-600' : 'text-green-600';
          
          return (
            <button
              key={item.id}
              onClick={() => setMenuAtual(item.id)}
              className={`p-6 rounded-xl border-2 ${bgColor} transition-all duration-200 transform hover:scale-105 text-left`}
            >
              <Icon className={`w-12 h-12 ${iconColor} mb-4`} />
              <h3 className="text-xl font-bold text-gray-800 mb-2">{item.titulo}</h3>
              <p className="text-sm text-gray-600">{item.descricao}</p>
            </button>
          );
        })}
      </div>
    </div>
  );
};

// Tela: Validar Alunos
const ValidarAlunos = ({ setMenuAtual }) => {
  const [alunos, setAlunos] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    carregarAlunos();
  }, []);

  const carregarAlunos = async () => {
    try {
      const response = await fetch(`${API_URL}/students/listar`);
      const data = await response.json();
      setAlunos(data);
    } catch (err) {
      alert('Erro ao carregar alunos: ' + err.message);
    }
  };

  const validarAluno = async (id, validado) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/students/validar/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ validado })
      });
      await response.json();
      await carregarAlunos();
    } catch (err) {
      alert('Erro ao validar: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <UserCheck className="w-6 h-6" />
          Validação de Alunos
        </h2>
        <button
          onClick={() => setMenuAtual('menu')}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg font-semibold transition-colors"
        >
          ← Voltar ao Menu
        </button>
      </div>

      <div className="mb-4 p-4 bg-blue-50 rounded-lg">
        <p className="text-sm text-blue-800">
          <strong>Instruções:</strong> Valide os alunos cadastrados para permitir que façam chamada.
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-3 text-left">ID</th>
              <th className="p-3 text-left">Nome</th>
              <th className="p-3 text-left">Status</th>
              <th className="p-3 text-center">Ações</th>
            </tr>
          </thead>
          <tbody>
            {alunos.map(aluno => (
              <tr key={aluno.id} className="border-t hover:bg-gray-50">
                <td className="p-3">{aluno.id}</td>
                <td className="p-3">{aluno.nome}</td>
                <td className="p-3">
                  {aluno.check_professor ? (
                    <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">
                      Validado
                    </span>
                  ) : (
                    <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-sm">
                      Pendente
                    </span>
                  )}
                </td>
                <td className="p-3 text-center">
                  <div className="flex gap-2 justify-center">
                    {!aluno.check_professor ? (
                      <button
                        onClick={() => validarAluno(aluno.id, true)}
                        disabled={loading}
                        className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded disabled:opacity-50"
                      >
                        Validar
                      </button>
                    ) : (
                      <button
                        onClick={() => validarAluno(aluno.id, false)}
                        disabled={loading}
                        className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded disabled:opacity-50"
                      >
                        Invalidar
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Tela: Validar Presenças com Calendário
const ValidarPresencas = ({ setMenuAtual }) => {
  const [presencas, setPresencas] = useState([]);
  const [dataSelecionada, setDataSelecionada] = useState(null);
  const [mesAtual, setMesAtual] = useState(new Date());
  const [turmaSelecionada, setTurmaSelecionada] = useState(null);
  const [loading, setLoading] = useState(false);

  const meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];

  const carregarPresencas = async (data) => {
    setLoading(true);
    try {
      const dataFormatada = data.toISOString().split('T')[0];
      const response = await fetch(`${API_URL}/attendance/date/${dataFormatada}`);
      const data_response = await response.json();
      setPresencas(data_response);
    } catch (err) {
      console.error('Erro ao carregar presenças:', err);
      setPresencas([]);
    } finally {
      setLoading(false);
    }
  };

  const validarPresenca = async (id, validado) => {
    try {
      await fetch(`${API_URL}/attendance/${id}/validate`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ validado })
      });
      if (dataSelecionada) {
        carregarPresencas(dataSelecionada);
      }
    } catch (err) {
      alert('Erro ao validar presença: ' + err.message);
    }
  };

  // Agrupa presenças por turma
  const presencasPorTurma = presencas.reduce((acc, presenca) => {
    const turmaId = presenca.turma_id || 'sem_turma';
    const turmaNome = presenca.turma_nome || 'Sem Turma';
    const professorNome = presenca.professor_nome || 'Não atribuído';
    
    if (!acc[turmaId]) {
      acc[turmaId] = {
        turmaId,
        turmaNome,
        professorNome,
        presencas: []
      };
    }
    acc[turmaId].presencas.push(presenca);
    return acc;
  }, {});

  const turmasComPresenca = Object.values(presencasPorTurma);

  const getDiasDoMes = () => {
    const ano = mesAtual.getFullYear();
    const mes = mesAtual.getMonth();
    const primeiroDia = new Date(ano, mes, 1);
    const ultimoDia = new Date(ano, mes + 1, 0);
    const diasNoMes = ultimoDia.getDate();
    const diaDaSemanaInicio = primeiroDia.getDay();

    const dias = [];
    // Preenche dias vazios antes do início do mês
    for (let i = 0; i < diaDaSemanaInicio; i++) {
      dias.push(null);
    }
    // Preenche os dias do mês
    for (let dia = 1; dia <= diasNoMes; dia++) {
      dias.push(new Date(ano, mes, dia));
    }
    return dias;
  };

  const mudarMes = (direcao) => {
    const novoMes = new Date(mesAtual);
    novoMes.setMonth(mesAtual.getMonth() + direcao);
    setMesAtual(novoMes);
  };

  const selecionarDia = (data) => {
    setDataSelecionada(data);
    setTurmaSelecionada(null);
    carregarPresencas(data);
  };

  const formatarData = (data) => {
    return data.toLocaleDateString('pt-BR', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const formatarHora = (dataHora) => {
    if (!dataHora) return 'N/A';
    return new Date(dataHora).toLocaleTimeString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const ehHoje = (data) => {
    if (!data) return false;
    const hoje = new Date();
    return data.toDateString() === hoje.toDateString();
  };

  const ehDataSelecionada = (data) => {
    if (!data || !dataSelecionada) return false;
    return data.toDateString() === dataSelecionada.toDateString();
  };

  const presencasFiltradas = turmaSelecionada 
    ? presencas.filter(p => (p.turma_id || 'sem_turma') === turmaSelecionada)
    : presencas;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <CheckCircle className="w-6 h-6" />
          Validar Presenças
        </h2>
        <button
          onClick={() => setMenuAtual('menu')}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg font-semibold transition-colors"
        >
          ← Voltar ao Menu
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendário */}
        <div className="lg:col-span-1">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <button
                onClick={() => mudarMes(-1)}
                className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
              >
                ←
              </button>
              <h3 className="text-lg font-bold text-gray-800">
                {meses[mesAtual.getMonth()]} {mesAtual.getFullYear()}
              </h3>
              <button
                onClick={() => mudarMes(1)}
                className="p-2 hover:bg-gray-200 rounded-lg transition-colors"
              >
                →
              </button>
            </div>

            <div className="grid grid-cols-7 gap-1 mb-2">
              {['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'].map(dia => (
                <div key={dia} className="text-center text-xs font-semibold text-gray-600 py-2">
                  {dia}
                </div>
              ))}
            </div>

            <div className="grid grid-cols-7 gap-1">
              {getDiasDoMes().map((data, index) => (
                <button
                  key={index}
                  onClick={() => data && selecionarDia(data)}
                  disabled={!data}
                  className={`
                    aspect-square p-2 text-sm rounded-lg transition-all
                    ${!data ? 'invisible' : ''}
                    ${ehHoje(data) ? 'bg-blue-100 font-bold text-blue-800' : ''}
                    ${ehDataSelecionada(data) ? 'bg-green-500 text-white font-bold' : ''}
                    ${!ehDataSelecionada(data) && !ehHoje(data) && data ? 'hover:bg-gray-200 text-gray-700' : ''}
                  `}
                >
                  {data?.getDate()}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Lista de Presenças */}
        <div className="lg:col-span-2">
          {!dataSelecionada ? (
            <div className="flex items-center justify-center h-full bg-gray-50 rounded-lg p-8">
              <div className="text-center text-gray-500">
                <Calendar className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <p className="text-lg font-semibold">Selecione uma data no calendário</p>
                <p className="text-sm mt-2">Clique em um dia para ver as presenças</p>
              </div>
            </div>
          ) : (
            <div>
              <div className="mb-4 p-4 bg-green-50 rounded-lg">
                <h3 className="font-bold text-green-800 capitalize">
                  {formatarData(dataSelecionada)}
                </h3>
                <p className="text-sm text-green-600 mt-1">
                  {presencas.length} presença(s) em {turmasComPresenca.length} turma(s)
                </p>
              </div>

              {loading ? (
                <p className="text-center py-8 text-gray-500">Carregando presenças...</p>
              ) : presencas.length === 0 ? (
                <div className="text-center py-8 text-gray-500 bg-gray-50 rounded-lg">
                  <p className="font-semibold">Nenhuma presença registrada neste dia</p>
                </div>
              ) : (
                <div className="space-y-6 max-h-[600px] overflow-y-auto">
                  {/* Lista de turmas */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    <button
                      onClick={() => setTurmaSelecionada(null)}
                      className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                        turmaSelecionada === null 
                          ? 'bg-purple-600 text-white' 
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                    >
                      Todas ({presencas.length})
                    </button>
                    {turmasComPresenca.map(turmaInfo => (
                      <button
                        key={turmaInfo.turmaId}
                        onClick={() => setTurmaSelecionada(turmaInfo.turmaId)}
                        className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                          turmaSelecionada === turmaInfo.turmaId 
                            ? 'bg-purple-600 text-white' 
                            : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                        }`}
                      >
                        {turmaInfo.turmaNome} ({turmaInfo.presencas.length})
                      </button>
                    ))}
                  </div>

                  {/* Presenças agrupadas por turma */}
                  {turmasComPresenca
                    .filter(turmaInfo => !turmaSelecionada || turmaInfo.turmaId === turmaSelecionada)
                    .map(turmaInfo => (
                      <div key={turmaInfo.turmaId} className="border-2 border-purple-200 rounded-lg p-4 bg-purple-50">
                        {/* Cabeçalho da Turma */}
                        <div className="mb-4 pb-3 border-b-2 border-purple-200">
                          <div className="flex items-center justify-between">
                            <div>
                              <h3 className="text-xl font-bold text-purple-900">
                                {turmaInfo.turmaNome}
                              </h3>
                              <p className="text-sm text-purple-700 mt-1">
                                <span className="font-semibold">Professor Designado:</span> {turmaInfo.professorNome}
                              </p>
                            </div>
                            <span className="px-3 py-1 bg-purple-600 text-white rounded-full text-sm font-semibold">
                              {turmaInfo.presencas.length} {turmaInfo.presencas.length === 1 ? 'aluno' : 'alunos'}
                            </span>
                          </div>
                        </div>

                        {/* Lista de presenças da turma */}
                        <div className="space-y-3">
                          {turmaInfo.presencas.map(presenca => (
                            <div key={presenca.id} className="bg-white border-2 border-gray-200 rounded-lg p-4 hover:border-green-400 transition-colors">
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center gap-3 mb-2">
                                    <h4 className="text-lg font-bold text-gray-800">{presenca.aluno_nome}</h4>
                                    {presenca.check_professor ? (
                                      <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">
                                        ✓ Validado
                                      </span>
                                    ) : (
                                      <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-semibold">
                                        ⏳ Pendente
                                      </span>
                                    )}
                                  </div>
                                  
                                  <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                                    <div>
                                      <span className="font-semibold">ID Aluno:</span> {presenca.aluno_id}
                                    </div>
                                    <div>
                                      <span className="font-semibold">Horário:</span> {formatarHora(presenca.data_hora)}
                                    </div>
                                    <div>
                                      <span className="font-semibold">Confiança:</span> {presenca.confianca}%
                                    </div>
                                    <div>
                                      <span className="font-semibold">ID Presença:</span> {presenca.id}
                                    </div>
                                  </div>
                                </div>

                                <div className="ml-4">
                                  {!presenca.check_professor ? (
                                    <button
                                      onClick={() => validarPresenca(presenca.id, true)}
                                      className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white rounded-lg font-semibold transition-colors flex items-center gap-2"
                                    >
                                      <CheckCircle className="w-4 h-4" />
                                      Validar
                                    </button>
                                  ) : (
                                    <button
                                      onClick={() => validarPresenca(presenca.id, false)}
                                      className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-semibold transition-colors flex items-center gap-2"
                                    >
                                      <XCircle className="w-4 h-4" />
                                      Invalidar
                                    </button>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Menu Principal do Admin
const AdminMenu = ({ setMenuAtual }) => {
  const menuItems = [
    { id: 'registrar', titulo: 'Registrar Aluno', descricao: 'Cadastrar novo aluno com nome e fotos', icon: Users, cor: 'blue' },
    { id: 'registrar-professor', titulo: 'Registrar Professor', descricao: 'Cadastrar professor e atribuir turmas', icon: UserCheck, cor: 'orange' },
    { id: 'turmas', titulo: 'Criar Turmas', descricao: 'Criar e gerenciar turmas/classes', icon: BookOpen, cor: 'green' },
    { id: 'listar', titulo: 'Turmas e Alunos', descricao: 'Ver lista de turmas e seus alunos', icon: Search, cor: 'purple' }
  ];

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-3xl font-bold mb-8 text-center text-gray-800">Painel Administrativo</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {menuItems.map(item => {
          const Icon = item.icon;
          const bgColor = item.cor === 'blue' ? 'bg-blue-50 hover:bg-blue-100 border-blue-200 hover:border-blue-400' : 
                          item.cor === 'green' ? 'bg-green-50 hover:bg-green-100 border-green-200 hover:border-green-400' :
                          item.cor === 'orange' ? 'bg-orange-50 hover:bg-orange-100 border-orange-200 hover:border-orange-400' :
                          'bg-purple-50 hover:bg-purple-100 border-purple-200 hover:border-purple-400';
          const iconColor = item.cor === 'blue' ? 'text-blue-600' : 
                            item.cor === 'green' ? 'text-green-600' : 
                            item.cor === 'orange' ? 'text-orange-600' : 'text-purple-600';
          
          return (
            <button
              key={item.id}
              onClick={() => setMenuAtual(item.id)}
              className={`p-6 rounded-xl border-2 ${bgColor} transition-all duration-200 transform hover:scale-105 text-left`}
            >
              <Icon className={`w-12 h-12 ${iconColor} mb-4`} />
              <h3 className="text-xl font-bold text-gray-800 mb-2">{item.titulo}</h3>
              <p className="text-sm text-gray-600">{item.descricao}</p>
            </button>
          );
        })}
      </div>
    </div>
  );
};

// Tela: Registrar Aluno
const RegistrarAluno = ({ setMenuAtual }) => {
  const [nome, setNome] = useState('');
  const [fotos, setFotos] = useState([]);
  const [turmas, setTurmas] = useState([]);
  const [turmaSelecionada, setTurmaSelecionada] = useState('');
  const [buscaTurma, setBuscaTurma] = useState('');
  const [mostrarDropdown, setMostrarDropdown] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    carregarTurmas();
  }, []);

  const carregarTurmas = async () => {
    try {
      const response = await fetch(`${API_URL}/classes/`);
      const data = await response.json();
      setTurmas(data);
    } catch (err) {
      console.error('Erro ao carregar turmas:', err);
    }
  };

  const handleFotosChange = (e) => {
    const arquivos = Array.from(e.target.files);
    setFotos(arquivos);
  };

  const turmasFiltradas = turmas.filter(turma =>
    turma.nome.toLowerCase().includes(buscaTurma.toLowerCase())
  );

  const selecionarTurma = (turma) => {
    setTurmaSelecionada(turma.id);
    setBuscaTurma(turma.nome);
    setMostrarDropdown(false);
  };

  const cadastrarAluno = async () => {
    if (!nome || fotos.length === 0) {
      alert('Preencha o nome e adicione pelo menos uma foto');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('nome', nome);
    if (turmaSelecionada) {
      formData.append('turma_id', turmaSelecionada);
    }
    
    // Adiciona múltiplas fotos
    fotos.forEach((foto) => {
      formData.append('fotos', foto);
    });

    try {
      const response = await fetch(`${API_URL}/students/cadastrar`, {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      alert(`Aluno cadastrado com sucesso! ${fotos.length} foto(s) enviada(s).`);
      setNome('');
      setFotos([]);
      setTurmaSelecionada('');
      setBuscaTurma('');
      document.getElementById('file-input').value = '';
    } catch (err) {
      alert('Erro ao cadastrar aluno: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Users className="w-6 h-6" />
          Registrar Novo Aluno
        </h2>
        <button
          onClick={() => setMenuAtual('menu')}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg font-semibold transition-colors"
        >
          ← Voltar ao Menu
        </button>
      </div>

      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <label className="block text-sm font-medium mb-2 text-gray-700">Nome do Aluno</label>
          <input
            type="text"
            value={nome}
            onChange={(e) => setNome(e.target.value)}
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Digite o nome completo"
          />
        </div>

        <div className="relative">
          <label className="block text-sm font-medium mb-2 text-gray-700">
            Turma <span className="text-gray-500">(Opcional)</span>
          </label>
          <input
            type="text"
            value={buscaTurma}
            onChange={(e) => {
              setBuscaTurma(e.target.value);
              setMostrarDropdown(true);
              if (!e.target.value) {
                setTurmaSelecionada('');
              }
            }}
            onFocus={() => setMostrarDropdown(true)}
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Buscar turma..."
          />
          
          {mostrarDropdown && turmasFiltradas.length > 0 && (
            <div className="absolute z-10 w-full mt-1 bg-white border-2 border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
              {turmasFiltradas.map(turma => (
                <button
                  key={turma.id}
                  type="button"
                  onClick={() => selecionarTurma(turma)}
                  className="w-full text-left px-4 py-3 hover:bg-blue-50 transition-colors border-b border-gray-100 last:border-b-0"
                >
                  <div className="font-semibold text-gray-800">{turma.nome}</div>
                  <div className="text-xs text-gray-500">ID: {turma.id}</div>
                </button>
              ))}
            </div>
          )}
          
          {turmaSelecionada && (
            <div className="mt-2 flex items-center gap-2">
              <span className="text-sm text-green-700 bg-green-50 px-3 py-1 rounded-full">
                ✓ Turma selecionada: {turmas.find(t => t.id === turmaSelecionada)?.nome}
              </span>
              <button
                type="button"
                onClick={() => {
                  setTurmaSelecionada('');
                  setBuscaTurma('');
                }}
                className="text-sm text-red-600 hover:text-red-800 underline"
              >
                Remover
              </button>
            </div>
          )}
          
          {turmas.length === 0 && (
            <p className="mt-2 text-sm text-gray-500">
              Nenhuma turma cadastrada ainda. Crie uma turma primeiro.
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium mb-2 text-gray-700">
            Fotos do Aluno <span className="text-gray-500">(Múltiplas fotos aumentam a precisão)</span>
          </label>
          <input
            id="file-input"
            type="file"
            accept="image/*"
            multiple
            onChange={handleFotosChange}
            className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          {fotos.length > 0 && (
            <div className="mt-3 p-3 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800 font-semibold">
                {fotos.length} foto(s) selecionada(s):
              </p>
              <ul className="mt-2 text-sm text-gray-700 max-h-32 overflow-y-auto">
                {fotos.map((foto, idx) => (
                  <li key={idx} className="truncate">• {foto.name}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <button
          onClick={cadastrarAluno}
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? 'Cadastrando...' : 'Cadastrar Aluno'}
        </button>
      </div>
    </div>
  );
};

// Tela: Registrar Professor
const RegistrarProfessor = ({ setMenuAtual }) => {
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [turmas, setTurmas] = useState([]);
  const [turmasSelecionadas, setTurmasSelecionadas] = useState([]);
  const [professores, setProfessores] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    carregarTurmas();
    carregarProfessores();
  }, []);

  const carregarTurmas = async () => {
    try {
      const response = await fetch(`${API_URL}/classes/`);
      const data = await response.json();
      setTurmas(data);
    } catch (err) {
      console.error('Erro ao carregar turmas:', err);
    }
  };

  const carregarProfessores = async () => {
    try {
      const response = await fetch(`${API_URL}/professors/`);
      const data = await response.json();
      setProfessores(data);
    } catch (err) {
      console.error('Erro ao carregar professores:', err);
    }
  };

  const toggleTurma = (turmaId) => {
    setTurmasSelecionadas(prev => 
      prev.includes(turmaId) 
        ? prev.filter(id => id !== turmaId)
        : [...prev, turmaId]
    );
  };

  const cadastrarProfessor = async () => {
    if (!nome.trim() || !email.trim()) {
      alert('Preencha o nome e email do professor');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/professors/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          nome, 
          email,
          turma_ids: turmasSelecionadas 
        })
      });
      const data = await response.json();
      alert('Professor cadastrado com sucesso!');
      setNome('');
      setEmail('');
      setTurmasSelecionadas([]);
      carregarProfessores();
    } catch (err) {
      alert('Erro ao cadastrar professor: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const removerProfessor = async (id) => {
    if (!window.confirm('Deseja realmente remover este professor?')) return;

    try {
      await fetch(`${API_URL}/professors/${id}`, {
        method: 'DELETE'
      });
      alert('Professor removido com sucesso!');
      carregarProfessores();
    } catch (err) {
      alert('Erro ao remover professor: ' + err.message);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <UserCheck className="w-6 h-6" />
          Registrar Professor
        </h2>
        <button
          onClick={() => setMenuAtual('menu')}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg font-semibold transition-colors"
        >
          ← Voltar ao Menu
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Formulário de Cadastro */}
        <div>
          <div className="bg-orange-50 p-6 rounded-lg space-y-4">
            <h3 className="text-lg font-bold text-orange-800 mb-4">Cadastrar Novo Professor</h3>
            
            <div>
              <label className="block text-sm font-medium mb-2 text-gray-700">Nome Completo</label>
              <input
                type="text"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                className="w-full px-4 py-3 border-2 border-orange-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="Digite o nome completo"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-700">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border-2 border-orange-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                placeholder="professor@exemplo.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2 text-gray-700">
                Turmas Atribuídas <span className="text-gray-500">(Opcional)</span>
              </label>
              {turmas.length === 0 ? (
                <p className="text-sm text-gray-500 bg-white p-3 rounded-lg">
                  Nenhuma turma cadastrada ainda. Crie turmas primeiro.
                </p>
              ) : (
                <div className="bg-white border-2 border-orange-200 rounded-lg p-3 max-h-48 overflow-y-auto">
                  {turmas.map(turma => (
                    <label 
                      key={turma.id} 
                      className="flex items-center gap-3 p-2 hover:bg-orange-50 rounded cursor-pointer transition-colors"
                    >
                      <input
                        type="checkbox"
                        checked={turmasSelecionadas.includes(turma.id)}
                        onChange={() => toggleTurma(turma.id)}
                        className="w-5 h-5 text-orange-600 rounded focus:ring-orange-500"
                      />
                      <span className="text-sm font-medium text-gray-800">{turma.nome}</span>
                    </label>
                  ))}
                </div>
              )}
              {turmasSelecionadas.length > 0 && (
                <p className="mt-2 text-sm text-orange-700 bg-orange-100 px-3 py-1 rounded">
                  {turmasSelecionadas.length} turma(s) selecionada(s)
                </p>
              )}
            </div>

            <button
              onClick={cadastrarProfessor}
              disabled={loading}
              className="w-full bg-orange-600 hover:bg-orange-700 text-white font-semibold py-4 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Cadastrando...' : 'Cadastrar Professor'}
            </button>
          </div>
        </div>

        {/* Lista de Professores */}
        <div>
          <h3 className="text-lg font-bold mb-4 text-gray-800">Professores Cadastrados</h3>
          {professores.length === 0 ? (
            <p className="text-center text-gray-500 py-8 bg-gray-50 rounded-lg">
              Nenhum professor cadastrado ainda
            </p>
          ) : (
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {professores.map(professor => (
                <div key={professor.id} className="border-2 border-gray-200 rounded-lg p-4 hover:border-orange-400 transition-colors">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h4 className="text-lg font-bold text-gray-800">{professor.nome}</h4>
                      <p className="text-sm text-gray-600">{professor.email}</p>
                    </div>
                    <button
                      onClick={() => removerProfessor(professor.id)}
                      className="px-3 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm flex items-center gap-1 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                      Remover
                    </button>
                  </div>
                  
                  {professor.turmas && professor.turmas.length > 0 ? (
                    <div className="mt-2">
                      <p className="text-xs font-semibold text-gray-600 mb-1">Turmas:</p>
                      <div className="flex flex-wrap gap-1">
                        {professor.turmas.map(turma => (
                          <span 
                            key={turma.id} 
                            className="text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded-full"
                          >
                            {turma.nome}
                          </span>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <p className="text-xs text-gray-500 italic">Sem turmas atribuídas</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Tela: Criar Turmas
const CriarTurmas = ({ setMenuAtual }) => {
  const [turmas, setTurmas] = useState([]);
  const [nomeTurma, setNomeTurma] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    carregarTurmas();
  }, []);

  const carregarTurmas = async () => {
    try {
      const response = await fetch(`${API_URL}/classes/`);
      const data = await response.json();
      setTurmas(data);
    } catch (err) {
      console.error('Erro ao carregar turmas:', err);
    }
  };

  const criarTurma = async () => {
    if (!nomeTurma.trim()) {
      alert('Digite o nome da turma');
      return;
    }

    setLoading(true);
    try {
      await fetch(`${API_URL}/classes/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome: nomeTurma })
      });
      alert('Turma criada com sucesso!');
      setNomeTurma('');
      carregarTurmas();
    } catch (err) {
      alert('Erro ao criar turma: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const removerTurma = async (id) => {
    if (!window.confirm('Deseja realmente remover esta turma?')) return;

    try {
      await fetch(`${API_URL}/classes/${id}`, {
        method: 'DELETE'
      });
      alert('Turma removida com sucesso!');
      carregarTurmas();
    } catch (err) {
      alert('Erro ao remover turma: ' + err.message);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <BookOpen className="w-6 h-6" />
          Gerenciar Turmas
        </h2>
        <button
          onClick={() => setMenuAtual('menu')}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg font-semibold transition-colors"
        >
          ← Voltar ao Menu
        </button>
      </div>

      <div className="max-w-4xl mx-auto space-y-6">
        <div className="bg-green-50 p-6 rounded-lg">
          <h3 className="text-lg font-bold mb-4 text-green-800">Criar Nova Turma</h3>
          <div className="flex gap-3">
            <input
              type="text"
              value={nomeTurma}
              onChange={(e) => setNomeTurma(e.target.value)}
              className="flex-1 px-4 py-3 border-2 border-green-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              placeholder="Ex: IA 1º Ano, Data Science 3º Ano"
            />
            <button
              onClick={criarTurma}
              disabled={loading}
              className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg disabled:opacity-50 transition-colors"
            >
              {loading ? 'Criando...' : 'Criar Turma'}
            </button>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-bold mb-4 text-gray-800">Turmas Cadastradas</h3>
          {turmas.length === 0 ? (
            <p className="text-center text-gray-500 py-8">Nenhuma turma cadastrada ainda</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {turmas.map(turma => (
                <div key={turma.id} className="p-4 border-2 border-gray-200 rounded-lg hover:border-green-400 transition-colors">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-bold text-lg text-gray-800">{turma.nome}</h4>
                      <p className="text-sm text-gray-500">ID: {turma.id}</p>
                    </div>
                    <button
                      onClick={() => removerTurma(turma.id)}
                      className="px-3 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm flex items-center gap-1 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                      Remover
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Tela: Listar Turmas e Alunos
const ListarTurmasAlunos = ({ setMenuAtual }) => {
  const [turmas, setTurmas] = useState([]);
  const [alunos, setAlunos] = useState([]);
  const [turmaSelecionada, setTurmaSelecionada] = useState(null);
  const [busca, setBusca] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    carregarTurmas();
    carregarAlunos();
  }, []);

  const carregarTurmas = async () => {
    try {
      const response = await fetch(`${API_URL}/classes/`);
      const data = await response.json();
      setTurmas(data);
    } catch (err) {
      console.error('Erro ao carregar turmas:', err);
    }
  };

  const carregarAlunos = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/students/listar`);
      const data = await response.json();
      setAlunos(data);
    } catch (err) {
      console.error('Erro ao carregar alunos:', err);
    } finally {
      setLoading(false);
    }
  };

  const alunosFiltrados = alunos.filter(aluno => {
    const matchBusca = aluno.nome.toLowerCase().includes(busca.toLowerCase());
    const matchTurma = turmaSelecionada ? aluno.turma_id === turmaSelecionada : true;
    return matchBusca && matchTurma;
  });

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold flex items-center gap-2">
          <Search className="w-6 h-6" />
          Turmas e Alunos
        </h2>
        <button
          onClick={() => setMenuAtual('menu')}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg font-semibold transition-colors"
        >
          ← Voltar ao Menu
        </button>
      </div>

      <div className="space-y-6">
        {/* Filtros */}
        <div className="bg-gray-50 p-4 rounded-lg space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-700">
              <Search className="w-4 h-4 inline mr-2" />
              Buscar Aluno
            </label>
            <input
              type="text"
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              className="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Digite o nome do aluno..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2 text-gray-700">Filtrar por Turma</label>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setTurmaSelecionada(null)}
                className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                  turmaSelecionada === null ? 'bg-purple-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Todas as Turmas
              </button>
              {turmas.map(turma => (
                <button
                  key={turma.id}
                  onClick={() => setTurmaSelecionada(turma.id)}
                  className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                    turmaSelecionada === turma.id ? 'bg-purple-600 text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {turma.nome}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Lista de Alunos */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-800">
              Alunos {turmaSelecionada && `- ${turmas.find(t => t.id === turmaSelecionada)?.nome}`}
            </h3>
            <span className="text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
              {alunosFiltrados.length} aluno(s) encontrado(s)
            </span>
          </div>

          {loading ? (
            <p className="text-center py-8 text-gray-500">Carregando...</p>
          ) : alunosFiltrados.length === 0 ? (
            <p className="text-center py-8 text-gray-500">Nenhum aluno encontrado</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="p-3 text-left">ID</th>
                    <th className="p-3 text-left">Nome</th>
                    <th className="p-3 text-left">Turma</th>
                    <th className="p-3 text-left">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {alunosFiltrados.map(aluno => (
                    <tr key={aluno.id} className="border-t hover:bg-gray-50 transition-colors">
                      <td className="p-3 text-gray-700">{aluno.id}</td>
                      <td className="p-3 font-semibold text-gray-800">{aluno.nome}</td>
                      <td className="p-3 text-gray-600">
                        {aluno.turma_id ? turmas.find(t => t.id === aluno.turma_id)?.nome || 'N/A' : 'Sem turma'}
                      </td>
                      <td className="p-3">
                        {aluno.check_professor ? (
                          <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold">
                            ✓ Validado
                          </span>
                        ) : (
                          <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-semibold">
                            ⏳ Pendente
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Componente: Tela do Admin
const AdminScreen = () => {
  const [menuAtual, setMenuAtual] = useState('menu');
  
  return (
    <div className="p-6 max-w-7xl mx-auto">
      {menuAtual === 'menu' ? (
        <AdminMenu setMenuAtual={setMenuAtual} />
      ) : menuAtual === 'registrar' ? (
        <RegistrarAluno setMenuAtual={setMenuAtual} />
      ) : menuAtual === 'registrar-professor' ? (
        <RegistrarProfessor setMenuAtual={setMenuAtual} />
      ) : menuAtual === 'turmas' ? (
        <CriarTurmas setMenuAtual={setMenuAtual} />
      ) : menuAtual === 'listar' ? (
        <ListarTurmasAlunos setMenuAtual={setMenuAtual} />
      ) : null}
    </div>
  );
};

// Componente Principal (App)
const App = () => {
  const [tela, setTela] = useState('aluno');

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-blue-600 text-white p-4 shadow-lg">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold">Sistema de Chamada Automática</h1>
          <div className="flex gap-2">
            <button
              onClick={() => setTela('aluno')}
              className={`px-4 py-2 rounded font-semibold transition-colors ${
                tela === 'aluno' ? 'bg-white text-blue-600' : 'bg-blue-500 hover:bg-blue-400'
              }`}
            >
              Aluno
            </button>
            <button
              onClick={() => setTela('professor')}
              className={`px-4 py-2 rounded font-semibold transition-colors ${
                tela === 'professor' ? 'bg-white text-blue-600' : 'bg-blue-500 hover:bg-blue-400'
              }`}
            >
              Professor
            </button>
            <button
              onClick={() => setTela('admin')}
              className={`px-4 py-2 rounded font-semibold transition-colors ${
                tela === 'admin' ? 'bg-white text-blue-600' : 'bg-blue-500 hover:bg-blue-400'
              }`}
            >
              Admin
            </button>
          </div>
        </div>
      </nav>

      <main>
        {tela === 'aluno' && <AlunoScreen />}
        {tela === 'professor' && <ProfessorScreen />}
        {tela === 'admin' && <AdminScreen />}
      </main>
    </div>
  );
};

export default App;
