/**
 * FIMFP - Federal Indian Mutual Fund Portal
 * Chart Utilities and Visualizations
 */

// Chart.js default configuration for government portal styling
Chart.defaults.font.family = "'Noto Sans', Arial, sans-serif";
Chart.defaults.color = '#334155';

// Color palette
const chartColors = {
    primary: '#0b3d91',
    primaryLight: '#1a5276',
    saffron: '#FF9933',
    green: '#138808',
    blue: '#1e88e5',
    purple: '#7c3aed',
    pink: '#ec4899',
    teal: '#14b8a6',
    orange: '#f97316',
    red: '#ef4444',
    gray: '#6b7280'
};

// Color palette array for multiple series
const colorPalette = [
    chartColors.primary,
    chartColors.saffron,
    chartColors.green,
    chartColors.blue,
    chartColors.purple,
    chartColors.pink,
    chartColors.teal,
    chartColors.orange,
    chartColors.red
];

/**
 * Create a Monte Carlo simulation chart
 */
function createMonteCarloChart(canvasId, samplePaths, currentNav, days) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');

    // Generate x-axis labels (days)
    const labels = Array.from({ length: days }, (_, i) => i + 1);

    // Create datasets for each sample path
    const datasets = samplePaths.map((path, index) => ({
        label: `Path ${index + 1}`,
        data: path,
        borderColor: colorPalette[index % colorPalette.length],
        backgroundColor: 'transparent',
        borderWidth: 1,
        pointRadius: 0,
        tension: 0.1
    }));

    // Add starting value line
    datasets.push({
        label: 'Initial Investment',
        data: Array(days).fill(currentNav),
        borderColor: chartColors.gray,
        borderDash: [5, 5],
        borderWidth: 2,
        pointRadius: 0
    });

    // Destroy existing chart if exists
    if (window.monteCarloChart) {
        window.monteCarloChart.destroy();
    }

    window.monteCarloChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Monte Carlo Simulation - Sample Paths',
                    font: { size: 14, weight: 'bold' }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function (context) {
                            return `${context.dataset.label}: ₹${context.parsed.y.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Days'
                    },
                    ticks: {
                        maxTicksLimit: 10
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Value (₹)'
                    },
                    ticks: {
                        callback: function (value) {
                            return '₹' + value.toLocaleString('en-IN', { maximumFractionDigits: 0 });
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });

    return window.monteCarloChart;
}

/**
 * Create a pie chart for portfolio allocation
 */
function createAllocationChart(canvasId, allocations) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');

    const labels = allocations.map(a => a.scheme_name ?
        (a.scheme_name.length > 30 ? a.scheme_name.substring(0, 30) + '...' : a.scheme_name) :
        `Fund ${a.fund_id}`);
    const data = allocations.map(a => a.weight);

    // Destroy existing chart if exists
    if (window.allocationChart) {
        window.allocationChart.destroy();
    }

    window.allocationChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colorPalette.slice(0, allocations.length),
                borderColor: '#ffffff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        padding: 10,
                        font: { size: 11 }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.label}: ${context.parsed.toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });

    return window.allocationChart;
}

/**
 * Create an efficient frontier chart
 */
function createFrontierChart(canvasId, frontierData, optimalPoint) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');

    // Create frontier line data
    const frontierPoints = frontierData.volatilities.map((vol, i) => ({
        x: vol,
        y: frontierData.returns[i]
    }));

    const datasets = [
        {
            label: 'Efficient Frontier',
            data: frontierPoints,
            borderColor: chartColors.primary,
            backgroundColor: 'rgba(11, 61, 145, 0.1)',
            borderWidth: 2,
            pointRadius: 2,
            fill: true,
            showLine: true,
            tension: 0.4
        }
    ];

    // Add optimal portfolio point
    if (optimalPoint) {
        datasets.push({
            label: 'Optimal Portfolio',
            data: [{
                x: optimalPoint.volatility,
                y: optimalPoint.expected_return
            }],
            pointRadius: 10,
            pointBackgroundColor: chartColors.saffron,
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            showLine: false
        });
    }

    // Destroy existing chart if exists
    if (window.frontierChart) {
        window.frontierChart.destroy();
    }

    window.frontierChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'top'
                },
                title: {
                    display: true,
                    text: 'Risk-Return Tradeoff',
                    font: { size: 14, weight: 'bold' }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `Return: ${context.parsed.y.toFixed(2)}%, Risk: ${context.parsed.x.toFixed(2)}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Volatility (%)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Expected Return (%)'
                    }
                }
            }
        }
    });

    return window.frontierChart;
}

