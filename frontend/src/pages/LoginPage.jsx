import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage({ onSwitch }) {
  const { login } = useAuth();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(form.email, form.password);
    } catch (err) {
      setError(err.response?.data?.message || 'Login failed.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={pageStyle}>
      <div style={cardStyle} className="fade-in">
        <div style={{ marginBottom: 32 }}>
          <div style={logoStyle}>TASK_SCHEDULER</div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: 6 }}>
            Sign in to your workspace
          </div>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {[
            { label: 'EMAIL', key: 'email', type: 'email' },
            { label: 'PASSWORD', key: 'password', type: 'password' },
          ].map(({ label, key, type }) => (
            <div key={key}>
              <label style={labelStyle}>{label}</label>
              <input type={type} value={form[key]} required
                onChange={e => setForm(p => ({ ...p, [key]: e.target.value }))}
                style={inputStyle}
              />
            </div>
          ))}

          {error && <div style={errorStyle}>{error}</div>}

          <button type="submit" disabled={loading} style={submitStyle(loading)}>
            {loading ? 'AUTHENTICATING...' : '→ SIGN IN'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: 24, fontSize: '12px', color: 'var(--text-secondary)' }}>
          No account?{' '}
          <button onClick={onSwitch} style={{
            background: 'none', border: 'none',
            color: 'var(--accent)', cursor: 'pointer',
            fontFamily: 'var(--font-mono)', fontSize: '12px',
          }}>
            Register
          </button>
        </div>
      </div>
    </div>
  );
}

const pageStyle = {
  minHeight: '100vh',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: 16,
  background: 'var(--bg-primary)',
};

const cardStyle = {
  background: 'var(--bg-card)',
  border: '1px solid var(--border)',
  padding: '40px 36px',
  width: '100%',
  maxWidth: 400,
};

const logoStyle = {
  fontFamily: 'var(--font-display)',
  fontWeight: 800,
  fontSize: '22px',
  color: 'var(--accent)',
  letterSpacing: '0.04em',
};

const labelStyle = {
  display: 'block',
  fontSize: '10px',
  color: 'var(--text-secondary)',
  letterSpacing: '0.1em',
  marginBottom: 6,
};

const inputStyle = {
  width: '100%',
  padding: '10px 12px',
  background: 'var(--bg-secondary)',
  border: '1px solid var(--border)',
  color: 'var(--text-primary)',
  fontSize: '13px',
  outline: 'none',
};

const errorStyle = {
  padding: '8px 12px',
  background: 'rgba(239,68,68,0.1)',
  border: '1px solid var(--status-failed)',
  color: 'var(--status-failed)',
  fontSize: '12px',
};

const submitStyle = (loading) => ({
  padding: '12px',
  background: loading ? 'transparent' : 'var(--accent)',
  border: '1px solid var(--accent)',
  color: loading ? 'var(--accent)' : 'var(--bg-primary)',
  fontSize: '13px',
  fontWeight: 700,
  letterSpacing: '0.08em',
  cursor: loading ? 'not-allowed' : 'pointer',
  marginTop: 8,
  fontFamily: 'var(--font-mono)',
});