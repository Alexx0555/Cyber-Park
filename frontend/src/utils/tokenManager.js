// Token Auto-Renewal Utility for JWT Authentication
// This utility automatically refreshes access tokens before they expire

const TOKEN_REFRESH_BUFFER = 5 * 60 * 1000; // Refresh 5 minutes before expiration

class TokenManager {
    constructor() {
        this.refreshTimer = null;
    }

    // Decode JWT to get expiration time (without verification)
    decodeToken(token) {
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(atob(base64).split('').map(c => {
                return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
            }).join(''));
            return JSON.parse(jsonPayload);
        } catch (error) {
            console.error('Failed to decode token:', error);
            return null;
        }
    }

    // Check if token is about to expire
    isTokenExpiringSoon(token) {
        const payload = this.decodeToken(token);
        if (!payload || !payload.exp) return true;

        const expirationTime = payload.exp * 1000; // Convert to milliseconds
        const currentTime = Date.now();
        const timeUntilExpiration = expirationTime - currentTime;

        return timeUntilExpiration <= TOKEN_REFRESH_BUFFER;
    }

    // Get time until token should be refreshed
    getTimeUntilRefresh(token) {
        const payload = this.decodeToken(token);
        if (!payload || !payload.exp) return 0;

        const expirationTime = payload.exp * 1000;
        const refreshTime = expirationTime - TOKEN_REFRESH_BUFFER;
        const currentTime = Date.now();

        return Math.max(0, refreshTime - currentTime);
    }

    // Refresh the access token using refresh token
    async refreshAccessToken() {
        const refreshToken = localStorage.getItem('refresh_token');

        if (!refreshToken) {
            console.warn('No refresh token available');
            this.handleTokenExpiration();
            return null;
        }

        try {
            const response = await fetch('/api/refresh', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ refresh_token: refreshToken })
            });

            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);
                console.log('✅ Access token refreshed successfully');

                // Schedule next refresh
                this.scheduleTokenRefresh();
                return data.access_token;
            } else {
                const error = await response.json();
                console.error('Token refresh failed:', error.message);
                this.handleTokenExpiration();
                return null;
            }
        } catch (error) {
            console.error('Token refresh error:', error);
            this.handleTokenExpiration();
            return null;
        }
    }

    // Handle token expiration (logout user)
    handleTokenExpiration() {
        console.warn('Token expired or refresh failed. Redirecting to login...');
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_role');

        // Redirect to login page
        if (window.location.pathname !== '/') {
            window.location.href = '/';
        }
    }

    // Schedule automatic token refresh
    scheduleTokenRefresh() {
        // Clear existing timer
        if (this.refreshTimer) {
            clearTimeout(this.refreshTimer);
        }

        const accessToken = localStorage.getItem('access_token');
        if (!accessToken) return;

        const timeUntilRefresh = this.getTimeUntilRefresh(accessToken);

        if (timeUntilRefresh <= 0) {
            // Token needs immediate refresh
            this.refreshAccessToken();
        } else {
            // Schedule refresh
            console.log(`⏰ Token refresh scheduled in ${Math.round(timeUntilRefresh / 1000 / 60)} minutes`);
            this.refreshTimer = setTimeout(() => {
                this.refreshAccessToken();
            }, timeUntilRefresh);
        }
    }

    // Initialize token management
    init() {
        const accessToken = localStorage.getItem('access_token');
        if (accessToken) {
            // Check if token needs immediate refresh
            if (this.isTokenExpiringSoon(accessToken)) {
                this.refreshAccessToken();
            } else {
                this.scheduleTokenRefresh();
            }
        }
    }

    // Stop token management
    stop() {
        if (this.refreshTimer) {
            clearTimeout(this.refreshTimer);
            this.refreshTimer = null;
        }
    }
}

// Create singleton instance
const tokenManager = new TokenManager();

// Auto-initialize when module is loaded and user is logged in
if (localStorage.getItem('access_token')) {
    tokenManager.init();
}

// Intercept fetch requests to handle 401 errors
const originalFetch = window.fetch;
window.fetch = async function (...args) {
    const response = await originalFetch.apply(this, args);

    // If we get 401 and have a refresh token, try to refresh
    if (response.status === 401) {
        const errorData = await response.clone().json();

        // Check if error is due to expired token
        if (errorData.message && errorData.message.includes('expired')) {
            console.log('🔄 Access token expired, attempting refresh...');
            const newToken = await tokenManager.refreshAccessToken();

            if (newToken) {
                // Retry the original request with new token
                const [url, options] = args;
                const newOptions = { ...options };

                if (newOptions.headers) {
                    newOptions.headers = {
                        ...newOptions.headers,
                        'Authorization': `Bearer ${newToken}`
                    };
                }

                return originalFetch(url, newOptions);
            }
        }
    }

    return response;
};

export default tokenManager;
