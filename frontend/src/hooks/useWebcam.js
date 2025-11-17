import { useState, useRef, useCallback } from 'react';

/**
 * Hook customizado para gerenciar a webcam
 * @returns {Object} - Objeto com estados e funções da webcam
 */
export const useWebcam = () => {
  const [webcamAtiva, setWebcamAtiva] = useState(false);
  const [erro, setErro] = useState(null);
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  const iniciarWebcam = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: 640, height: 480 }
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setWebcamAtiva(true);
        setErro(null);
      }
    } catch (err) {
      console.error('Erro ao acessar webcam:', err);
      setErro('Erro ao acessar a webcam. Verifique as permissões.');
      setWebcamAtiva(false);
    }
  }, []);

  const pararWebcam = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setWebcamAtiva(false);
  }, []);

  return {
    videoRef,
    webcamAtiva,
    erro,
    iniciarWebcam,
    pararWebcam
  };
};
