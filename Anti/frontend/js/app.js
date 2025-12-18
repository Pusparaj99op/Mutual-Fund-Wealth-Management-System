/**
 * FIMFP - Federal Indian Mutual Fund Portal
 * Main Application JavaScript
 */

// API Base URL - Configure based on environment
// When running Flask server (python app.py), it runs on port 8009
// Leave empty if serving frontend from Flask static files
// Set to 'http://localhost:8009' if running frontend separately
const API_BASE = window.location.hostname === 'localhost' && window.location.port !== '8009'
    ? 'http://localhost:8009'
    : '';

// Global state
let currentSection = 'home';
let fundsData = [];
let currentPage = 1;
const pageSize = 20;
let currentUser = null;

// ============================================
// Authentication
// ============================================

async function checkAuthState() {
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
    return false;
}

function updateNavForLoggedInUser(user) {
    const navAuth = document.getElementById('navAuth');
    if (!navAuth) return;

    navAuth.innerHTML = `
        <div class="nav-user-info">
            <a href="/profile" class="nav-user-name" style="text-decoration: none; cursor: pointer;">👤 ${user.fullName || user.firstName}</a>
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

    // Clear local storage
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    currentUser = null;

    // Redirect to login
    window.location.href = '/login';
}

// ============================================
// Initialization
// ============================================

document.addEventListener('DOMContentLoaded', async function () {
    // Check authentication state first
    await checkAuthState();

    // Initialize hero image - random on each page refresh
    const heroImages = [
        'images/Gemini_Generated_Image_defdaqdefdaqdefd.png',
        'images/Gemini_Generated_Image_ssdwu2ssdwu2ssdw.png'
    ];
    const randomIndex = Math.floor(Math.random() * heroImages.length);
    const heroImg = document.getElementById('heroImage');
    if (heroImg) {
        heroImg.src = heroImages[randomIndex];
    }

    // Load categories for filter
    loadCategories();

    // Set up navigation
    setupNavigation();

    // Set up forms
    setupForms();

    // Load initial data
    loadFunds();

    console.log('🇮🇳 FIMFP Portal Initialized');
});

// ============================================
// Navigation
// ============================================

function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const section = this.dataset.section;
            showSection(section);
        });
    });
}

function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
    });

    // Show target section
    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.style.display = 'block';
    }

    // Update nav active state
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.section === sectionId) {
            link.classList.add('active');
        }
    });

    currentSection = sectionId;

    // Load section-specific data
    if (sectionId === 'analytics') {
        loadAnalytics();
    }

    // Scroll to top
    window.scrollTo(0, 0);
}

// ============================================
// API Helpers
// ============================================

async function apiGet(endpoint) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            credentials: 'include'
        });

        // Handle 401 - redirect to login
        if (response.status === 401) {
            window.location.href = '/login';
            return { success: false, error: 'Authentication required' };
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        return { success: false, error: error.message };
    }
}

async function apiPost(endpoint, body) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(body)
        });

        // Handle 401 - redirect to login
        if (response.status === 401) {
            window.location.href = '/login';
            return { success: false, error: 'Authentication required' };
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        return { success: false, error: error.message };
    }
}

// ============================================
// Funds Management
// ============================================

async function loadCategories() {
    const result = await apiGet('/api/categories');

    if (result.success && result.categories) {
        const categorySelect = document.getElementById('categoryFilter');
        if (categorySelect) {
            result.categories.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat;
                option.textContent = cat;
                categorySelect.appendChild(option);
            });
        }
    }
}

async function loadFunds(page = 1) {
    const offset = (page - 1) * pageSize;
    const result = await apiGet(`/api/funds?limit=${pageSize}&offset=${offset}`);

    if (result.success) {
        fundsData = result.data;
        renderFundsTable(result.data);
        renderPagination(result.total, page);

        // Update hero stat
        const totalFundsEl = document.getElementById('totalFunds');
        if (totalFundsEl) {
            totalFundsEl.textContent = result.total;
        }
    }
}

async function searchFunds() {
    const query = document.getElementById('searchQuery').value;
    const category = document.getElementById('categoryFilter').value;
    const riskLevel = document.getElementById('riskFilter').value;
    const minRating = document.getElementById('ratingFilter').value;

    let endpoint = '/api/funds?limit=100';
    if (query) endpoint += `&q=${encodeURIComponent(query)}`;
    if (category) endpoint += `&category=${encodeURIComponent(category)}`;
    if (riskLevel) endpoint += `&risk_level=${riskLevel}`;
    if (minRating) endpoint += `&min_rating=${minRating}`;

    const result = await apiGet(endpoint);

    if (result.success) {
        fundsData = result.data;
        renderFundsTable(result.data);
        renderPagination(result.total, 1);
    }
}

function renderFundsTable(funds) {
    const tbody = document.getElementById('fundsTableBody');
    if (!tbody) return;

    if (!funds || funds.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="empty-state">
                    <div class="empty-icon">📭</div>
                    <p>No funds found matching your criteria</p>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = funds.map(fund => `
        <tr>
            <td>
                <strong>${truncateText(fund.scheme_name, 40)}</strong>
            </td>
            <td>${truncateText(fund.amc_name, 20)}</td>
            <td>${fund.category || '-'}</td>
            <td class="rating-stars">${renderRating(fund.rating)}</td>
            <td class="${getReturnClass(fund.returns_1yr)}">${formatReturn(fund.returns_1yr)}</td>
            <td class="${getReturnClass(fund.returns_3yr)}">${formatReturn(fund.returns_3yr)}</td>
            <td>${fund.sharpe ? fund.sharpe.toFixed(2) : '-'}</td>
            <td>${renderRiskBadge(fund.risk_level)}</td>
            <td>
                <button class="btn btn-sm btn-outline" onclick="viewFundDetails(${fund.fund_id})">View</button>
                <button class="btn btn-sm btn-primary" onclick="predictFund(${fund.fund_id})">Predict</button>
            </td>
        </tr>
    `).join('');
}

function renderPagination(total, currentPage) {
    const container = document.getElementById('fundsPagination');
    if (!container) return;

    const totalPages = Math.ceil(total / pageSize);

    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = '';

    // Previous button
    html += `<button ${currentPage === 1 ? 'disabled' : ''} onclick="loadFunds(${currentPage - 1})">← Prev</button>`;

    // Page numbers
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);

    if (startPage > 1) {
        html += `<button onclick="loadFunds(1)">1</button>`;
        if (startPage > 2) html += `<span>...</span>`;
    }

    for (let i = startPage; i <= endPage; i++) {
        html += `<button class="${i === currentPage ? 'active' : ''}" onclick="loadFunds(${i})">${i}</button>`;
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) html += `<span>...</span>`;
        html += `<button onclick="loadFunds(${totalPages})">${totalPages}</button>`;
    }

    // Next button
    html += `<button ${currentPage === totalPages ? 'disabled' : ''} onclick="loadFunds(${currentPage + 1})">Next →</button>`;

    container.innerHTML = html;
}

async function viewFundDetails(fundId) {
    const result = await apiGet(`/api/fund/${fundId}`);

    if (result.success && result.data) {
        showFundModal(result.data);
    }
}

function showFundModal(fund) {
    const modal = document.getElementById('fundModal');
    const modalBody = document.getElementById('fundModalBody');

    if (!modal || !modalBody) return;

    modalBody.innerHTML = `
        <h2 style="color: var(--gov-primary); margin-bottom: var(--space-4);">${fund.scheme_name}</h2>
        <p style="color: var(--gray-600); margin-bottom: var(--space-6);">${fund.amc_name} | ${fund.category} | ${fund.sub_category}</p>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-4); margin-bottom: var(--space-6);">
            <div class="stat-card">
                <div class="stat-card-value">${formatReturn(fund.returns?.['1yr'])}</div>
                <div class="stat-card-label">1 Year Return</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-value">${formatReturn(fund.returns?.['3yr'])}</div>
                <div class="stat-card-label">3 Year Return</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-value">${formatReturn(fund.returns?.['5yr'])}</div>
                <div class="stat-card-label">5 Year Return</div>
            </div>
        </div>

        <h3 style="margin-bottom: var(--space-3);">Risk Metrics</h3>
        <table class="data-table" style="margin-bottom: var(--space-6);">
            <tr><td>Alpha</td><td>${fund.risk_metrics?.alpha || '-'}</td></tr>
            <tr><td>Beta</td><td>${fund.risk_metrics?.beta || '-'}</td></tr>
            <tr><td>Sharpe Ratio</td><td>${fund.risk_metrics?.sharpe || '-'}</td></tr>
            <tr><td>Sortino Ratio</td><td>${fund.risk_metrics?.sortino || '-'}</td></tr>
            <tr><td>Standard Deviation</td><td>${fund.risk_metrics?.std_dev || '-'}%</td></tr>
            <tr><td>Risk Level</td><td>${renderRiskBadge(fund.risk_metrics?.risk_level)}</td></tr>
        </table>

        <h3 style="margin-bottom: var(--space-3);">Fund Details</h3>
        <table class="data-table">
            <tr><td>Rating</td><td>${renderRating(fund.fund_details?.rating)}</td></tr>
            <tr><td>Expense Ratio</td><td>${fund.fund_details?.expense_ratio}%</td></tr>
            <tr><td>Fund Size</td><td>₹${fund.fund_details?.fund_size_cr} Cr</td></tr>
            <tr><td>Fund Age</td><td>${fund.fund_details?.fund_age_yr} Years</td></tr>
            <tr><td>Fund Manager</td><td>${fund.fund_details?.fund_manager}</td></tr>
            <tr><td>Min SIP</td><td>₹${fund.fund_details?.min_sip}</td></tr>
            <tr><td>Min Lumpsum</td><td>₹${fund.fund_details?.min_lumpsum}</td></tr>
        </table>

        <div style="margin-top: var(--space-6);">
            <button class="btn btn-primary" onclick="predictFund(${fund.fund_id}); closeModal();">
                Run AI Prediction
            </button>
        </div>
    `;

    modal.classList.add('active');
}

function closeModal() {
    const modal = document.getElementById('fundModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// ============================================
// Predictions
// ============================================

function setupForms() {
    // Prediction form
    const predictionForm = document.getElementById('predictionForm');
    if (predictionForm) {
        predictionForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            await runPrediction();
        });
    }

    // Risk profile form
    const riskProfileForm = document.getElementById('riskProfileForm');
    if (riskProfileForm) {
        riskProfileForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            await getRecommendations();
        });
    }

    // Optimizer form
    const optimizerForm = document.getElementById('optimizerForm');
    if (optimizerForm) {
        optimizerForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            await optimizePortfolio();
        });
    }

    // Advanced AI form
    const advancedForm = document.getElementById('advancedForm');
    if (advancedForm) {
        advancedForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            await runAdvancedAnalysis();
        });
    }

    // Compare form
    const compareForm = document.getElementById('compareForm');
    if (compareForm) {
        compareForm.addEventListener('submit', async function (e) {
            e.preventDefault();
            await compareFunds();
        });
    }
}

async function predictFund(fundId) {
    // Switch to prediction section
    showSection('predict');

    // Set fund ID
    document.getElementById('predictFundId').value = fundId;

    // Run prediction
    await runPrediction();
}

async function runPrediction() {
    const fundId = document.getElementById('predictFundId').value;
    const investment = document.getElementById('predictInvestment').value;
    const days = document.getElementById('predictDays').value;

    if (!fundId) {
        alert('Please enter a Fund ID');
        return;
    }

    // Show loading state
    document.getElementById('predictionEmpty').style.display = 'none';
    document.getElementById('predictionContent').innerHTML = '<div class="loading"></div>';
    document.getElementById('predictionContent').style.display = 'block';

    const result = await apiGet(`/api/predict/${fundId}?investment=${investment}&days=${days}`);

    if (result.success && result.data) {
        renderPredictionResults(result.data);
    } else {
        document.getElementById('predictionContent').innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">❌</div>
                <p>${result.error || 'Failed to generate prediction'}</p>
            </div>
        `;
    }
}

