// src/contexts/AuthContext.tsx
import { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { useRouter } from 'next/router';
import authApi from '../lib/authApi';

interface User {
  id: string;
  email: string;
  username: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  register: (email: string, password: string, username: string) => Promise<void>;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check if user is already logged in on initial load
    const token = localStorage.getItem('authToken');
    if (token) {
      // Verify the token with the backend
      verifyTokenAndSetUser(token);
    } else {
      setLoading(false);
    }
  }, []);

  const verifyTokenAndSetUser = async (token: string) => {
    try {
      // In a real app, you would make an API call to verify the token
      // For now, we'll just decode the token to get user info
      // In a real implementation, you would have an endpoint like /auth/me
      const payload = parseJwtPayload(token);
      if (payload && payload.sub) {
        // Set user data based on token payload
        setUser({
          id: payload.sub,
          email: payload.email || 'user@example.com',
          username: payload.username || 'demo_user'
        });
      }
    } catch (error) {
      console.error('Token verification failed:', error);
      // Clear invalid token
      localStorage.removeItem('authToken');
    } finally {
      setLoading(false);
    }
  };

  const parseJwtPayload = (token: string) => {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
      }).join(''));

      return JSON.parse(jsonPayload);
    } catch (error) {
      console.error('Error parsing JWT payload:', error);
      return null;
    }
  };

  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      // Make API call to login endpoint
      const response = await authApi.login({ email, password });
      
      // Extract token from response
      const token = response.data.token;
      if (token) {
        // Store token in localStorage
        localStorage.setItem('authToken', token);
        
        // Set user data from response
        setUser(response.data.user);
        
        router.push('/tasks');
      } else {
        throw new Error('No token received from login');
      }
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (email: string, password: string, username: string) => {
    setLoading(true);
    try {
      // Make API call to register endpoint
      const response = await authApi.register({ email, password, username });
      
      // Extract token from response
      const token = response.data.token;
      if (token) {
        // Store token in localStorage
        localStorage.setItem('authToken', token);
        
        // Set user data from response
        setUser(response.data.user);
        
        router.push('/tasks');
      } else {
        throw new Error('No token received from registration');
      }
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('authToken');
    setUser(null);
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, register, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}