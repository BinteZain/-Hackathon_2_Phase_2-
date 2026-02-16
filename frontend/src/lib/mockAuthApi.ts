// Mock authentication API for development purposes
// This simulates the backend responses when the real backend auth endpoints are not available

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000/api/v1';

// Simulated user data
const MOCK_USERS = [
  {
    id: '1',
    email: 'admin@example.com',
    username: 'admin',
    password: 'admin123'
  },
  {
    id: '2',
    email: 'user@example.com',
    username: 'user',
    password: 'user123'
  },
  {
    id: '3',
    email: 'test@example.com',
    username: 'testuser',
    password: 'password123'
  }
];

// Simple token generation (for development only)
function generateMockToken(userData) {
  const payload = {
    user_id: userData.id,
    email: userData.email,
    username: userData.username,
    exp: Math.floor(Date.now() / 1000) + (60 * 60 * 24 * 7) // 7 days expiry
  };
  
  // Base64 encode the payload (simplified for mock)
  const base64Payload = btoa(JSON.stringify(payload));
  return `mock.token.${base64Payload}`;
}

const mockAuthApi = {
  login: async (credentials) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const user = MOCK_USERS.find(u => 
      u.email === credentials.email && u.password === credentials.password
    );
    
    if (!user) {
      throw new Error('Invalid credentials');
    }
    
    const token = generateMockToken(user);
    
    return {
      data: {
        success: true,
        token,
        user: {
          id: user.id,
          email: user.email,
          username: user.username
        },
        message: 'Login successful'
      }
    };
  },

  register: async (credentials) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // Check if user already exists
    const existingUser = MOCK_USERS.find(u => 
      u.email === credentials.email || u.username === credentials.username
    );
    
    if (existingUser) {
      throw new Error('Email or username already exists');
    }
    
    // Create new user
    const newUser = {
      id: String(MOCK_USERS.length + 1),
      email: credentials.email,
      username: credentials.username,
      password: credentials.password // In real app, this would be hashed
    };
    
    // Add to mock users (in memory only)
    MOCK_USERS.push(newUser);
    
    const token = generateMockToken(newUser);
    
    return {
      data: {
        success: true,
        token,
        user: {
          id: newUser.id,
          email: newUser.email,
          username: newUser.username
        },
        message: 'Registration successful'
      }
    };
  },

  logout: async () => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 200));
    
    return {
      data: {
        success: true,
        message: 'Logout successful'
      }
    };
  },

  getProfile: async () => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Decode token to get user info (simplified)
    const token = localStorage.getItem('authToken');
    if (!token) {
      throw new Error('No token found');
    }
    
    try {
      const parts = token.split('.');
      if (parts.length !== 3) {
        throw new Error('Invalid token format');
      }
      
      const payload = JSON.parse(atob(parts[2]));
      
      const user = MOCK_USERS.find(u => u.id === payload.user_id);
      if (!user) {
        throw new Error('User not found');
      }
      
      return {
        data: {
          id: user.id,
          email: user.email,
          username: user.username
        }
      };
    } catch (error) {
      throw new Error('Invalid token');
    }
  }
};

export default mockAuthApi;