function renderPredictionResults(data) {
    const container = document.getElementById('predictionContent');
    const chartContainer = document.getElementById('predictionChartContainer');

    const stats = data.statistics;
    const risk = data.risk_metrics;
    const ci = data.confidence_intervals;

    container.innerHTML = `
        <div style="margin-bottom: var(--space-6);">
            <h4 style="color: var(--gov-primary);">${data.fund?.scheme_name || 'Fund'}</h4>
            <p style="color: var(--gray-500);">Prediction for ${data.prediction_days} days | ${data.n_simulations.toLocaleString()} simulations</p>
        </div>

        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-4); margin-bottom: var(--space-6);">
            <div class="stat-card">
                <div class="stat-card-value">₹${stats.mean_nav.toLocaleString('en-IN')}</div>
                <div class="stat-card-label">Expected Value</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-value" style="color: ${stats.expected_return_pct >= 0 ? 'var(--success)' : 'var(--error)'}">
                    ${stats.expected_return_pct >= 0 ? '+' : ''}${stats.expected_return_pct}%
                </div>
                <div class="stat-card-label">Expected Return</div>
            </div>
        </div>

        <h4 style="margin-bottom: var(--space-3);">Confidence Intervals</h4>
        <div style="background: var(--gray-100); padding: var(--space-4); border-radius: var(--radius); margin-bottom: var(--space-4);">
            <p><strong>90% Confidence:</strong> ₹${ci['90%'].lower.toLocaleString('en-IN')} - ₹${ci['90%'].upper.toLocaleString('en-IN')}</p>
            <p><strong>50% Confidence:</strong> ₹${ci['50%'].lower.toLocaleString('en-IN')} - ₹${ci['50%'].upper.toLocaleString('en-IN')}</p>
        </div>

        <h4 style="margin-bottom: var(--space-3);">Risk Metrics</h4>
        <table class="data-table">
            <tr><td>Value at Risk (95%)</td><td class="badge badge-warning">₹${risk.var_95.toLocaleString('en-IN')}</td></tr>
            <tr><td>Value at Risk (99%)</td><td class="badge badge-error">₹${risk.var_99.toLocaleString('en-IN')}</td></tr>
            <tr><td>CVaR (95%)</td><td>₹${risk.cvar_95.toLocaleString('en-IN')}</td></tr>
            <tr><td>Probability of Loss</td><td>${risk.probability_of_loss}%</td></tr>
        </table>
    `;

    container.style.display = 'block';

    // Render chart
    if (data.sample_paths && data.sample_paths.length > 0) {
        chartContainer.style.display = 'block';
        window.chartUtils.createMonteCarloChart('predictionChart', data.sample_paths, data.current_nav, data.prediction_days);
    }
}