/**
 * Create a category distribution chart
 */
function createCategoryChart(canvasId, categoryData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');

    const labels = Object.keys(categoryData);
    const data = Object.values(categoryData);

    // Destroy existing chart if exists
    if (window.categoryChart) {
        window.categoryChart.destroy();
    }

    window.categoryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Funds',
                data: data,
                backgroundColor: colorPalette,
                borderColor: colorPalette.map(c => c),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: false
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Number of Funds'
                    }
                },
                y: {
                    ticks: {
                        font: { size: 10 }
                    }
                }
            }
        }
    });

    return window.categoryChart;
}

/**
 * Create a returns comparison chart
 */
function createReturnsChart(canvasId, returnsData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');

    // Sort by returns descending
    const sorted = Object.entries(returnsData)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);

    const labels = sorted.map(([cat]) => cat);
    const data = sorted.map(([, ret]) => ret);

    // Destroy existing chart if exists
    if (window.returnsChart) {
        window.returnsChart.destroy();
    }

    window.returnsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average 1Y Return (%)',
                data: data,
                backgroundColor: data.map(v => v >= 0 ? chartColors.green : chartColors.red),
                borderColor: data.map(v => v >= 0 ? chartColors.green : chartColors.red),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                        font: { size: 9 }
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Return (%)'
                    }
                }
            }
        }
    });

    return window.returnsChart;
}

/**
 * Create hero section animated chart
 */
function createHeroChart() {
    const canvas = document.getElementById('heroChart');
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');

    // Generate sample growth data
    const labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const portfolioData = [100, 105, 103, 112, 118, 122, 120, 128, 135, 142, 138, 150];
    const benchmarkData = [100, 102, 101, 106, 108, 110, 109, 112, 115, 118, 116, 120];

    // Destroy existing chart if exists
    if (window.heroChart) {
        window.heroChart.destroy();
    }

    window.heroChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'AI-Optimized Portfolio',
                    data: portfolioData,
                    borderColor: chartColors.saffron,
                    backgroundColor: 'rgba(255, 153, 51, 0.1)',
                    borderWidth: 3,
                    pointRadius: 4,
                    pointBackgroundColor: chartColors.saffron,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Benchmark',
                    data: benchmarkData,
                    borderColor: 'rgba(255, 255, 255, 0.5)',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointRadius: 0,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: 'rgba(255, 255, 255, 0.9)',
                        padding: 20
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)'
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.7)',
                        callback: function (value) {
                            return '₹' + value;
                        }
                    }
                }
            }
        }
    });

    return window.heroChart;
}

/**
 * Create a prediction distribution histogram
 */
function createDistributionChart(canvasId, percentiles) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');

    const labels = Object.keys(percentiles);
    const data = Object.values(percentiles);

    // Destroy existing chart if exists
    if (window.distributionChart) {
        window.distributionChart.destroy();
    }

    window.distributionChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Value',
                data: data,
                backgroundColor: colorPalette.slice(0, labels.length),
                borderColor: colorPalette.slice(0, labels.length),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Value Distribution at Horizon'
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function (value) {
                            return '₹' + value.toLocaleString('en-IN');
                        }
                    }
                }
            }
        }
    });

    return window.distributionChart;
}

// Export functions for use in app.js
window.chartUtils = {
    createMonteCarloChart,
    createAllocationChart,
    createFrontierChart,
    createCategoryChart,
    createReturnsChart,
    createHeroChart,
    createDistributionChart,
    colors: chartColors,
    palette: colorPalette
};
