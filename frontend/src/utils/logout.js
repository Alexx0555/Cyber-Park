// Logout utility to handle user logout with token blacklisting

export async function logout() {
    const accessToken = localStorage.getItem('access_token');

    if (accessToken) {
        try {
            // Call logout endpoint to blacklist the token
            await fetch('/api/logout', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json'
                }
            });
        } catch (error) {
            console.error('Logout API call failed:', error);
            // Continue with local logout even if API call fails
        }
    }

    // Clear all tokens from localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');

    // Stop token manager
    const tokenManager = await import('./tokenManager.js');
    tokenManager.default.stop();

    // Redirect to login page
    window.location.href = '/';
}

export default { logout };