// ============================================
// Recommendations
// ============================================

async function getRecommendations() {
    const age = document.getElementById('userAge').value;
    const income = document.getElementById('userIncome').value;
    const horizon = document.getElementById('userHorizon').value;
    const lossTolerance = document.getElementById('userLossTolerance').value;
    const experience = document.getElementById('userExperience').value;
    const investment = document.getElementById('userInvestment').value;

    // Show loading
    const recommendationsCard = document.getElementById('recommendationsCard');
    recommendationsCard.style.display = 'block';
    document.getElementById('recommendationsList').innerHTML = '<div class="loading"></div>';

    const result = await apiPost('/api/recommend', {
        age: age,
        income: income,
        horizon: horizon,
        loss_tolerance: lossTolerance,
        experience: experience,
        investment: investment,
        top_n: 10
    });

    if (result.success && result.data) {
        renderRiskProfile(result.data.risk_profile);
        renderRecommendations(result.data.recommendations);
    } else {
        document.getElementById('recommendationsList').innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">❌</div>
                <p>${result.error || 'Failed to get recommendations'}</p>
            </div>
        `;
    }
}

function renderRiskProfile(profile) {
    const card = document.getElementById('riskProfileCard');
    const display = document.getElementById('riskProfileDisplay');

    if (!profile) return;

    card.style.display = 'block';

    display.innerHTML = `
        <div class="risk-level-badge risk-level-${profile.risk_level}">${profile.risk_level}</div>
        <div class="risk-profile-name">${profile.risk_profile}</div>
        <div class="equity-allocation">
            <strong>Recommended Equity Allocation:</strong><br>
            ${profile.recommended_equity_allocation[0]}% - ${profile.recommended_equity_allocation[1]}%
        </div>
        <p style="color: var(--gray-600); font-size: var(--font-size-sm);">
            Volatility Tolerance: ${profile.volatility_tolerance}%
        </p>
    `;
}

function renderRecommendations(recommendations) {
    const container = document.getElementById('recommendationsList');

    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <p>No recommendations found</p>
            </div>
        `;
        return;
    }

    container.innerHTML = recommendations.map((rec, index) => `
        <div class="recommendation-item">
            <div class="recommendation-rank">${index + 1}</div>
            <div class="recommendation-info">
                <h4>${truncateText(rec.scheme_name, 50)}</h4>
                <p>${rec.amc_name} | ${rec.category}</p>
                ${rec.insights && rec.insights.length > 0 ?
            `<p style="color: var(--success); font-size: var(--font-size-xs);">✓ ${rec.insights[0]}</p>` : ''}
            </div>
            <div class="recommendation-metrics">
                <div class="metric">
                    <span class="metric-value">${rec.rating}</span>
                    <span class="metric-label">Rating</span>
                </div>
                <div class="metric">
                    <span class="metric-value">${formatReturn(rec.metrics?.returns?.['1yr'])}</span>
                    <span class="metric-label">1Y Return</span>
                </div>
                <div class="metric">
                    <span class="metric-value">${rec.metrics?.risk?.sharpe?.toFixed(2) || '-'}</span>
                    <span class="metric-label">Sharpe</span>
                </div>
                <div class="metric">
                    <span class="metric-value" style="color: var(--gov-primary);">${rec.recommendation_score}</span>
                    <span class="metric-label">Score</span>
                </div>
            </div>
        </div>
    `).join('');
}

