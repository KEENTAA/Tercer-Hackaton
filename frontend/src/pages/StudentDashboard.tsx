// Dashboard de Estudiante
import { useEffect } from 'react';
import { useAuthStore } from '../stores/useStore';

export const StudentDashboard = () => {
  const user = useAuthStore((state) => state.user);

  useEffect(() => {
    // Cargar datos del estudiante
  }, []);

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">
          Bienvenido, {user?.first_name}
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Tareas Activas</h3>
            <p className="text-3xl font-bold text-blue-600">5</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Promedio</h3>
            <p className="text-3xl font-bold text-green-600">85%</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-700 mb-2">Envíos</h3>
            <p className="text-3xl font-bold text-purple-600">12</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Mis Tareas</h2>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="flex justify-between items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                <div>
                  <h3 className="font-semibold text-gray-800">Tarea {i}</h3>
                  <p className="text-sm text-gray-600">Vence en 2 días</p>
                </div>
                <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                  Ver Detalles
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
