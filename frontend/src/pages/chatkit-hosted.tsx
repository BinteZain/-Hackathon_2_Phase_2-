// src/pages/chatkit-hosted.tsx
// ChatKit UI page that integrates with custom backend REST API
// Uses @openai/chatkit library for the UI component

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';
import { useAuth } from '../contexts/AuthContext';
import type { OpenAIChatKit, ChatKitOptions } from '@openai/chatkit';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000';

// ChatKit Web Component script URL
const CHATKIT_SCRIPT_URL = 'https://cdn.openai.com/chatkit/v1.6.0/index.js';

export default function ChatKitHostedPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();

  const chatkitRef = useRef<OpenAIChatKit | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [isChatKitReady, setIsChatKitReady] = useState(false);
  const [initializationError, setInitializationError] = useState<string | null>(null);
  const [isScriptLoaded, setIsScriptLoaded] = useState(false);

  // Load ChatKit script
  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Check if script already exists
    const existingScript = document.querySelector(`script[src="${CHATKIT_SCRIPT_URL}"]`);
    if (existingScript) {
      setIsScriptLoaded(true);
      return;
    }

    const script = document.createElement('script');
    script.src = CHATKIT_SCRIPT_URL;
    script.async = true;
    script.onload = () => setIsScriptLoaded(true);
    script.onerror = () => setInitializationError('Failed to load ChatKit script');
    document.body.appendChild(script);

    return () => {
      // Don't remove script on unmount - keep it for navigation
    };
  }, []);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  // Initialize ChatKit when user is authenticated and script is loaded
  useEffect(() => {
    if (!user || !containerRef.current || !isScriptLoaded) return;

    const initializeChatKit = async () => {
      try {
        // Wait for the web component to be registered
        if (!customElements.get('openai-chatkit')) {
          await customElements.whenDefined('openai-chatkit');
        }

        // Create ChatKit element (web component)
        const chatkitElement = document.createElement('openai-chatkit') as OpenAIChatKit;
        chatkitRef.current = chatkitElement;
        
        // Helper: Get current user ID from JWT token
        const getCurrentUserId = (): string | null => {
          const token = localStorage.getItem('authToken');
          if (!token) return null;
          try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(
              atob(base64).split('').map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join('')
            );
            const payload = JSON.parse(jsonPayload);
            return payload?.sub || null;
          } catch (error) {
            console.error('Error parsing JWT payload:', error);
            return null;
          }
        };

        const userId = getCurrentUserId();
        if (!userId) {
          setInitializationError('User ID not found in authentication token');
          return;
        }

        // Configure ChatKit with Custom API to call our existing backend
        // The custom fetch completely overrides request handling to work with our REST API
        const options: ChatKitOptions = {
          api: {
            // Custom API configuration
            url: `${API_BASE_URL}/api/${userId}/chat`,
            domainKey: process.env.NEXT_PUBLIC_CHATKIT_DOMAIN_KEY || 'local-development',
            
            // Custom fetch to integrate with our REST API
            // This transforms ChatKit requests into our backend's expected format
            fetch: async (input: RequestInfo | URL, init?: RequestInit) => {
              const token = localStorage.getItem('authToken');
              
              // Parse the request body if present
              let requestBody: any = null;
              if (init?.body) {
                try {
                  // ChatKit sends messages in its own format, we need to extract the text
                  const bodyStr = typeof init.body === 'string' ? init.body : JSON.stringify(init.body);
                  const parsed = JSON.parse(bodyStr);
                  
                  // Extract message content from ChatKit format
                  // ChatKit sends: { messages: [{ role, content }], ... }
                  // We need: { message: string, conversation_id?: number }
                  const lastMessage = parsed.messages?.[parsed.messages.length - 1];
                  if (lastMessage?.role === 'user') {
                    requestBody = {
                      message: lastMessage.content,
                      conversation_id: conversationId,
                    };
                  }
                } catch (e) {
                  console.warn('Could not parse request body:', e);
                }
              }

              // Build headers with JWT authentication
              const headers: Record<string, string> = {
                'Content-Type': 'application/json',
              };
              
              if (token) {
                headers['Authorization'] = `Bearer ${token}`;
              }

              // Make request to our backend
              const response = await fetch(`${API_BASE_URL}/api/${userId}/chat`, {
                method: 'POST',
                headers,
                body: requestBody ? JSON.stringify(requestBody) : JSON.stringify({ message: '', conversation_id: conversationId }),
              });

              if (!response.ok) {
                throw new Error(`Backend error: ${response.status} ${response.statusText}`);
              }

              const data = await response.json();
              
              // Transform our backend response to ChatKit's expected format
              // Our backend returns: { success, conversation_id, response, tool_calls, message_id, created_at }
              // ChatKit expects SSE stream or JSON with assistant message
              const chatkitResponse = {
                id: data.message_id?.toString() || Date.now().toString(),
                role: 'assistant',
                content: data.response,
                created_at: data.created_at,
              };

              // Return as a Response object that ChatKit can consume
              // For non-streaming, return JSON
              return new Response(JSON.stringify(chatkitResponse), {
                headers: { 'Content-Type': 'application/json' },
              });
            },
            
            uploadStrategy: {
              type: 'two_phase',
            },
          },
          
          // UI Configuration
          theme: {
            colorScheme: 'light',
            radius: 'pill',
            density: 'normal',
          },
          
          header: {
            enabled: true,
            title: {
              enabled: true,
            },
          },
          
          history: {
            enabled: true,
            showDelete: true,
            showRename: true,
          },
          
          startScreen: {
            greeting: 'Hello! I\'m your Todo Assistant. How can I help you today?',
            prompts: [
              {
                label: 'Add a task',
                prompt: 'Add a task to buy groceries',
                icon: 'plus',
              },
              {
                label: 'List my tasks',
                prompt: 'Show me my tasks',
                icon: 'book-open',
              },
              {
                label: 'Complete a task',
                prompt: 'Mark task as complete',
                icon: 'check-circle',
              },
              {
                label: 'Delete tasks',
                prompt: 'Delete my completed tasks',
                icon: 'close',
              } as any,
            ],
          },
          
          composer: {
            placeholder: 'Ask me to help with your tasks...',
          },
          
          disclaimer: {
            text: 'AI-powered Todo Assistant • Powered by ChatKit',
            highContrast: false,
          },
        };

        // Apply options to the ChatKit element
        chatkitElement.setOptions(options);
        
        // Style the container to fill the available space
        chatkitElement.style.width = '100%';
        chatkitElement.style.height = '100%';

        // Clear container and append ChatKit
        if (containerRef.current) {
          containerRef.current.innerHTML = '';
          containerRef.current.appendChild(chatkitElement);
        }
        
        setIsChatKitReady(true);
        setInitializationError(null);
      } catch (error) {
        console.error('Failed to initialize ChatKit:', error);
        setInitializationError(error instanceof Error ? error.message : 'Failed to initialize ChatKit');
      }
    };

    initializeChatKit();

    // Cleanup on unmount
    return () => {
      if (chatkitRef.current && containerRef.current) {
        containerRef.current.removeChild(chatkitRef.current);
      }
    };
  }, [user, conversationId]);

  // Handle conversation state changes from ChatKit events
  useEffect(() => {
    if (!chatkitRef.current || !isChatKitReady) return;

    // Listen for thread change events
    const handleThreadChange = (event: CustomEvent) => {
      const threadId = event.detail?.threadId;
      if (threadId) {
        // Store conversation ID in state
        const convId = parseInt(threadId, 10);
        setConversationId(convId);
        console.log('Conversation ID updated:', convId);
      }
    };

    const element = chatkitRef.current as HTMLElement;
    element.addEventListener('threadchange', handleThreadChange as EventListener);

    return () => {
      element.removeEventListener('threadchange', handleThreadChange as EventListener);
    };
  }, [isChatKitReady]);

  if (authLoading || !user) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (initializationError) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-100">
        <div className="text-center max-w-md">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <svg className="w-12 h-12 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-lg font-semibold text-red-800 mb-2">ChatKit Initialization Error</h2>
            <p className="text-red-600 text-sm">{initializationError}</p>
            <button
              onClick={() => router.push('/tasks')}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Go to Tasks
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>ChatKit - Todo Assistant</title>
        <meta name="description" content="AI-powered todo assistant using ChatKit" />
      </Head>

      <div className="flex h-screen bg-gray-100">
        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col min-w-0 bg-white">
          {/* Chat Header */}
          <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between shadow-sm z-10">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h1 className="text-lg font-semibold text-gray-800">ChatKit Assistant</h1>
              {conversationId && (
                <span className="text-xs text-gray-400 ml-2">
                  (Conversation: {conversationId})
                </span>
              )}
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-sm text-gray-600">
                {user.username}
              </span>
              <button
                onClick={() => router.push('/tasks')}
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Tasks View
              </button>
            </div>
          </header>

          {/* ChatKit Container */}
          <div
            ref={containerRef}
            className="flex-1 overflow-hidden"
            style={{ minHeight: 0 }}
          />
        </main>
      </div>
    </>
  );
}