// ============================================
// Portfolio Optimization
// ============================================

async function optimizePortfolio() {
    const fundIdsStr = document.getElementById('optimizeFundIds').value;
    const investment = document.getElementById('optimizeInvestment').value;

    const fundIds = fundIdsStr.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id));

    if (fundIds.length < 2) {
        alert('Please enter at least 2 fund IDs');
        return;
    }

    // Show loading
    const resultsCard = document.getElementById('optimizationResults');
    resultsCard.style.display = 'block';
    document.getElementById('optimizationContent').innerHTML = '<div class="loading"></div>';

    const result = await apiPost('/api/optimize', {
        fund_ids: fundIds,
        investment: parseFloat(investment)
    });

    if (result.success && result.data) {
        renderOptimizationResults(result.data, parseFloat(investment));
    } else {
        document.getElementById('optimizationContent').innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">❌</div>
                <p>${result.error || 'Failed to optimize portfolio'}</p>
            </div>
        `;
    }
}

function renderOptimizationResults(data, investment) {
    const container = document.getElementById('optimizationContent');
    const chartsRow = document.getElementById('optimizationCharts');

    const metrics = data.portfolio_metrics;

    container.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-4); margin-bottom: var(--space-6);">
            <div class="stat-card">
                <div class="stat-card-value" style="color: var(--success);">${metrics.expected_return}%</div>
                <div class="stat-card-label">Expected Return</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-value" style="color: var(--warning);">${metrics.volatility}%</div>
                <div class="stat-card-label">Volatility</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-value">${metrics.sharpe_ratio}</div>
                <div class="stat-card-label">Sharpe Ratio</div>
            </div>
        </div>

        <h4 style="margin-bottom: var(--space-3);">Recommended Allocation</h4>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Fund</th>
                    <th>Weight</th>
                    <th>Amount</th>
                </tr>
            </thead>
            <tbody>
                ${data.allocations.map(alloc => `
                    <tr>
                        <td>${truncateText(alloc.scheme_name, 40)}</td>
                        <td><strong>${alloc.weight}%</strong></td>
                        <td>₹${(investment * alloc.weight / 100).toLocaleString('en-IN', { maximumFractionDigits: 0 })}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    // Show charts
    chartsRow.style.display = 'grid';

    // Create allocation chart
    window.chartUtils.createAllocationChart('allocationChart', data.allocations);

    // Create efficient frontier chart
    if (data.efficient_frontier) {
        window.chartUtils.createFrontierChart('frontierChart', data.efficient_frontier, metrics);
    }
}

