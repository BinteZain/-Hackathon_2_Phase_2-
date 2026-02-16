// src/utils/notification.ts
export const showNotification = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
  // In a real app, you would use a notification library like react-toastify
  // For now, we'll use a simple alert
  console.log(`${type.toUpperCase()}: ${message}`);
  
  // You could implement a more sophisticated notification system here
  // For example, using a state management solution to show toast notifications
};