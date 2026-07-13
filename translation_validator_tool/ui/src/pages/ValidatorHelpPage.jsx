import { useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import Navbar from '../components/common/Navbar';
import instructivoVideo from '../videos/Validaciones.mp4';

const ValidatorHelpPage = () => {
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      console.log('Validator help page loaded for user:', user.username);
    }
  }, [user]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="bg-gradient-to-r from-teal-600 to-teal-700 rounded-2xl shadow-lg p-8 text-white">
            <h1 className="text-3xl font-bold">
              Video instructivo
            </h1>

            <p className="mt-2 text-teal-100">
              Aprende paso a paso cómo validar traducciones en Mbo'ehara Digital mediante este video explicativo.
            </p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="w-full bg-gray-900 rounded-lg overflow-hidden">
            <div className="relative w-full" style={{ paddingTop: '56.25%' }}>
              <video
                src={instructivoVideo}
                title="Video instructivo para validadores"
                className="absolute inset-0 w-full h-full border-0"
                controls
                style={{ width: '100%', height: '100%' }}
              />
            </div>
          </div>

          <div className="mt-6 p-4 bg-teal-50 border border-teal-200 rounded-lg">
            <h3 className="font-semibold text-teal-900 mb-2">Instrucciones principales para validadores:</h3>
            <ul className="text-sm text-teal-800 space-y-2">
              <li>• En la sección "Validar" se muestra una traducción pendiente asignada para evaluación.</li>
              <li>• Revisa cuidadosamente el texto original en español y la traducción propuesta en guaraní.</li>
              <li>• Indica si la traducción es correcta, incorrecta o regular según la calidad del contenido.</li>
              <li>• Si marcas la traducción como regular, selecciona el motivo que mejor describa el problema.</li>
              <li>• Asigna una puntuación de fluidez considerando qué tan natural suena el texto en guaraní.</li>
              <li>• Asigna una puntuación de precisión considerando qué tan fiel es la traducción al texto en español.</li>
              <li>• Usa el campo de notas si es necesario para explicar observaciones importantes o justificar tu evaluación cuando sea necesario.</li>
              <li>• Cuando la traducción tenga problemas, puedes sugerir una versión mejorada desde el botón "¿Quieres sugerir una traducción?".</li>
              <li>• Antes de enviar, verifica que hayas seleccionado corrección, fluidez y precisión.</li>
              <li>• Presiona "Enviar evaluación" para registrar tu validación; después se te asignará otra traducción si hay disponibles.</li>
              <li>• Si no deseas evaluar la traducción actual, usa "Pasar a la siguiente evaluación" para omitirla y recibir otra asignación.</li>
            </ul>
          </div>

          <p className="text-sm text-gray-600 mt-6">
            Si tienes dudas o necesitas más ayuda, no dudes en contactarnos.
          </p>
        </div>

        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Contactos del equipo:</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-2xl">📧</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">Carlos Lugo</h3>
                  <span className="text-blue-600 hover:text-blue-800 text-sm break-all">
                    carlos.luugoo@gmail.com
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-pink-100 rounded-full flex items-center justify-center">
                  <span className="text-2xl">📧</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">Raquel Insfran</h3>
                  <span className="text-blue-600 hover:text-blue-800 text-sm break-all">
                    raquelinsfran17@gmail.com
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ValidatorHelpPage;
