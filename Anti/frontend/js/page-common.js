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

            // Check if user needs to complete onboarding
            // Skip redirect if already on onboarding page
            const currentPath = window.location.pathname;
            const isOnboardingPage = currentPath.includes('onboarding.html');

            if (!data.user.onboardingCompleted && !isOnboardingPage) {
                // Redirect to onboarding for first-time users
                window.location.href = '/onboarding.html';
                return false;
            }

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

    const initials = getInitials(user.fullName || user.firstName || 'User');
    const displayName = user.fullName || user.firstName || 'User';
    const email = user.email || '';

    navAuth.innerHTML = `
        <div class="nav-user-info">
            <div class="nav-user-profile">
                <div class="nav-user-avatar">${initials}</div>
                <div class="nav-user-details">
                    <span class="nav-user-name">${displayName}</span>
                    <span class="nav-user-role">Investor</span>
                </div>
                <span class="nav-user-dropdown-icon">▼</span>
            </div>
            <div class="nav-user-dropdown">
                <div class="nav-dropdown-header">
                    <div class="avatar-large">${initials}</div>
                    <div class="user-fullname">${displayName}</div>
                    <div class="user-email">${email}</div>
                </div>
                <div class="nav-dropdown-menu">
                    <a href="/profile.html" class="nav-dropdown-item">
                        <img src="https://cdn-icons-png.flaticon.com/512/1077/1077114.png" alt="Profile">
                        My Profile
                    </a>
                    <a href="dashboard.html" class="nav-dropdown-item">
                        <img src="https://cdn-icons-png.flaticon.com/512/1828/1828765.png" alt="Dashboard">
                        Dashboard
                    </a>
                    <a href="my-portfolio.html" class="nav-dropdown-item">
                        <img src="https://cdn-icons-png.flaticon.com/512/2920/2920293.png" alt="Portfolio">
                        My Portfolio
                    </a>
                    <div class="nav-dropdown-divider"></div>
                    <button class="nav-dropdown-item logout" onclick="logout()">
                        <img src="https://cdn-icons-png.flaticon.com/512/1286/1286853.png" alt="Logout">
                        Sign Out
                    </button>
                </div>
            </div>
        </div>
    `;
}

function getInitials(name) {
    if (!name) return 'U';
    const parts = name.trim().split(' ').filter(p => p.length > 0);
    if (parts.length >= 2) {
        return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return parts[0].substring(0, 2).toUpperCase();
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

        // Check if response is JSON before parsing
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            console.error('API Error: Expected JSON but received:', contentType);
            return {
                success: false,
                error: `Server error (${response.status}). Please try again later.`
            };
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        // Provide user-friendly error message for JSON parse errors
        if (error.message && error.message.includes('Unexpected token')) {
            return { success: false, error: 'Server returned an invalid response. Please try again.' };
        }
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

        // Check if response is JSON before parsing
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            console.error('API Error: Expected JSON but received:', contentType);
            return {
                success: false,
                error: `Server error (${response.status}). Please try again later.`
            };
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        // Provide user-friendly error message for JSON parse errors
        if (error.message && error.message.includes('Unexpected token')) {
            return { success: false, error: 'Server returned an invalid response. Please try again.' };
        }
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
