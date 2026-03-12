import { useState, useEffect, useCallback, useRef } from 'react';
import api from '../api/axios';

export function useTasks() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  const fetchTasks = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    try {
      const { data } = await api.get('/tasks/');
      setTasks(data.results || []);
      setError(null);
    } catch (err) {
      setError('Failed to load tasks.');
    } finally {
      setLoading(false);
    }
  }, []);

  // Poll every 10 seconds
  useEffect(() => {
    fetchTasks();
    intervalRef.current = setInterval(() => fetchTasks(true), 10000);
    return () => clearInterval(intervalRef.current);
  }, [fetchTasks]);

  // Optimistic complete
  const completeTask = useCallback(async (taskId) => {
    setTasks(prev => prev.map(t =>
      t.id === taskId ? { ...t, status: 'COMPLETED' } : t
    ));
    try {
      await api.post(`/tasks/${taskId}/complete/`);
      fetchTasks(true);
    } catch {
      fetchTasks(true);
    }
  }, [fetchTasks]);

  // Optimistic cancel
  const cancelTask = useCallback(async (taskId) => {
    setTasks(prev => prev.map(t =>
      t.id === taskId ? { ...t, status: 'CANCELLED' } : t
    ));
    try {
      await api.post(`/tasks/${taskId}/cancel/`);
      fetchTasks(true);
    } catch {
      fetchTasks(true);
    }
  }, [fetchTasks]);

  // Optimistic delete
  const deleteTask = useCallback(async (taskId) => {
    setTasks(prev => prev.filter(t => t.id !== taskId));
    try {
      await api.delete(`/tasks/${taskId}/`);
    } catch {
      fetchTasks(true);
    }
  }, [fetchTasks]);

  /**
   * Generic status updater.
   * Routes to the correct backend endpoint based on target status.
   *
   * COMPLETED → POST /tasks/{id}/complete/
   * CANCELLED → POST /tasks/{id}/cancel/
   * PENDING | SCHEDULED | RUNNING | FAILED
   *         → PATCH /tasks/{id}/  { status: <value> }
   *           (manual override for testing/admin purposes)
   */
  const updateTaskStatus = useCallback(async (taskId, newStatus) => {
    // Optimistic update immediately
    setTasks(prev => prev.map(t =>
      t.id === taskId ? { ...t, status: newStatus } : t
    ));

    try {
      if (newStatus === 'COMPLETED') {
        await api.post(`/tasks/${taskId}/complete/`);
      } else if (newStatus === 'CANCELLED') {
        await api.post(`/tasks/${taskId}/cancel/`);
      } else {
        // Direct PATCH for system states (PENDING, SCHEDULED, RUNNING, FAILED)
        await api.patch(`/tasks/${taskId}/`, { status: newStatus });
      }
      fetchTasks(true);
    } catch {
      fetchTasks(true); // Revert on failure
    }
  }, [fetchTasks]);

  const createTask = useCallback(async (payload) => {
    const { data } = await api.post('/tasks/', payload);
    fetchTasks(true);
    return data.task;
  }, [fetchTasks]);

  return {
    tasks, loading, error,
    fetchTasks, createTask,
    completeTask, cancelTask, deleteTask,
    updateTaskStatus,
  };
}