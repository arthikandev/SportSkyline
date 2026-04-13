/**
 * SportSkyline Admin Dashboard - Core JS
 * Handles Auth, Routing, and API Interaction
 */

const API_BASE = window.location.origin.includes('localhost') 
    ? 'http://localhost:8000/api/v1' 
    : window.location.origin + '/api/v1';

// --- State Management ---
const state = {
    token: localStorage.getItem('ss_admin_token'),
    user: JSON.parse(localStorage.getItem('ss_admin_user')),
    currentView: 'dashboard'
};

// --- API Client ---
async function apiFetch(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (state.token) {
        headers['Authorization'] = `Bearer ${state.token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
    });

    if (response.status === 401 && endpoint !== '/admin/auth/login') {
        logout();
        throw new Error('Session expired');
    }

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.detail || 'API Error');
    }
    return data;
}

// --- Auth Manager ---
async function login(email, password) {
    try {
        const data = await apiFetch('/admin/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });

        state.token = data.access_token;
        localStorage.setItem('ss_admin_token', data.access_token);
        
        // Fetch user profile
        const user = await apiFetch('/admin/auth/me');
        state.user = user;
        localStorage.setItem('ss_admin_user', JSON.stringify(user));

        showDashboard();
        showToast('Welcome back, ' + user.full_name);
    } catch (err) {
        document.getElementById('login-error').textContent = err.message;
    }
}

function logout() {
    state.token = null;
    state.user = null;
    localStorage.removeItem('ss_admin_token');
    localStorage.removeItem('ss_admin_user');
    window.location.hash = '';
    showLogin();
}

// --- View Renderer ---
function showLogin() {
    document.getElementById('login-screen').classList.remove('hidden');
    document.getElementById('dashboard-shell').classList.add('hidden');
}

function showDashboard() {
    document.getElementById('login-screen').classList.add('hidden');
    document.getElementById('dashboard-shell').classList.remove('hidden');
    document.getElementById('admin-name').textContent = state.user.full_name;
    document.getElementById('admin-avatar').textContent = state.user.full_name[0].toUpperCase();
    
    // Initial route handling
    handleRoute();
}

const views = {
    dashboard: async () => {
        return `
            <div class="stats-grid">
                <div class="stat-card">
                    <label>Total Articles</label>
                    <div class="value">--</div>
                </div>
                <div class="stat-card">
                    <label>Live Matches</label>
                    <div class="value">--</div>
                </div>
                <div class="stat-card">
                    <label>View Count (24h)</label>
                    <div class="value">--</div>
                </div>
            </div>
            <div class="welcome-msg">
                <h2>Welcome to the SportSkyline Admin Panel</h2>
                <p>Use the sidebar to manage your content and sports data.</p>
            </div>
        `;
    },
    articles: async () => {
        return `
            <div class="view-header">
                <h2>Articles Management</h2>
                <button class="btn-primary" onclick="window.location.hash='#articles/new'">+ Create Article</button>
            </div>
            <div class="table-container">
                <table id="articles-table">
                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>Status</th>
                            <th>Date</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td colspan="4" class="text-center">Loading articles...</td></tr>
                    </tbody>
                </table>
            </div>
        `;
    }
    // Other views will be implemented as needed
};

async function renderView(viewName) {
    const container = document.getElementById('content-view');
    container.innerHTML = '<div class="loader"><div class="spinner"></div></div>';
    
    const pageTitle = viewName.charAt(0).toUpperCase() + viewName.slice(1);
    document.getElementById('page-title').textContent = pageTitle;

    // Update nav active state
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.toggle('active', link.dataset.view === viewName);
    });

    try {
        if (views[viewName]) {
            container.innerHTML = await views[viewName]();
        } else {
            container.innerHTML = `<div class="p-4">View ${viewName} coming soon.</div>`;
        }
    } catch (err) {
        container.innerHTML = `<div class="error-msg">${err.message}</div>`;
    }
}

// --- Routing ---
function handleRoute() {
    const hash = window.location.hash.slice(1) || 'dashboard';
    const view = hash.split('/')[0];
    state.currentView = view;
    renderView(view);
}

// --- Utilities ---
function showToast(msg) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 3000);
}

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
    // Initial checks
    if (state.token && state.user) {
        showDashboard();
    } else {
        showLogin();
    }

    // Event Listeners
    document.getElementById('login-form').addEventListener('submit', (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        login(email, password);
    });

    document.getElementById('logout-btn').addEventListener('click', logout);

    window.addEventListener('hashchange', handleRoute);
});
