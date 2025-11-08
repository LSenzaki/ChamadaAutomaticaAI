import React, { useState, useRef, useEffect } from 'react';
import { Camera, Users, UserCheck, Upload, Trash2, CheckCircle, XCircle, Video, VideoOff } from 'lucide-react';

const API_URL = 'http://localhost:8001';
0
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
    }
  };

  const stopCamera = () => {
    if (videoRef.current?.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(track => track.stop());
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
      formData.append('foto', blob, 'capture.jpg');
      
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
      const response = await fetch(`${API_URL}/students/validar/${id}?validado=${validado}`, {
        method: 'PUT'
      });
      const data = await response.json();
      
      if (response.ok) {
        alert(data.mensagem);
        await carregarAlunos();
      } else {
        alert('Erro: ' + (data.detail || 'Falha na validação'));
      }
    } catch (err) {
      alert('Erro ao validar: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
          <UserCheck className="w-6 h-6" />
          Validação de Alunos - Professor
        </h2>

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
    </div>
  );
};

// Componente: Tela do Admin
const AdminScreen = () => {
  const [alunos, setAlunos] = useState([]);
  const [nome, setNome] = useState('');
  const [foto, setFoto] = useState(null);
  const [fotoTeste, setFotoTeste] = useState(null);
  const [loading, setLoading] = useState(false);
  const [resultadoTeste, setResultadoTeste] = useState(null);

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

  const cadastrarAluno = async () => {
    if (!nome || !foto) {
      alert('Preencha nome e foto');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('nome', nome);
    formData.append('foto', foto);

    try {
      const response = await fetch(`${API_URL}/students/cadastrar`, {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      alert(data.mensagem);
      setNome('');
      setFoto(null);
      await carregarAlunos();
    } catch (err) {
      alert('Erro ao cadastrar: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const removerAluno = async (id) => {
    if (!window.confirm('Deseja realmente remover este aluno?')) return;

    try {
      const response = await fetch(`${API_URL}/students/remover/${id}`, {
        method: 'DELETE'
      });
      const data = await response.json();
      alert(data.mensagem);
      await carregarAlunos();
    } catch (err) {
      alert('Erro ao remover: ' + err.message);
    }
  };

  const testarReconhecimento = async () => {
    if (!fotoTeste) {
      alert('Selecione uma foto para teste');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('foto', fotoTeste);

    try {
      const response = await fetch(`${API_URL}/faces/reconhecer`, {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      setResultadoTeste(data);
    } catch (err) {
      alert('Erro ao testar: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      {/* Cadastro */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
          <Users className="w-6 h-6" />
          Cadastrar Aluno
        </h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Nome</label>
            <input
              type="text"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Nome do aluno"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Foto</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setFoto(e.target.files[0])}
              className="w-full px-4 py-2 border rounded-lg"
            />
          </div>
          <button
            onClick={cadastrarAluno}
            disabled={loading}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 rounded-lg disabled:opacity-50"
          >
            {loading ? 'Cadastrando...' : 'Cadastrar Aluno'}
          </button>
        </div>
      </div>

      {/* Lista de Alunos */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6">Alunos Cadastrados</h2>
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
                    <button
                      onClick={() => removerAluno(aluno.id)}
                      className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded flex items-center gap-2 mx-auto"
                    >
                      <Trash2 className="w-4 h-4" />
                      Remover
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Teste de Reconhecimento */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
          <Upload className="w-6 h-6" />
          Testar Reconhecimento
        </h2>
        <div className="space-y-4">
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setFotoTeste(e.target.files[0])}
            className="w-full px-4 py-2 border rounded-lg"
          />
          <button
            onClick={testarReconhecimento}
            disabled={loading}
            className="w-full bg-purple-500 hover:bg-purple-600 text-white font-semibold py-3 rounded-lg disabled:opacity-50"
          >
            {loading ? 'Testando...' : 'Testar Reconhecimento'}
          </button>
        </div>

        {resultadoTeste && (
          <div className={`mt-6 p-4 rounded-lg ${
            resultadoTeste.mais_provavel ? 'bg-green-50 border-2 border-green-500' : 'bg-red-50 border-2 border-red-500'
          }`}>
            {resultadoTeste.mais_provavel ? (
              <>
                <h3 className="text-xl font-bold mb-2">Reconhecido!</h3>
                <p><strong>Nome:</strong> {resultadoTeste.mais_provavel.nome}</p>
                <p><strong>ID:</strong> {resultadoTeste.mais_provavel.id}</p>
                <p><strong>Confiança:</strong> {resultadoTeste.mais_provavel.similaridade}%</p>
              </>
            ) : (
              <>
                <h3 className="text-xl font-bold mb-2">Não Reconhecido</h3>
                <p>{resultadoTeste.mensagem}</p>
              </>
            )}
          </div>
        )}
      </div>
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
              className={`px-4 py-2 rounded font-semibold ${
                tela === 'aluno' ? 'bg-white text-blue-600' : 'bg-blue-500 hover:bg-blue-400'
              }`}
            >
              Aluno
            </button>
            <button
              onClick={() => setTela('professor')}
              className={`px-4 py-2 rounded font-semibold ${
                tela === 'professor' ? 'bg-white text-blue-600' : 'bg-blue-500 hover:bg-blue-400'
              }`}
            >
              Professor
            </button>
            <button
              onClick={() => setTela('admin')}
              className={`px-4 py-2 rounded font-semibold ${
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