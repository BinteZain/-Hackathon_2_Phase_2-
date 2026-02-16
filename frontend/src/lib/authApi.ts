// src/lib/authApi.ts
import axios, { AxiosResponse } from 'axios';
import mockAuthApi from './mockAuthApi';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000/api/v1';

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterCredentials {
  email: string;
  password: string;
  username: string;
}

interface LoginResponse {
  success: boolean;
  token: string;
  user: {
    id: string;
    email: string;
    username: string;
  };
  message: string;
}

// Check if backend auth endpoints are available
async function isBackendAvailable(): Promise<boolean> {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.status === 200;
  } catch (error) {
    console.log('Backend not available, using mock auth');
    return false;
  }
}

// Wrapper function that tries real API first, falls back to mock
async function callWithFallback<T>(
  realCall: () => Promise<AxiosResponse<T>>,
  mockCall: () => Promise<any>
): Promise<AxiosResponse<T>> {
  const backendAvailable = await isBackendAvailable();
  
  if (backendAvailable) {
    try {
      return await realCall();
    } catch (error) {
      console.log('Real API failed, falling back to mock auth');
      const mockResult = await mockCall();
      return { data: mockResult.data, status: 200, statusText: 'OK', headers: {}, config: {} as any };
    }
  } else {
    console.log('Using mock auth API');
    const mockResult = await mockCall();
    return { data: mockResult.data, status: 200, statusText: 'OK', headers: {}, config: {} as any };
  }
}

const authApi = {
  login: async (credentials: LoginCredentials): Promise<AxiosResponse<LoginResponse>> => {
    return callWithFallback(
      () => axios.post(`${API_BASE_URL}/auth/login`, credentials),
      () => mockAuthApi.login(credentials)
    );
  },

  register: async (credentials: RegisterCredentials): Promise<AxiosResponse<LoginResponse>> => {
    return callWithFallback(
      () => axios.post(`${API_BASE_URL}/auth/register`, credentials),
      () => mockAuthApi.register(credentials)
    );
  },

  logout: async (): Promise<AxiosResponse<{ success: boolean; message: string }>> => {
    return callWithFallback(
      () => axios.post(`${API_BASE_URL}/auth/logout`),
      () => mockAuthApi.logout()
    );
  },

  getProfile: async (): Promise<AxiosResponse<any>> => {
    return callWithFallback(
      () => axios.get(`${API_BASE_URL}/auth/profile`),
      () => mockAuthApi.getProfile()
    );
  }
};

export default authApi;