import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useTasks } from '../hooks/useTasks';
import TaskCard from '../components/tasks/TaskCard';
import TaskForm from '../components/tasks/TaskForm';

const FILTERS = ['ALL', 'PENDING', 'SCHEDULED', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED'];

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const { tasks, loading, error, createTask, completeTask, cancelTask, deleteTask } = useTasks();
  const [showForm, setShowForm] = useState(false);
  const [filter, setFilter] = useState('ALL');

  const filtered = filter === 'ALL' ? tasks : tasks.filter(t => t.status === filter);

  const counts = tasks.reduce((acc, t) => {
    acc[t.status] = (acc[t.status] || 0) + 1;
    return acc;
  }, {});

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>

      {/* Header */}
      <header style={{
        borderBottom: '1px solid var(--border)',
        padding: '0 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: 56,
        position: 'sticky', top: 0,
        background: 'var(--bg-primary)',
        zIndex: 50,
      }}>
        <div style={{
          fontFamily: 'var(--font-display)',
          fontWeight: 800,
          fontSize: '18px',
          color: 'var(--accent)',
          letterSpacing: '0.04em',
        }}>
          TASK_SCHEDULER
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
            {user?.email}
          </span>
          <button onClick={logout} style={{
            padding: '4px 12px',
            background: 'transparent',
            border: '1px solid var(--border)',
            color: 'var(--text-secondary)',
            fontSize: '11px',
            cursor: 'pointer',
            letterSpacing: '0.06em',
            fontFamily: 'var(--font-mono)',
            transition: 'all var(--transition)',
          }}>
            LOGOUT
          </button>
        </div>
      </header>

      <main style={{ maxWidth: 900, margin: '0 auto', padding: '32px 24px' }}>

        {/* Stats Row */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
          gap: 1,
          marginBottom: 32,
          border: '1px solid var(--border)',
          background: 'var(--border)',
        }}>
          {[
            { label: 'TOTAL', value: tasks.length, color: 'var(--text-primary)' },
            { label: 'PENDING', value: counts.PENDING || 0, color: 'var(--status-pending)' },
            { label: 'RUNNING', value: counts.RUNNING || 0, color: 'var(--status-running)' },
            { label: 'DONE', value: counts.COMPLETED || 0, color: 'var(--status-completed)' },
            { label: 'FAILED', value: counts.FAILED || 0, color: 'var(--status-failed)' },
          ].map(({ label, value, color }) => (
            <div key={label} style={{
              background: 'var(--bg-card)',
              padding: '16px 20px',
              textAlign: 'center',
            }}>
              <div style={{ fontSize: '24px', fontWeight: 700, color, fontFamily: 'var(--font-display)' }}>
                {value}
              </div>
              <div style={{ fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '0.1em', marginTop: 4 }}>
                {label}
              </div>
            </div>
          ))}
        </div>

        {/* Toolbar */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 16,
          gap: 12,
          flexWrap: 'wrap',
        }}>
          {/* Filter tabs */}
          <div style={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {FILTERS.map(f => (
              <button key={f} onClick={() => setFilter(f)} style={{
                padding: '5px 12px',
                background: filter === f ? 'var(--accent-dim)' : 'var(--bg-card)',
                border: `1px solid ${filter === f ? 'var(--accent-border)' : 'var(--border)'}`,
                color: filter === f ? 'var(--accent)' : 'var(--text-secondary)',
                fontSize: '10px',
                cursor: 'pointer',
                letterSpacing: '0.06em',
                fontFamily: 'var(--font-mono)',
                transition: 'all var(--transition)',
              }}>
                {f}
                {f !== 'ALL' && counts[f] ? ` (${counts[f]})` : ''}
              </button>
            ))}
          </div>

          {/* New Task button */}
          <button onClick={() => setShowForm(true)} style={{
            padding: '6px 16px',
            background: 'var(--accent)',
            border: '1px solid var(--accent)',
            color: 'var(--bg-primary)',
            fontSize: '11px',
            fontWeight: 700,
            cursor: 'pointer',
            letterSpacing: '0.08em',
            fontFamily: 'var(--font-mono)',
            whiteSpace: 'nowrap',
          }}>
            + NEW TASK
          </button>
        </div>

        {/* Task List */}
        {loading && tasks.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-secondary)', fontSize: '13px' }}>
            LOADING...
          </div>
        ) : error ? (
          <div style={{
            padding: '16px',
            border: '1px solid var(--status-failed)',
            color: 'var(--status-failed)',
            fontSize: '13px',
          }}>
            {error}
          </div>
        ) : filtered.length === 0 ? (
          <div style={{
            textAlign: 'center', padding: '60px 0',
            color: 'var(--text-muted)', fontSize: '13px',
          }}>
            {filter === 'ALL' ? (
              <>
                <div style={{ fontSize: '32px', marginBottom: 12 }}>_</div>
                <div>NO TASKS YET</div>
                <div style={{ fontSize: '11px', marginTop: 8 }}>
                  Press + NEW TASK to schedule your first task
                </div>
              </>
            ) : `NO ${filter} TASKS`}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {filtered.map(task => (
              <TaskCard
                key={task.id}
                task={task}
                onComplete={completeTask}
                onCancel={cancelTask}
                onDelete={deleteTask}
              />
            ))}
          </div>
        )}

        {/* Footer */}
        <div style={{
          marginTop: 32,
          paddingTop: 16,
          borderTop: '1px solid var(--border)',
          fontSize: '10px',
          color: 'var(--text-muted)',
          display: 'flex',
          justifyContent: 'space-between',
        }}>
          <span>TASK_SCHEDULER v1.0</span>
          <span>AUTO-REFRESH 10s</span>
        </div>
      </main>

      {showForm && (
        <TaskForm onSubmit={createTask} onClose={() => setShowForm(false)} />
      )}
    </div>
  );
}