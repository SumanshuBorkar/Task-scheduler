export default function StatusBadge({ status }) {
    const config = {
      PENDING:   { label: 'PENDING',   color: 'var(--status-pending)' },
      SCHEDULED: { label: 'SCHEDULED', color: 'var(--status-scheduled)' },
      RUNNING:   { label: 'RUNNING',   color: 'var(--status-running)' },
      COMPLETED: { label: 'COMPLETED', color: 'var(--status-completed)' },
      FAILED:    { label: 'FAILED',    color: 'var(--status-failed)' },
      CANCELLED: { label: 'CANCELLED', color: 'var(--status-cancelled)' },
    };
  
    const { label, color } = config[status] || config.PENDING;
    const isRunning = status === 'RUNNING';
  
    return (
      <span style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '2px 8px',
        border: `1px solid ${color}`,
        color,
        fontSize: '10px',
        fontFamily: 'var(--font-mono)',
        letterSpacing: '0.08em',
        animation: isRunning ? 'pulse-border 1.5s ease infinite' : 'none',
      }}>
        <span style={{
          width: 6, height: 6,
          borderRadius: '50%',
          background: color,
          animation: isRunning ? 'spin 1s linear infinite' : 'none',
          flexShrink: 0,
        }} />
        {label}
      </span>
    );
  }