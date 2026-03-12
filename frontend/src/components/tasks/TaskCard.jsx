import { useState } from 'react';
import StatusBadge from './StatusBadge';

const PRIORITY_COLORS = {
  LOW: 'var(--priority-low)',
  NORMAL: 'var(--priority-normal)',
  HIGH: 'var(--priority-high)',
  CRITICAL: 'var(--priority-critical)',
};

function formatDate(dt) {
  if (!dt) return '—';
  return new Date(dt).toLocaleString('en-US', {
    month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit', hour12: false,
  });
}

export default function TaskCard({ task, onComplete, onCancel, onDelete }) {
  const [confirming, setConfirming] = useState(false);
  const isTerminal = ['COMPLETED', 'FAILED', 'CANCELLED'].includes(task.status);
  const isRunning = task.status === 'RUNNING';
  const priorityColor = PRIORITY_COLORS[task.priority] || PRIORITY_COLORS.NORMAL;

  return (
    <div className="fade-in" style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border)',
      borderLeft: `3px solid ${priorityColor}`,
      padding: '16px 20px',
      display: 'flex',
      flexDirection: 'column',
      gap: '12px',
      transition: 'border-color var(--transition)',
      opacity: isTerminal ? 0.7 : 1,
    }}>

      {/* Header Row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{
            fontFamily: 'var(--font-display)',
            fontWeight: 700,
            fontSize: '15px',
            color: 'var(--text-primary)',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
          }}>
            {task.title}
          </div>
          {task.description && (
            <div style={{
              fontSize: '12px',
              color: 'var(--text-secondary)',
              marginTop: 4,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}>
              {task.description}
            </div>
          )}
        </div>
        <StatusBadge status={task.status} />
      </div>

      {/* Meta Row */}
      <div style={{
        display: 'flex',
        gap: 16,
        fontSize: '11px',
        color: 'var(--text-secondary)',
        flexWrap: 'wrap',
      }}>
        <span>
          <span style={{ color: 'var(--text-muted)' }}>SCHED </span>
          {formatDate(task.scheduled_at)}
        </span>
        {task.executed_at && (
          <span>
            <span style={{ color: 'var(--text-muted)' }}>RAN </span>
            {formatDate(task.executed_at)}
          </span>
        )}
        <span style={{ color: priorityColor }}>
          {task.priority}
        </span>
        {task.retry_count > 0 && (
          <span style={{ color: 'var(--status-failed)' }}>
            RETRY {task.retry_count}/{task.max_retries}
          </span>
        )}
      </div>

      {/* Actions */}
      {!isTerminal && !isRunning && (
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => onComplete(task.id)} style={btnStyle('var(--status-completed)')}>
            ✓ COMPLETE
          </button>
          <button onClick={() => onCancel(task.id)} style={btnStyle('var(--status-cancelled)')}>
            ✕ CANCEL
          </button>
          {!confirming ? (
            <button onClick={() => setConfirming(true)} style={btnStyle('var(--status-failed)')}>
              ⌫ DELETE
            </button>
          ) : (
            <>
              <button onClick={() => { onDelete(task.id); setConfirming(false); }}
                style={btnStyle('var(--status-failed)', true)}>
                CONFIRM
              </button>
              <button onClick={() => setConfirming(false)} style={btnStyle('var(--text-secondary)')}>
                BACK
              </button>
            </>
          )}
        </div>
      )}

      {isTerminal && (
        <div style={{ display: 'flex', gap: 8 }}>
          <button onClick={() => onDelete(task.id)} style={btnStyle('var(--text-muted)')}>
            ⌫ REMOVE
          </button>
        </div>
      )}
    </div>
  );
}

function btnStyle(color, filled = false) {
  return {
    padding: '4px 12px',
    background: filled ? color : 'transparent',
    border: `1px solid ${color}`,
    color: filled ? 'var(--bg-primary)' : color,
    fontSize: '10px',
    letterSpacing: '0.06em',
    cursor: 'pointer',
    transition: 'all var(--transition)',
    fontFamily: 'var(--font-mono)',
  };
}