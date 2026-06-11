import { useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import Navbar from '../components/common/Navbar';
import instructivoVideo from '../videos/Instructivo.mp4';
import WeeklyLeaderboard from '../components/common/WeeklyLeaderboard';

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
      
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
        <div className="bg-gradient-to-r from-teal-600 to-teal-700 rounded-2xl shadow-lg p-8 text-white">
          <h1 className="text-3xl font-bold">
            Video instructivo
          </h1>

          <p className="mt-2 text-teal-100">
            Aprende paso a paso cómo traducir correctamente en Mbo'ehara Digital mediante este video explicativo.
          </p>
        </div>
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
          
          <div className="mt-6 p-4 bg-teal-50 border border-teal-200 rounded-lg">
            <h3 className="font-semibold text-teal-900 mb-2">Instrucciones principales:</h3>
            <ul className="text-sm text-teal-800 space-y-2">
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

        {/* Contact Section */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Contactos del equipo:</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Contact Card 1 */}
            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-2xl">📧</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">Carlos Lugo</h3>
                  <span 
                    className="text-blue-600 hover:text-blue-800 text-sm break-all"
                  >
                    carlos.luugoo@gmail.com
                  </span>
                </div>
              </div>
            </div>

            {/* Contact Card 2 */}
            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-pink-100 rounded-full flex items-center justify-center">
                  <span className="text-2xl">📧</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">Raquel Insfran</h3>
                  <span 
                    className="text-blue-600 hover:text-blue-800 text-sm break-all"
                  >
                    raquelinsfran17@gmail.com
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="hidden xl:block absolute top-28 right-3">
        <WeeklyLeaderboard />
      </div>
    </div>
  );
};

export default HelpPage;
