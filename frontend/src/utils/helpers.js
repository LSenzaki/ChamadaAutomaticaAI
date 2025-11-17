/**
 * Converte um objeto Blob para base64
 * @param {Blob} blob - O blob a ser convertido
 * @returns {Promise<string>} - String base64 do blob
 */
export const blobToBase64 = (blob) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result.split(',')[1]);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
};

/**
 * Captura um frame do elemento de vídeo
 * @param {HTMLVideoElement} videoElement - Elemento de vídeo
 * @param {number} width - Largura da captura
 * @param {number} height - Altura da captura
 * @returns {Promise<Blob>} - Blob da imagem capturada
 */
export const captureVideoFrame = (videoElement, width = 640, height = 480) => {
  return new Promise((resolve) => {
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const context = canvas.getContext('2d');
    context.drawImage(videoElement, 0, 0, width, height);
    canvas.toBlob(resolve, 'image/jpeg');
  });
};

/**
 * Formata a data para exibição
 * @param {string} dateString - String de data ISO
 * @returns {string} - Data formatada
 */
export const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('pt-BR');
};

/**
 * Formata a data e hora para exibição
 * @param {string} dateString - String de data ISO
 * @returns {string} - Data e hora formatadas
 */
export const formatDateTime = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString('pt-BR');
};

/**
 * Formata apenas a hora
 * @param {string} dateString - String de data ISO
 * @returns {string} - Hora formatada
 */
export const formatTime = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
};

/**
 * Valida se uma string está vazia ou é nula
 * @param {string} str - String a ser validada
 * @returns {boolean} - true se válida
 */
export const isValidString = (str) => {
  return str && str.trim().length > 0;
};

/**
 * Calcula a porcentagem de confiança
 * @param {number} confidence - Valor de confiança (0-100)
 * @returns {number} - Porcentagem arredondada
 */
export const calculateConfidencePercent = (confidence) => {
  return Math.round(confidence);
};
