// Authentication utility functions

const TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

// Custom event for auth state changes
const AUTH_STATE_CHANGED = 'auth_state_changed';

export const emitAuthStateChange = (isAuthenticated) => {
    window.dispatchEvent(new CustomEvent(AUTH_STATE_CHANGED, { detail: { isAuthenticated } }));
};

export const setTokens = (accessToken, refreshToken) => {
    localStorage.setItem(TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    emitAuthStateChange(true);
};

export const getAccessToken = () => {
    return localStorage.getItem(TOKEN_KEY);
};

export const getRefreshToken = () => {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
};

export const clearTokens = () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    emitAuthStateChange(false);
};

export const isAuthenticated = () => {
    return !!getAccessToken();
};

export const login = async (username, password) => {
    try {
        const response = await fetch('/api/v1/auth/token/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Login failed');
        }

        setTokens(data.access, data.refresh);
        return true;
    } catch (error) {
        console.error('Login error:', error);
        throw error;
    }
};

export const logout = () => {
    clearTokens();
};

export const refreshAccessToken = async () => {
    try {
        const refreshToken = getRefreshToken();
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        const response = await fetch('/api/v1/auth/token/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ refresh: refreshToken }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'Token refresh failed');
        }

        localStorage.setItem(TOKEN_KEY, data.access);
        emitAuthStateChange(true);
        return data.access;
    } catch (error) {
        console.error('Token refresh error:', error);
        clearTokens();
        throw error;
    }
};