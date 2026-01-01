/**
 * Authentication Logic
 * Handles login, token management, and user authentication
 */

const API_BASE = window.location.origin;

// Check if user is authenticated
async function checkAuth() {
    const token = localStorage.getItem('token');
    
    if (!token) {
        if (window.location.pathname !== '/' && !window.location.pathname.includes('index.html')) {
            window.location.href = '/';
        }
        return false;
    }

    try {
        const response = await fetch(`${API_BASE}/api/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            localStorage.removeItem('token');
            if (window.location.pathname !== '/') {
                window.location.href = '/';
            }
            return false;
        }

        const user = await response.json();
        
        // Update UI with user info
        const usernameElement = document.getElementById('currentUsername');
        if (usernameElement) {
            usernameElement.textContent = user.username;
        }
        
        // Also update header username if present
        const headerUsername = document.getElementById('headerUsername');
        if (headerUsername) {
            headerUsername.textContent = user.username;
        }

        return true;
    } catch (error) {
        console.error('Auth check failed:', error);
        localStorage.removeItem('token');
        if (window.location.pathname !== '/') {
            window.location.href = '/';
        }
        return false;
    }
}

// Handle login form submission
if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorMessage = document.getElementById('errorMessage');
        const spinner = document.getElementById('loadingSpinner');
        const submitButton = e.target.querySelector('button[type="submit"]');

        // Show loading state
        errorMessage.classList.remove('show');
        spinner.classList.remove('hidden');
        submitButton.disabled = true;

        try {
            const response = await fetch(`${API_BASE}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Login fehlgeschlagen');
            }

            // Store token
            localStorage.setItem('token', data.access_token);

            // Redirect to dashboard
            window.location.href = '/dashboard';

        } catch (error) {
            errorMessage.textContent = error.message || 'Fehler beim Anmelden. Bitte versuchen Sie es erneut.';
            errorMessage.classList.add('show');
            submitButton.disabled = false;
        } finally {
            spinner.classList.add('hidden');
        }
    });
}

// API helper function with authentication
async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        }
    };

    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, mergedOptions);

        if (response.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/';
            throw new Error('Unauthorized');
        }

        return response;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Show toast notification
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}
