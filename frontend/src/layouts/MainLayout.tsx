// MainLayout.tsx - Layout principal
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/useStore';
import { authService } from '../services/authService';

export const MainLayout = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = async () => {
    await authService.logout();
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header/Navbar */}
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-600">Code Grading</h1>
          
          <div className="flex items-center gap-6">
            <span className="text-gray-700">
              {user?.first_name} {user?.last_name}
            </span>
            <button
              onClick={handleLogout}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main>
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white text-center py-4 mt-16">
        <p>&copy; 2024 Code Grading System. Todos los derechos reservados.</p>
      </footer>
    </div>
  );
};
