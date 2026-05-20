// Página para Enviar Código
import { useState } from 'react';
import { useParams } from 'react-router-dom';

const LANGUAGES = [
  { value: 'python', label: 'Python' },
  { value: 'java', label: 'Java' },
  { value: 'cpp', label: 'C++' },
  { value: 'javascript', label: 'JavaScript' },
  { value: 'csharp', label: 'C#' },
];

export const SubmitCodePage = () => {
  const { assignmentId } = useParams();
  const [language, setLanguage] = useState('python');
  const [code, setCode] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // TODO: Llamar a API de envío
      setMessage('Código enviado exitosamente');
      setCode('');
    } catch (err) {
      setMessage('Error al enviar el código');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">Enviar Código</h1>

        {message && (
          <div
            className={`p-4 rounded mb-6 ${
              message.includes('exitosamente')
                ? 'bg-green-100 text-green-700'
                : 'bg-red-100 text-red-700'
            }`}
          >
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 space-y-6">
          <div>
            <label className="block text-gray-700 font-semibold mb-2">
              Lenguaje de Programación
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            >
              {LANGUAGES.map((lang) => (
                <option key={lang.value} value={lang.value}>
                  {lang.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-gray-700 font-semibold mb-2">
              Código
            </label>
            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              className="w-full h-96 px-4 py-2 border border-gray-300 rounded-lg font-mono text-sm focus:outline-none focus:border-blue-500"
              placeholder="Pega tu código aquí..."
              required
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting || !code}
            className="w-full bg-blue-600 text-white font-bold py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {isSubmitting ? 'Enviando...' : 'Enviar Código'}
          </button>
        </form>
      </div>
    </div>
  );
};
