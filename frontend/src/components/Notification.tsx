// src/components/Notification.tsx
import { useEffect } from 'react';
import { XCircleIcon, CheckCircleIcon, ExclamationIcon, InformationCircleIcon } from '@heroicons/react/outline';

interface NotificationProps {
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  onClose: () => void;
}

export default function Notification({ message, type, onClose }: NotificationProps) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 5000); // Auto-close after 5 seconds

    return () => clearTimeout(timer);
  }, [onClose]);

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircleIcon className="h-6 w-6 text-green-400" />;
      case 'error':
        return <XCircleIcon className="h-6 w-6 text-red-400" />;
      case 'warning':
        return <ExclamationIcon className="h-6 w-6 text-yellow-400" />;
      case 'info':
        return <InformationCircleIcon className="h-6 w-6 text-blue-400" />;
      default:
        return <InformationCircleIcon className="h-6 w-6 text-blue-400" />;
    }
  };

  const getBgColor = () => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'info':
        return 'bg-blue-50 border-blue-200';
      default:
        return 'bg-blue-50 border-blue-200';
    }
  };

  return (
    <div className={`fixed top-4 right-4 z-50 max-w-md ${getBgColor()} border rounded-lg shadow-lg p-4`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          {getIcon()}
        </div>
        <div className="ml-3 flex-1">
          <p className={`text-sm font-medium ${type === 'error' ? 'text-red-800' : type === 'success' ? 'text-green-800' : type === 'warning' ? 'text-yellow-800' : 'text-blue-800'}`}>
            {message}
          </p>
        </div>
        <div className="ml-4 flex-shrink-0">
          <button
            onClick={onClose}
            className={`inline-flex rounded-md ${type === 'error' ? 'text-red-500 hover:text-red-700' : type === 'success' ? 'text-green-500 hover:text-green-700' : type === 'warning' ? 'text-yellow-500 hover:text-yellow-700' : 'text-blue-500 hover:text-blue-700'}`}
          >
            <span className="sr-only">Close</span>
            <XCircleIcon className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
}