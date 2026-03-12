import { useState } from 'react';

export default function TaskForm({ onSubmit, onClose }) {
  const [form, setForm] = useState({
    title: '',
    description: '',
    priority: 'NORMAL',
    scheduled_at: '',
    max_retries: 3,
  });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  function getMinDateTime() {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 2);
    return now.toISOString().slice(0, 16);
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    if (!form.title.trim()) return setError('Title is required.');
    if (!form.scheduled_at) return setError('Scheduled time is required.');

    setSubmitting(true);
    try {
      await onSubmit({
        ...form,
        scheduled_at: new Date(form.scheduled_at).toISOString(),
        max_retries: Number(form.max_retries),
      });
      onClose();
    } catch (err) {
      const msg = err.response?.data?.errors?.scheduled_at?.[0]
        || err.response?.data?.message
        || 'Failed to create task.';
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={{
      position: 'fixed', inset: 0,
      background: 'rgba(0,0,0,0.85)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 100, padding: 16,
    }}>
      <div className="fade-in" style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        width: '100%', maxWidth: 480,
        padding: 32,
      }}>
        <div style={{
          display: 'flex', justifyContent: 'space-between',
          alignItems: 'center', marginBottom: 24,
        }}>
          <h2 style={{
            fontFamily: 'var(--font-display)',
            fontWeight: 800, fontSize: '18px',
            color: 'var(--accent)',
          }}>
            NEW TASK
          </h2>
          <button onClick={onClose} style={{
            background: 'none', border: 'none',
            color: 'var(--text-secondary)', cursor: 'pointer', fontSize: 20,
          }}>✕</button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

          {[
            { label: 'TITLE *', key: 'title', type: 'text', placeholder: 'What needs to be done?' },
            { label: 'DESCRIPTION', key: 'description', type: 'text', placeholder: 'Optional details...' },
          ].map(({ label, key, type, placeholder }) => (
            <div key={key}>
              <label style={labelStyle}>{label}</label>
              <input
                type={type}
                value={form[key]}
                onChange={e => setForm(p => ({ ...p, [key]: e.target.value }))}
                placeholder={placeholder}
                style={inputStyle}
              />
            </div>
          ))}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label style={labelStyle}>PRIORITY</label>
              <select value={form.priority}
                onChange={e => setForm(p => ({ ...p, priority: e.target.value }))}
                style={inputStyle}>
                {['LOW', 'NORMAL', 'HIGH', 'CRITICAL'].map(p => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
            <div>
              <label style={labelStyle}>MAX RETRIES</label>
              <input type="number" min={0} max={10}
                value={form.max_retries}
                onChange={e => setForm(p => ({ ...p, max_retries: e.target.value }))}
                style={inputStyle}
              />
            </div>
          </div>

          <div>
            <label style={labelStyle}>SCHEDULED TIME *</label>
            <input type="datetime-local"
              value={form.scheduled_at}
              min={getMinDateTime()}
              onChange={e => setForm(p => ({ ...p, scheduled_at: e.target.value }))}
              style={{ ...inputStyle, colorScheme: 'dark' }}
            />
          </div>

          {error && (
            <div style={{
              padding: '8px 12px',
              background: 'rgba(239,68,68,0.1)',
              border: '1px solid var(--status-failed)',
              color: 'var(--status-failed)',
              fontSize: '12px',
            }}>
              {error}
            </div>
          )}

          <button type="submit" disabled={submitting} style={{
            padding: '12px',
            background: submitting ? 'transparent' : 'var(--accent)',
            border: '1px solid var(--accent)',
            color: submitting ? 'var(--accent)' : 'var(--bg-primary)',
            fontSize: '13px',
            fontWeight: 700,
            letterSpacing: '0.08em',
            cursor: submitting ? 'not-allowed' : 'pointer',
            marginTop: 8,
            transition: 'all var(--transition)',
            fontFamily: 'var(--font-mono)',
          }}>
            {submitting ? 'SCHEDULING...' : '+ SCHEDULE TASK'}
          </button>
        </form>
      </div>
    </div>
  );
}

const labelStyle = {
  display: 'block',
  fontSize: '10px',
  color: 'var(--text-secondary)',
  letterSpacing: '0.1em',
  marginBottom: 6,
};

const inputStyle = {
  width: '100%',
  padding: '8px 10px',
  background: 'var(--bg-secondary)',
  border: '1px solid var(--border)',
  color: 'var(--text-primary)',
  fontSize: '13px',
  outline: 'none',
  transition: 'border-color var(--transition)',
};