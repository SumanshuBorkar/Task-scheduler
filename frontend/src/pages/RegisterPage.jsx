import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function RegisterPage({ onSwitch }) {
  const { register } = useAuth();
  const [form, setForm] = useState({
    username: '', email: '', password: '', password_confirm: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    if (form.password !== form.password_confirm) {
      return setError('Passwords do not match.');
    }
    setLoading(true);
    try {
      await register(form.username, form.email, form.password, form.password_confirm);
    } catch (err) {
      const errors = err.response?.data?.errors || {};
      const first = Object.values(errors)[0];
      setError(Array.isArray(first) ? first[0] : err.response?.data?.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  }

  const fields = [
    { label: 'USERNAME', key: 'username', type: 'text' },
    { label: 'EMAIL', key: 'email', type: 'email' },
    { label: 'PASSWORD', key: 'password', type: 'password' },
    { label: 'CONFIRM PASSWORD', key: 'password_confirm', type: 'password' },
  ];

  return (
    <div style={pageStyle}>
      <div style={cardStyle} className="fade-in">
        <div style={{ marginBottom: 32 }}>
          <div style={logoStyle}>TASK_SCHEDULER</div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: 6 }}>
            Create your workspace
          </div>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {fields.map(({ label, key, type }) => (
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
            {loading ? 'CREATING...' : '→ CREATE ACCOUNT'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: 24, fontSize: '12px', color: 'var(--text-secondary)' }}>
          Already have an account?{' '}
          <button onClick={onSwitch} style={{
            background: 'none', border: 'none',
            color: 'var(--accent)', cursor: 'pointer',
            fontFamily: 'var(--font-mono)', fontSize: '12px',
          }}>
            Sign in
          </button>
        </div>
      </div>
    </div>
  );
}

const pageStyle = { minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16 };
const cardStyle = { background: 'var(--bg-card)', border: '1px solid var(--border)', padding: '40px 36px', width: '100%', maxWidth: 400 };
const logoStyle = { fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: '22px', color: 'var(--accent)', letterSpacing: '0.04em' };
const labelStyle = { display: 'block', fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.1em', marginBottom: 6 };
const inputStyle = { width: '100%', padding: '10px 12px', background: 'var(--bg-secondary)', border: '1px solid var(--border)', color: 'var(--text-primary)', fontSize: '13px', outline: 'none' };
const errorStyle = { padding: '8px 12px', background: 'rgba(239,68,68,0.1)', border: '1px solid var(--status-failed)', color: 'var(--status-failed)', fontSize: '12px' };
const submitStyle = (loading) => ({ padding: '12px', background: loading ? 'transparent' : 'var(--accent)', border: '1px solid var(--accent)', color: loading ? 'var(--accent)' : 'var(--bg-primary)', fontSize: '13px', fontWeight: 700, letterSpacing: '0.08em', cursor: loading ? 'not-allowed' : 'pointer', marginTop: 8, fontFamily: 'var(--font-mono)' });