// src/pages/tasks.tsx
import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';
import TaskCard from '../components/TaskCard';
import TaskForm from '../components/TaskForm';
import apiClient from '../lib/api';
import { Task } from '../types/task';

export default function TasksPage() {
  const { user, logout } = useAuth();
  const { showNotification } = useNotification();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/tasks');
      setTasks(response.data.data.tasks);
      showNotification('Tasks loaded successfully', 'info');
    } catch (err: any) {
      console.error('Failed to fetch tasks:', err);
      showNotification(err.response?.data?.message || 'Failed to load tasks. Please try again later.', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOrUpdate = async (taskData: Partial<Task>) => {
    try {
      let response;
      if (editingTask) {
        // Update existing task
        response = await apiClient.put(`/tasks/${editingTask.id}`, taskData);
        setTasks(tasks.map(t => t.id === editingTask.id ? response.data.data.task : t));
        showNotification('Task updated successfully', 'success');
      } else {
        // Create new task
        response = await apiClient.post('/tasks', taskData);
        setTasks([...tasks, response.data.data.task]);
        showNotification('Task created successfully', 'success');
      }
      setShowForm(false);
      setEditingTask(null);
    } catch (err: any) {
      console.error('Failed to save task:', err);
      showNotification(
        err.response?.data?.message || (editingTask ? 'Failed to update task. Please try again.' : 'Failed to create task. Please try again.'),
        'error'
      );
    }
  };

  const handleDelete = async (taskId: string) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      await apiClient.delete(`/tasks/${taskId}`);
      setTasks(tasks.filter(t => t.id !== taskId));
      showNotification('Task deleted successfully', 'success');
    } catch (err: any) {
      console.error('Failed to delete task:', err);
      showNotification(err.response?.data?.message || 'Failed to delete task. Please try again.', 'error');
    }
  };

  const handleToggleComplete = async (task: Task) => {
    try {
      const response = await apiClient.patch(`/tasks/${task.id}/status`, {
        completed: task.status !== 'completed'
      });
      
      // Update the task in the local state
      setTasks(tasks.map(t => 
        t.id === task.id ? response.data.data.task : t
      ));
      
      showNotification(
        task.status === 'completed' 
          ? 'Task marked as pending' 
          : 'Task marked as completed', 
        'success'
      );
    } catch (err: any) {
      console.error('Failed to update task status:', err);
      showNotification(err.response?.data?.message || 'Failed to update task status. Please try again.', 'error');
    }
  };

  const handleEdit = (task: Task) => {
    setEditingTask(task);
    setShowForm(true);
  };

  const handleCancelForm = () => {
    setShowForm(false);
    setEditingTask(null);
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <h2 className="text-xl font-semibold">Access Denied</h2>
          <p className="text-gray-600">Please log in to access your tasks</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900">My Tasks</h1>
          <div className="flex items-center space-x-4">
            <span className="text-gray-700">Welcome, {user.username}</span>
            <button
              onClick={logout}
              className="btn-secondary"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-800">Your Tasks</h2>
          <button
            onClick={() => {
              setEditingTask(null);
              setShowForm(true);
            }}
            className="btn-primary"
          >
            Add New Task
          </button>
        </div>

        {showForm && (
          <div className="mb-8 card">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              {editingTask ? 'Edit Task' : 'Create New Task'}
            </h3>
            <TaskForm
              task={editingTask}
              onSave={handleCreateOrUpdate}
              onCancel={handleCancelForm}
            />
          </div>
        )}

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : tasks.length === 0 ? (
          <div className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              aria-hidden="true"
            >
              <path
                vectorEffect="non-scaling-stroke"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No tasks</h3>
            <p className="mt-1 text-sm text-gray-500">Get started by creating a new task.</p>
            <div className="mt-6">
              <button
                onClick={() => setShowForm(true)}
                className="btn-primary"
              >
                Create New Task
              </button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {tasks.map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onEdit={handleEdit}
                onDelete={handleDelete}
                onToggleComplete={handleToggleComplete}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}