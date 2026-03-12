import { useState } from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';

function AppRouter() {
  const { user, loading } = useAuth();
  const [showRegister, setShowRegister] = useState(false);

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: 'var(--bg-primary)',
        color: 'var(--text-secondary)',
        fontFamily: 'var(--font-mono)',
        fontSize: '13px',
        letterSpacing: '0.1em',
      }}>
        INITIALIZING...
      </div>
    );
  }

  if (user) return <DashboardPage />;

  if (showRegister) {
    return <RegisterPage onSwitch={() => setShowRegister(false)} />;
  }

  return <LoginPage onSwitch={() => setShowRegister(true)} />;
}

export default function App() {
  return (
    <AuthProvider>
      <AppRouter />
    </AuthProvider>
  );
}