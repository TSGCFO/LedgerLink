import {
  setTokens,
  getAccessToken,
  getRefreshToken,
  clearTokens,
  isAuthenticated,
  login,
  logout,
  refreshAccessToken,
  emitAuthStateChange
} from '../auth';

// Mock fetch
global.fetch = jest.fn();

// Mock localStorage
const mockLocalStorage = (() => {
  let store = {};
  return {
    getItem: jest.fn(key => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    removeItem: jest.fn(key => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
  writable: true,
});

// Mock custom event dispatch
window.dispatchEvent = jest.fn();
window.CustomEvent = jest.fn((event, options) => ({
  event,
  detail: options?.detail,
}));

describe('Authentication Utilities', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.clear();
  });

  describe('Token Management', () => {
    test('setTokens should store tokens in localStorage', () => {
      setTokens('access_token_123', 'refresh_token_456');
      
      expect(localStorage.setItem).toHaveBeenCalledWith('auth_token', 'access_token_123');
      expect(localStorage.setItem).toHaveBeenCalledWith('refresh_token', 'refresh_token_456');
    });

    test('getAccessToken should retrieve token from localStorage', () => {
      localStorage.setItem('auth_token', 'test_access_token');
      
      const token = getAccessToken();
      
      expect(localStorage.getItem).toHaveBeenCalledWith('auth_token');
      expect(token).toBe('test_access_token');
    });

    test('getRefreshToken should retrieve refresh token from localStorage', () => {
      localStorage.setItem('refresh_token', 'test_refresh_token');
      
      const token = getRefreshToken();
      
      expect(localStorage.getItem).toHaveBeenCalledWith('refresh_token');
      expect(token).toBe('test_refresh_token');
    });

    test('clearTokens should remove tokens from localStorage', () => {
      clearTokens();
      
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth_token');
      expect(localStorage.removeItem).toHaveBeenCalledWith('refresh_token');
    });

    test('isAuthenticated should return true when token exists', () => {
      localStorage.setItem('auth_token', 'some_token');
      
      const result = isAuthenticated();
      
      expect(result).toBe(true);
    });

    test('isAuthenticated should return false when token does not exist', () => {
      // Ensure no token exists
      expect(localStorage.getItem('auth_token')).toBeNull();
      
      const result = isAuthenticated();
      
      expect(result).toBe(false);
    });
  });

  describe('Authentication Flow', () => {
    test('login should call API and store tokens on success', async () => {
      // Mock successful login response
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          access: 'new_access_token',
          refresh: 'new_refresh_token'
        })
      });
      
      await login('username', 'password');
      
      // Check if fetch was called correctly
      expect(fetch).toHaveBeenCalledWith('/api/v1/auth/token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: 'username', password: 'password' })
      });
      
      // Check if tokens were stored
      expect(localStorage.setItem).toHaveBeenCalledWith('auth_token', 'new_access_token');
      expect(localStorage.setItem).toHaveBeenCalledWith('refresh_token', 'new_refresh_token');
    });

    test('login should throw error on API failure', async () => {
      // Mock failed login response
      fetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({
          detail: 'Invalid credentials'
        })
      });
      
      await expect(login('wrong', 'credentials')).rejects.toThrow();
      
      // Tokens should not be set
      expect(localStorage.setItem).not.toHaveBeenCalledWith('auth_token', expect.any(String));
      expect(localStorage.setItem).not.toHaveBeenCalledWith('refresh_token', expect.any(String));
    });

    test('logout should clear tokens', () => {
      logout();
      
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth_token');
      expect(localStorage.removeItem).toHaveBeenCalledWith('refresh_token');
    });

    test('refreshAccessToken should call API and update access token', async () => {
      // Set refresh token
      localStorage.setItem('refresh_token', 'current_refresh_token');
      
      // Mock successful refresh response
      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          access: 'new_access_token'
        })
      });
      
      const result = await refreshAccessToken();
      
      // Check if fetch was called correctly
      expect(fetch).toHaveBeenCalledWith('/api/v1/auth/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: 'current_refresh_token' })
      });
      
      // Check if access token was updated
      expect(localStorage.setItem).toHaveBeenCalledWith('auth_token', 'new_access_token');
      
      // Should return the new token
      expect(result).toBe('new_access_token');
    });

    test('refreshAccessToken should throw error when no refresh token exists', async () => {
      // Ensure no refresh token exists
      expect(localStorage.getItem('refresh_token')).toBeNull();
      
      await expect(refreshAccessToken()).rejects.toThrow('No refresh token available');
      
      // No API call should be made
      expect(fetch).not.toHaveBeenCalled();
    });

    test('refreshAccessToken should clear tokens on API failure', async () => {
      // Set refresh token
      localStorage.setItem('refresh_token', 'invalid_refresh_token');
      
      // Mock failed refresh response
      fetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({
          detail: 'Token is invalid or expired'
        })
      });
      
      await expect(refreshAccessToken()).rejects.toThrow();
      
      // Tokens should be cleared
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth_token');
      expect(localStorage.removeItem).toHaveBeenCalledWith('refresh_token');
    });
  });

  describe('Authentication Events', () => {
    test('emitAuthStateChange should dispatch custom event', () => {
      emitAuthStateChange(true);
      
      expect(window.CustomEvent).toHaveBeenCalledWith('auth_state_changed', {
        detail: { isAuthenticated: true }
      });
      expect(window.dispatchEvent).toHaveBeenCalled();
    });

    test('setTokens should emit auth state change event', () => {
      setTokens('token123', 'refresh123');
      
      expect(window.dispatchEvent).toHaveBeenCalled();
      expect(window.CustomEvent).toHaveBeenCalledWith('auth_state_changed', {
        detail: { isAuthenticated: true }
      });
    });

    test('clearTokens should emit auth state change event', () => {
      clearTokens();
      
      expect(window.dispatchEvent).toHaveBeenCalled();
      expect(window.CustomEvent).toHaveBeenCalledWith('auth_state_changed', {
        detail: { isAuthenticated: false }
      });
    });
  });
});