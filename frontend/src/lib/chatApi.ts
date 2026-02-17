// src/lib/chatApi.ts
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000/api';

/**
 * Get auth token from localStorage
 */
function getAuthToken(): string | null {
  return localStorage.getItem('authToken');
}

/**
 * Parse JWT payload to extract user info
 */
function parseJwtPayload(token: string): any {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Error parsing JWT payload:', error);
    return null;
  }
}

/**
 * Get current user ID from token
 */
function getCurrentUserId(): string | null {
  const token = getAuthToken();
  if (!token) return null;
  
  const payload = parseJwtPayload(token);
  return payload?.sub || null;
}

export interface ChatRequest {
  message: string;
  conversation_id?: number | null;
}

export interface ToolCall {
  tool_name: string;
  arguments: Record<string, any>;
  result?: Record<string, any>;
}

export interface ChatResponse {
  success: boolean;
  conversation_id: number;
  response: string;
  tool_calls: ToolCall[];
  message_id: number;
  created_at: string;
}

export interface Message {
  id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  created_at: string;
  metadata?: {
    tool_calls?: ToolCall[];
  };
  tool_calls?: ToolCall[];
}

export interface Conversation {
  id: number;
  user_id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export interface ConversationHistoryResponse {
  success: boolean;
  conversation: Conversation;
  messages: Message[];
}

export interface ConversationListResponse {
  success: boolean;
  conversations: Conversation[];
  total: number;
}

const chatApi = {
  /**
   * Send a message to the chat endpoint
   */
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    const token = getAuthToken();
    const userId = getCurrentUserId();
    
    if (!token || !userId) {
      throw new Error('Authentication required');
    }

    const response = await axios.post<ChatResponse>(
      `${API_BASE_URL}/${userId}/chat`,
      request,
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      }
    );

    return response.data;
  },

  /**
   * Get conversation history
   */
  getConversation: async (conversationId: number): Promise<ConversationHistoryResponse> => {
    const token = getAuthToken();
    const userId = getCurrentUserId();
    
    if (!token || !userId) {
      throw new Error('Authentication required');
    }

    const response = await axios.get<ConversationHistoryResponse>(
      `${API_BASE_URL}/${userId}/conversations/${conversationId}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      }
    );

    return response.data;
  },

  /**
   * List all conversations
   */
  listConversations: async (limit: number = 50, offset: number = 0): Promise<ConversationListResponse> => {
    const token = getAuthToken();
    const userId = getCurrentUserId();
    
    if (!token || !userId) {
      throw new Error('Authentication required');
    }

    const response = await axios.get<ConversationListResponse>(
      `${API_BASE_URL}/${userId}/conversations?limit=${limit}&offset=${offset}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      }
    );

    return response.data;
  },

  /**
   * Delete a conversation
   */
  deleteConversation: async (conversationId: number): Promise<{ success: boolean; message: string }> => {
    const token = getAuthToken();
    const userId = getCurrentUserId();
    
    if (!token || !userId) {
      throw new Error('Authentication required');
    }

    const response = await axios.delete<{ success: boolean; message: string }>(
      `${API_BASE_URL}/${userId}/conversations/${conversationId}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      }
    );

    return response.data;
  },

  /**
   * Get current user ID from token
   */
  getCurrentUserId,

  /**
   * Check if user is authenticated
   */
  isAuthenticated: (): boolean => {
    return !!getAuthToken();
  },
};

export default chatApi;
