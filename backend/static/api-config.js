/**
 * SportSkyline Frontend Integration - API Configuration
 * Supports both Local and Production environments
 */
const SportSkylineAPI = {
    // Detect environment
    BASE_URL: window.location.origin.includes('localhost') 
        ? 'http://localhost:8000/api/v1' 
        : window.location.origin + '/api/v1',
    
    MAX_RETRIES: 3,
    
    async fetch(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.BASE_URL}${endpoint}`, options);
            if (!response.ok) throw new Error('Network response was not ok');
            return await response.json();
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            return null;
        }
    }
};
