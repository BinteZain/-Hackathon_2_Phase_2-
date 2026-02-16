// src/pages/_app.tsx
import '../styles/globals.css';
import type { AppProps } from 'next/app';
import { AuthProvider } from '../contexts/AuthContext';
import { NotificationProvider } from '../contexts/NotificationContext';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <NotificationProvider>
      <AuthProvider>
        <Component {...pageProps} />
      </AuthProvider>
    </NotificationProvider>
  );
}