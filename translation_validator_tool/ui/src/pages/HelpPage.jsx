import { useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import Navbar from '../components/common/Navbar';
import instructivoVideo from '../videos/Instructivo.mp4';

const HelpPage = () => {
  const { user } = useAuth();

  useEffect(() => {
    // Verificar que el usuario está autenticado
    if (user) {
      console.log('Help page loaded for user:', user.username);
    }
  }, [user]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Video instructivo</h1>
          <p className="mt-2 text-gray-600">
              A continuación se muestra un video con instrucciones detalladas para traducir correctamente en Mbo'ehara Digital.
          </p>
        </div>

        {/* Video Container */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          
          <div className="w-full bg-gray-900 rounded-lg overflow-hidden">
            <div className="relative w-full" style={{ paddingTop: '56.25%' }}>
              <video
                src={instructivoVideo}
                title="Video instructivo"
                className="absolute inset-0 w-full h-full border-0"
                controls
                style={{ width: '100%', height: '100%' }}
              />
            </div>
          </div>
          
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">Instrucciones principales:</h3>
            <ul className="text-sm text-blue-800 space-y-2">
             <li>• Todas las enunciados pendientes se muestran en un listado en la sección de "Traducciones pendientes".</li>
             <li>• Para traducir el enunciado seleccionado, haz click en el botón "Traducir" situado a la derecha de cada enunciado.</li>
              <li>• Posteriormente, revisa cuidadosamente cada enunciado.</li>
              <li>• Traduce al guaraní de manera precisa y natural.</li>
              <li>• Utiliza los caracteres especiales cuando sea necesario, las tienes disponibles en la barra de herramientas.</li>
              <li>• La traduccion debe tener una longintud similar a la oración en español.</li>
              <li>• No se podrán enviar traducciones vacías o incompletas.</li>
              <li>• Una vez traducido, presiona el botón "Enviar traduccion".</li>
              <li>• Si deseas descartar la traducción, haz click en "Ignorar".</li>
              <li>• Los enunciados traducidos o ignorados, ya no se encontra disponibles en la sección "Traducciones pendientes", ni tampoco en la sección "Mis pendientes".</li>
            </ul>
          </div>

          <p className="text-sm text-gray-600 mt-6">
            Si tienes dudas o necesitas más ayuda, no dudes en contactarnos.
          </p>
        </div>
      </div>
    </div>
  );
};

export default HelpPage;
