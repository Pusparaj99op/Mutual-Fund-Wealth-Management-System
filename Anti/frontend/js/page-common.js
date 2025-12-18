/**
 * FIMFP - Federal Indian Mutual Fund Portal
 * Page Common JavaScript - Shared across all feature pages
 */

// API Base URL
const API_BASE = window.location.hostname === 'localhost' && window.location.port !== '8009'
    ? 'http://localhost:8009'
    : '';

// Current user state
let currentUser = null;

// ============================================
// Authentication Check on Page Load
// ============================================

async function checkAuthAndRedirect() {
    try {
        const response = await fetch(`${API_BASE}/api/auth/me`, {
            credentials: 'include'
        });
        const data = await response.json();

        if (data.success && data.user) {
            currentUser = data.user;
            updateNavForLoggedInUser(data.user);
            return true;
        }
    } catch (error) {
        console.log('Auth check failed:', error);
    }

    // Not authenticated - redirect to login
    const currentPath = window.location.pathname;
    sessionStorage.setItem('redirectAfterLogin', currentPath);
    window.location.href = '/login.html';
    return false;
}

function updateNavForLoggedInUser(user) {
    const navAuth = document.getElementById('navAuth');
    if (!navAuth) return;

    navAuth.innerHTML = `
        <div class="nav-user-info">
            <a href="/profile.html" class="nav-user-name" style="text-decoration: none; cursor: pointer;">
                <img src="https://cdn-icons-png.flaticon.com/512/1077/1077114.png" alt="User" style="width: 16px; height: 16px; vertical-align: middle; margin-right: 5px;">
                ${user.fullName || user.firstName}
            </a>
            <button class="btn-nav-logout" onclick="logout()">Logout</button>
        </div>
    `;
}

async function logout() {
    try {
        await fetch(`${API_BASE}/api/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        });
    } catch (error) {
        console.log('Logout error:', error);
    }

    localStorage.removeItem('user');
    localStorage.removeItem('token');
    currentUser = null;
    window.location.href = '/login.html';
}

// ============================================
// API Helpers
// ============================================

async function apiGet(endpoint) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            credentials: 'include'
        });

        if (response.status === 401) {
            window.location.href = '/login.html';
            return { success: false, error: 'Authentication required' };
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return { success: false, error: error.message };
    }
}

async function apiPost(endpoint, body) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(body)
        });

        if (response.status === 401) {
            window.location.href = '/login.html';
            return { success: false, error: 'Authentication required' };
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return { success: false, error: error.message };
    }
}

// ============================================
// Helper Functions
// ============================================

function truncateText(text, maxLength) {
    if (!text) return '-';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
}

function formatReturn(value) {
    if (value === null || value === undefined) return '-';
    const num = parseFloat(value);
    return (num >= 0 ? '+' : '') + num.toFixed(2) + '%';
}

function getReturnClass(value) {
    if (value === null || value === undefined) return '';
    return parseFloat(value) >= 0 ? 'text-success' : 'text-error';
}

function renderRating(rating) {
    if (!rating) return '-';
    return '★'.repeat(Math.floor(rating)) + '☆'.repeat(5 - Math.floor(rating));
}

function renderRiskBadge(riskLevel) {
    const riskLabels = {
        1: 'Very Low',
        2: 'Low',
        3: 'Moderate',
        4: 'High',
        5: 'Very High',
        6: 'Extreme'
    };
    const riskColors = {
        1: '#4CAF50',
        2: '#8BC34A',
        3: '#FF9800',
        4: '#FF5722',
        5: '#F44336',
        6: '#9C27B0'
    };

    const label = riskLabels[riskLevel] || 'Unknown';
    const color = riskColors[riskLevel] || '#9E9E9E';

    return `<span class="badge" style="background: ${color}; color: #fff;">${label}</span>`;
}

function showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = '<div class="loading"></div>';
    }
}

function showError(containerId, message) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="empty-state">
                <img src="https://cdn-icons-png.flaticon.com/512/753/753345.png" alt="Error" style="width: 48px; height: 48px; opacity: 0.5; margin-bottom: 15px;">
                <p>${message}</p>
            </div>
        `;
    }
}

function showEmpty(containerId, message) {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `
            <div class="empty-state">
                <img src="https://cdn-icons-png.flaticon.com/512/3588/3588614.png" alt="Empty" style="width: 48px; height: 48px; opacity: 0.5; margin-bottom: 15px;">
                <p>${message}</p>
            </div>
        `;
    }
}

// ============================================
// Navigation Active State
// ============================================

function setActiveNav() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        const href = link.getAttribute('href');
        if (currentPath === href || (currentPath.includes(href) && href !== '/')) {
            link.classList.add('active');
        }
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async function () {
    const isAuthenticated = await checkAuthAndRedirect();
    if (isAuthenticated) {
        setActiveNav();
        // Call page-specific init if exists
        if (typeof pageInit === 'function') {
            pageInit();
        }
    }
});

// Export for use
window.pageCommon = {
    apiGet,
    apiPost,
    truncateText,
    formatReturn,
    getReturnClass,
    renderRating,
    renderRiskBadge,
    showLoading,
    showError,
    showEmpty,
    currentUser: () => currentUser
};
