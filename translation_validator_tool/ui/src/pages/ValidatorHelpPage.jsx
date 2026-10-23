import Navbar from '../components/common/Navbar';

const ValidatorHelpPage = () => (
  <div className="min-h-screen bg-gray-50">
    <Navbar />
    <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <header className="mb-8 rounded-2xl bg-gradient-to-r from-teal-600 to-teal-700 p-8 text-white shadow-lg">
        <h1 className="text-3xl font-bold">Guía de validación</h1>
        <p className="mt-2 text-teal-100">Revisa traducciones y registra una evaluación de su calidad.</p>
      </header>
      <section className="rounded-lg bg-white p-6 shadow-lg">
        <h2 className="mb-4 text-xl font-bold text-gray-900">Cómo validar una traducción</h2>
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
        <p className="mt-6 rounded-lg border border-teal-200 bg-teal-50 p-4 text-sm text-teal-900">
          Si necesitas ayuda con tu cuenta o con una evaluación, consulta al administrador de esta instancia.
        </p>
      </section>
    </main>
  </div>
);

export default ValidatorHelpPage;