// ============================================
// Analytics
// ============================================

async function loadAnalytics() {
    const result = await apiGet('/api/analytics/summary');

    if (result.success && result.data) {
        renderAnalytics(result.data);
    }
}

function renderAnalytics(data) {
    // Render stats cards
    const statsContainer = document.getElementById('analyticsStats');
    statsContainer.innerHTML = `
        <div class="stat-card">
            <div class="stat-card-value">${data.total_funds}</div>
            <div class="stat-card-label">Total Funds</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-value" style="color: var(--success);">${data.returns_summary.average_1yr}%</div>
            <div class="stat-card-label">Avg 1Y Return</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-value">${data.returns_summary.max_1yr}%</div>
            <div class="stat-card-label">Max 1Y Return</div>
        </div>
        <div class="stat-card">
            <div class="stat-card-value">${data.sharpe_summary.average}</div>
            <div class="stat-card-label">Avg Sharpe</div>
        </div>
    `;

    // Create charts
    window.chartUtils.createCategoryChart('categoryChart', data.category_distribution);
    window.chartUtils.createReturnsChart('returnsChart', data.category_avg_returns);
}

// ============================================
// Advanced AI Analysis
// ============================================

async function runAdvancedAnalysis() {
    const fundId = document.getElementById('advFundId').value;
    const analysisType = document.getElementById('advAnalysisType').value;

    if (!fundId) {
        alert('Please enter a Fund ID');
        return;
    }

    // Show loading
    document.getElementById('advancedEmpty').style.display = 'none';
    const content = document.getElementById('advancedContent');
    content.innerHTML = '<div class="loading"></div>';
    content.style.display = 'block';

    let endpoint;
    switch (analysisType) {
        case 'ml_prediction':
            endpoint = `/api/advanced/ml-predict/${fundId}`;
            break;
        case 'momentum':
            endpoint = `/api/advanced/momentum/${fundId}`;
            break;
        case 'factor':
            endpoint = `/api/advanced/factor/${fundId}`;
            break;
        case 'sentiment':
            endpoint = `/api/advanced/sentiment/${fundId}`;
            break;
        case 'all':
        default:
            endpoint = `/api/advanced/complete/${fundId}`;
    }

    const result = await apiGet(endpoint);

    if (result.success && result.data) {
        renderAdvancedResults(result, analysisType);
    } else {
        content.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">❌</div>
                <p>${result.error || 'Failed to run analysis'}</p>
            </div>
        `;
    }
}

function renderAdvancedResults(result, analysisType) {
    const content = document.getElementById('advancedContent');
    const data = result.data;
    const fund = result.fund || {};

    let html = `
        <div style="margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid var(--gray-200);">
            <h4 style="color: var(--gov-navy); margin-bottom: 5px;">${fund.scheme_name || 'Fund Analysis'}</h4>
            <p style="font-size: 0.8rem; color: var(--gray-500);">Fund ID: ${fund.fund_id || 'N/A'}</p>
        </div>
    `;

    if (analysisType === 'ml_prediction') {
        html += renderMLPrediction(data);
    } else if (analysisType === 'momentum') {
        html += renderMomentum(data);
    } else if (analysisType === 'factor') {
        html += renderFactorAnalysis(data);
    } else if (analysisType === 'sentiment') {
        html += renderSentiment(data);
    } else {
        // Complete analysis
        html += `
            <div style="display: grid; gap: 15px;">
                <div class="gov-notice">
                    <strong>🤖 AI/ML Complete Analysis</strong> - 10 models applied
                </div>

                <h4>📊 Monte Carlo Simulation</h4>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 15px;">
                    <div class="stat-card">
                        <div class="stat-card-value">₹${data.monte_carlo?.expected_value?.toLocaleString('en-IN') || 'N/A'}</div>
                        <div class="stat-card-label">Expected Value</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-card-value" style="color: var(--success);">+${data.monte_carlo?.expected_return || 0}%</div>
                        <div class="stat-card-label">Expected Return</div>
                    </div>
                </div>

                <h4>🤖 ML Return Prediction</h4>
                ${renderMLPrediction(data.ml_prediction)}

                <h4>🚀 Momentum Analysis</h4>
                ${renderMomentum(data.momentum)}

                <h4>🎯 Factor Model (6 Factors)</h4>
                ${renderFactorAnalysis(data.factor_analysis)}

                <h4>💭 Market Sentiment</h4>
                ${renderSentiment(data.sentiment)}

                <h4>📉 Drawdown Analysis</h4>
                <table class="data-table">
                    <tr><td>Max Drawdown</td><td><span class="badge badge-error">${data.drawdown?.max_drawdown || 0}%</span></td></tr>
                    <tr><td>Calmar Ratio</td><td>${data.drawdown?.calmar_ratio || 0}</td></tr>
                    <tr><td>Pain Index</td><td>${data.drawdown?.pain_index || 0}</td></tr>
                </table>
            </div>
        `;
    }

    content.innerHTML = html;
}

function renderMLPrediction(data) {
    if (!data) return '<p>No ML prediction data available</p>';

    const predClass = data.prediction_class || 'UNKNOWN';
    const classColors = {
        'HIGH_GROWTH': 'badge-success',
        'MODERATE_GROWTH': 'badge-success',
        'STABLE': 'badge-info',
        'LOW_GROWTH': 'badge-warning',
        'NEGATIVE': 'badge-error'
    };

    return `
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 15px;">
            <div class="stat-card">
                <div class="stat-card-value" style="color: var(--success);">${data.predicted_return || 0}%</div>
                <div class="stat-card-label">Predicted Return</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-value">${data.prediction_confidence || 0}%</div>
                <div class="stat-card-label">Confidence</div>
            </div>
        </div>
        <p><strong>Classification:</strong> <span class="badge ${classColors[predClass] || ''}">${predClass}</span></p>
        <p style="font-size: 0.8rem; color: var(--gray-500);">
            Range: ${data.prediction_range?.lower || 0}% to ${data.prediction_range?.upper || 0}%
        </p>
    `;
}

function renderMomentum(data) {
    if (!data) return '<p>No momentum data available</p>';

    const signalColors = {
        'STRONG_BUY': 'badge-success',
        'BUY': 'badge-success',
        'HOLD': 'badge-info',
        'SELL': 'badge-warning',
        'STRONG_SELL': 'badge-error'
    };

    return `
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 10px;">
            <div class="stat-card">
                <div class="stat-card-value">${data.combined_score || 0}</div>
                <div class="stat-card-label">Momentum Score</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-value">
                    <span class="badge ${signalColors[data.signal] || ''}">${data.signal || 'N/A'}</span>
                </div>
                <div class="stat-card-label">Signal</div>
            </div>
        </div>
        <p><strong>Trend Strength:</strong> ${data.trend_strength || 'Unknown'}</p>
    `;
}

function renderFactorAnalysis(data) {
    if (!data || !data.factors) return '<p>No factor data available</p>';

    const factors = data.factors;
    return `
        <table class="data-table">
            <tr><td>Market β</td><td>${factors.market?.toFixed(3) || 0}</td></tr>
            <tr><td>Quality</td><td>${factors.quality?.toFixed(3) || 0}</td></tr>
            <tr><td>Momentum</td><td>${factors.momentum?.toFixed(3) || 0}</td></tr>
            <tr><td>Low Vol</td><td>${factors.low_volatility?.toFixed(3) || 0}</td></tr>
            <tr><td>Size</td><td>${factors.size?.toFixed(3) || 0}</td></tr>
            <tr><td>Value</td><td>${factors.value?.toFixed(3) || 0}</td></tr>
        </table>
        <p style="margin-top: 10px;"><strong>Composite Score:</strong> ${data.composite_score || 0}</p>
        <p><strong>Dominant Factor:</strong> <span class="badge badge-info">${data.dominant_factor || 'N/A'}</span></p>
    `;
}

function renderSentiment(data) {
    if (!data) return '<p>No sentiment data available</p>';

    const sentimentColors = {
        'EXTREME_GREED': 'badge-success',
        'GREED': 'badge-success',
        'NEUTRAL': 'badge-info',
        'FEAR': 'badge-warning',
        'EXTREME_FEAR': 'badge-error'
    };

    return `
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 10px;">
            <div class="stat-card">
                <div class="stat-card-value">${data.fear_greed_index || 50}</div>
                <div class="stat-card-label">Fear & Greed</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-value">
                    <span class="badge ${sentimentColors[data.sentiment] || ''}">${data.sentiment || 'N/A'}</span>
                </div>
                <div class="stat-card-label">Sentiment</div>
            </div>
        </div>
        <p><strong>Trend:</strong> ${data.trend || 'Unknown'}</p>
        <p><strong>Recommendation:</strong> <span class="badge badge-info">${data.recommendation || 'N/A'}</span></p>
    `;
}

// ============================================
// Utility Functions
// ============================================

function truncateText(text, maxLength) {
    if (!text) return '-';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function formatReturn(value) {
    if (value === null || value === undefined) return '-';
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(1)}%`;
}

function getReturnClass(value) {
    if (value === null || value === undefined) return '';
    return value >= 0 ? 'badge badge-success' : 'badge badge-error';
}

function renderRating(rating) {
    if (!rating) return '-';
    let stars = '';
    for (let i = 0; i < 5; i++) {
        stars += i < rating ? '★' : '☆';
    }
    return stars;
}

function renderRiskBadge(riskLevel) {
    if (!riskLevel) return '-';

    const colors = {
        1: 'badge-success',
        2: 'badge-success',
        3: 'badge-warning',
        4: 'badge-warning',
        5: 'badge-error',
        6: 'badge-error'
    };

    const labels = {
        1: 'Very Low',
        2: 'Low',
        3: 'Moderate',
        4: 'High',
        5: 'Very High',
        6: 'Extreme'
    };

    return `<span class="badge ${colors[riskLevel] || ''}">${labels[riskLevel] || riskLevel}</span>`;
}

// ============================================
// Fund Comparison
// ============================================

let compareCharts = {};

async function compareFunds() {
    const fundIdsInput = document.getElementById('compareFundIds').value;
    const fundIds = fundIdsInput.split(',').map(id => parseInt(id.trim())).filter(id => !isNaN(id));

    if (fundIds.length < 2) {
        alert('Please enter at least 2 fund IDs to compare');
        return;
    }

    if (fundIds.length > 5) {
        alert('Maximum 5 funds can be compared at once');
        return;
    }

    // Show results container
    document.getElementById('compareResults').style.display = 'block';

    // Fetch fund data
    const fundsPromises = fundIds.map(id => apiGet(`/api/fund/${id}`));
    const results = await Promise.all(fundsPromises);

    const funds = results.filter(r => r.success).map(r => r.data);

    if (funds.length < 2) {
        alert('Could not fetch enough fund data. Please check the fund IDs.');
        return;
    }

    // Render comparison table
    renderCompareTable(funds);

    // Render comparison charts
    renderCompareCharts(funds);
}

function renderCompareTable(funds) {
    const thead = document.getElementById('compareTableHead');
    const tbody = document.getElementById('compareTableBody');

    // Table headers
    let headerHtml = '<tr><th>Metric</th>';
    funds.forEach(fund => {
        const name = fund.scheme_name || fund.name || `Fund ${fund.fund_id}`;
        headerHtml += `<th>${name.substring(0, 30)}...</th>`;
    });
    headerHtml += '</tr>';
    thead.innerHTML = headerHtml;

    // Table rows
    const metrics = [
        { key: 'amc_name', label: 'AMC' },
        { key: 'category', label: 'Category' },
        { key: 'rating', label: 'Rating', format: v => v ? '⭐'.repeat(Math.min(v, 5)) : 'N/A' },
        { key: 'risk_level', label: 'Risk Level' },
        { key: 'returns_1yr', label: '1Y Return', format: v => v ? `${(v * 100).toFixed(2)}%` : 'N/A' },
        { key: 'returns_3yr', label: '3Y Return', format: v => v ? `${(v * 100).toFixed(2)}%` : 'N/A' },
        { key: 'returns_5yr', label: '5Y Return', format: v => v ? `${(v * 100).toFixed(2)}%` : 'N/A' },
        { key: 'sharpe_ratio', label: 'Sharpe Ratio', format: v => v ? v.toFixed(2) : 'N/A' },
        { key: 'expense_ratio', label: 'Expense Ratio', format: v => v ? `${(v * 100).toFixed(2)}%` : 'N/A' },
        { key: 'aum', label: 'AUM (Cr)', format: v => v ? `₹${v.toFixed(0)}` : 'N/A' }
    ];

    let bodyHtml = '';
    metrics.forEach(metric => {
        bodyHtml += `<tr><td><strong>${metric.label}</strong></td>`;
        funds.forEach(fund => {
            const value = fund[metric.key];
            const displayValue = metric.format ? metric.format(value) : (value || 'N/A');
            bodyHtml += `<td>${displayValue}</td>`;
        });
        bodyHtml += '</tr>';
    });
    tbody.innerHTML = bodyHtml;
}

function renderCompareCharts(funds) {
    // Destroy existing charts
    Object.values(compareCharts).forEach(chart => chart.destroy());
    compareCharts = {};

    const colors = [
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 99, 132, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(153, 102, 255, 0.8)'
    ];

    // Returns Bar Chart
    const returnsCtx = document.getElementById('compareReturnsChart').getContext('2d');
    compareCharts.returns = new Chart(returnsCtx, {
        type: 'bar',
        data: {
            labels: ['1Y Return', '3Y Return', '5Y Return'],
            datasets: funds.map((fund, i) => ({
                label: (fund.scheme_name || `Fund ${fund.fund_id}`).substring(0, 20),
                data: [
                    (fund.returns_1yr || 0) * 100,
                    (fund.returns_3yr || 0) * 100,
                    (fund.returns_5yr || 0) * 100
                ],
                backgroundColor: colors[i],
                borderWidth: 1
            }))
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'top', labels: { color: '#fff' } } },
            scales: {
                y: { title: { display: true, text: 'Return (%)', color: '#fff' }, ticks: { color: '#ccc' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                x: { ticks: { color: '#ccc' }, grid: { color: 'rgba(255,255,255,0.1)' } }
            }
        }
    });

    // Radar Chart
    const radarCtx = document.getElementById('compareRadarChart').getContext('2d');
    compareCharts.radar = new Chart(radarCtx, {
        type: 'radar',
        data: {
            labels: ['Low Risk', 'Rating', 'Low Cost', 'Sharpe', '5Y Return'],
            datasets: funds.map((fund, i) => ({
                label: (fund.scheme_name || `Fund ${fund.fund_id}`).substring(0, 15),
                data: [
                    fund.risk_level ? (7 - fund.risk_level) * 16 : 50,
                    (fund.rating || 3) * 20,
                    fund.expense_ratio ? (1 - fund.expense_ratio) * 100 : 50,
                    fund.sharpe_ratio ? Math.min(fund.sharpe_ratio * 30, 100) : 50,
                    fund.returns_5yr ? Math.min(fund.returns_5yr * 500, 100) : 50
                ],
                backgroundColor: colors[i].replace('0.8', '0.3'),
                borderColor: colors[i],
                borderWidth: 2
            }))
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'right', labels: { color: '#fff' } } },
            scales: { r: { angleLines: { color: 'rgba(255,255,255,0.2)' }, grid: { color: 'rgba(255,255,255,0.2)' }, pointLabels: { color: '#fff' }, ticks: { display: false } } }
        }
    });

    // Scatter Chart (Risk-Return)
    const scatterCtx = document.getElementById('compareScatterChart').getContext('2d');
    compareCharts.scatter = new Chart(scatterCtx, {
        type: 'scatter',
        data: {
            datasets: funds.map((fund, i) => ({
                label: (fund.scheme_name || `Fund ${fund.fund_id}`).substring(0, 20),
                data: [{ x: fund.risk_level || 3, y: (fund.returns_3yr || 0) * 100 }],
                backgroundColor: colors[i],
                pointRadius: 12,
                pointHoverRadius: 15
            }))
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'top', labels: { color: '#fff' } } },
            scales: {
                x: { title: { display: true, text: 'Risk Level', color: '#fff' }, min: 0, max: 7, ticks: { color: '#ccc' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                y: { title: { display: true, text: '3Y Return (%)', color: '#fff' }, ticks: { color: '#ccc' }, grid: { color: 'rgba(255,255,255,0.1)' } }
            }
        }
    });
}

// ============================================
// Event Listeners
// ============================================

// Close modal on escape key
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// Font size adjustment
document.getElementById('langSize')?.addEventListener('click', function () {
    const currentSize = parseFloat(getComputedStyle(document.documentElement).fontSize);
    document.documentElement.style.fontSize = (currentSize + 1) + 'px';
    setTimeout(() => {
        document.documentElement.style.fontSize = '';
    }, 3000);
});

