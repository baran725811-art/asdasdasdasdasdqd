//core\static\dashboard\js\pages\charts.js - Grafik yönetimi
/**
 * ==========================================================================
 * CHARTS JAVASCRIPT
 * Chart.js implementations for dashboard analytics
 * ==========================================================================
 */

class ChartManager {
    constructor() {
        this.charts = new Map();
        this.colors = {
            primary: 'rgba(102, 126, 234, 1)',
            primaryLight: 'rgba(102, 126, 234, 0.1)',
            success: 'rgba(17, 153, 142, 1)',
            successLight: 'rgba(17, 153, 142, 0.1)',
            warning: 'rgba(255, 193, 7, 1)',
            warningLight: 'rgba(255, 193, 7, 0.1)',
            danger: 'rgba(220, 53, 69, 1)',
            dangerLight: 'rgba(220, 53, 69, 0.1)',
            info: 'rgba(52, 152, 219, 1)',
            infoLight: 'rgba(52, 152, 219, 0.1)'
        };
        this.init();
        this.setupThemeListener();

    }
    
    init() {
        console.log('📊 Chart Manager initializing...');
        
        // Set Chart.js defaults
        this.setChartDefaults();
        
        // Initialize charts
        this.initializeMonthlyChart();
        this.initializeCategoryChart();
        this.setupChartControls();
        
        console.log('✅ Chart Manager initialized successfully');
    }
    
    setChartDefaults() {
        if (typeof Chart !== 'undefined') {
            Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
            Chart.defaults.color = '#6c757d';
            Chart.defaults.borderColor = 'rgba(0, 0, 0, 0.05)';
            Chart.defaults.plugins.legend.labels.usePointStyle = true;
            Chart.defaults.plugins.legend.labels.padding = 20;
        }
    }
    
    initializeMonthlyChart() {
        const monthlyCtx = document.getElementById('monthlyChart');
        if (!monthlyCtx) return;
        
        console.log('📈 Initializing monthly chart...');
        
        try {
            // Get data from template variables or data attributes
            const monthlyData = this.getMonthlyChartData();
            
            if (!monthlyData || monthlyData.labels.length === 0) {
                this.showNoDataMessage(monthlyCtx.parentElement, 'Aylık veriler bulunamadı');
                return;
            }
            
            const chart = new Chart(monthlyCtx, {
                type: 'line',
                data: monthlyData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: 'white',
                            bodyColor: 'white',
                            borderColor: this.colors.primary,
                            borderWidth: 1,
                            cornerRadius: 8,
                            padding: 12
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.05)'
                            },
                            ticks: {
                                stepSize: 1,
                                callback: function(value) {
                                    return Number.isInteger(value) ? value : '';
                                }
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    },
                    interaction: {
                        intersect: false,
                        mode: 'index'
                    },
                    elements: {
                        line: {
                            tension: 0.4
                        },
                        point: {
                            radius: 6,
                            hoverRadius: 8
                        }
                    },
                    animation: {
                        duration: 1000,
                        easing: 'easeInOutQuart'
                    }
                }
            });
            
            this.charts.set('monthly', chart);
            console.log('✅ Monthly chart initialized');
            
        } catch (error) {
            console.error('❌ Monthly chart initialization error:', error);
            this.showErrorMessage(monthlyCtx.parentElement, 'Grafik yüklenirken hata oluştu');
        }
    }
    
    initializeCategoryChart() {
        const categoryCtx = document.getElementById('categoryChart');
        if (!categoryCtx) return;
        
        console.log('🍩 Initializing category chart...');
        
        try {
            const categoryData = this.getCategoryChartData();
            
            if (!categoryData || categoryData.datasets[0].data.length === 0) {
                this.showNoDataMessage(categoryCtx.parentElement, 'Kategori verileri bulunamadı');
                return;
            }
            
            const chart = new Chart(categoryCtx, {
                type: 'doughnut',
                data: categoryData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true,
                                font: {
                                    size: 12
                                }
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleColor: 'white',
                            bodyColor: 'white',
                            borderColor: this.colors.primary,
                            borderWidth: 1,
                            cornerRadius: 8,
                            padding: 12,
                            callbacks: {
                                label: (context) => {
                                    const total = context.dataset.data.reduce((sum, value) => sum + value, 0);
                                    if (total <= 0) {
                                        return 'Henüz kategori eklenmemiş';
                                    }
                                    const value = context.parsed;
                                    const percentage = ((value / total) * 100).toFixed(1);
                                    return `${context.label}: ${value} ürün (${percentage}%)`;
                                }
                            }
                        }
                    },
                    cutout: '60%',
                    animation: {
                        animateScale: true,
                        duration: 1000,
                        easing: 'easeInOutQuart'
                    }
                }
            });
            
            this.charts.set('category', chart);
            console.log('✅ Category chart initialized');
            
        } catch (error) {
            console.error('❌ Category chart initialization error:', error);
            this.showErrorMessage(categoryCtx.parentElement, 'Grafik yüklenirken hata oluştu');
        }
    }
    
    getMonthlyChartData() {
        // Öncelikle window.monthlyStatsData'yı kontrol et
        if (typeof window.monthlyStatsData !== 'undefined' && window.monthlyStatsData.labels.length > 0) {
            console.log('✅ Using window.monthlyStatsData');
            return window.monthlyStatsData;
        }

        console.log('❌ window.monthlyStatsData bulunamadı, fallback kullanılıyor');

        // Fallback structure
        return {
            labels: ['Veri Yok'],
            datasets: [
                {
                    label: 'Ürünler',
                    data: [0],
                    borderColor: this.colors.primary,
                    backgroundColor: this.colors.primaryLight,
                    tension: 0.4,
                    fill: true
                }
            ]
        };
    }
    
    getCategoryChartData() {
        // Öncelikle window.categoryStatsData'yı kontrol et
        if (typeof window.categoryStatsData !== 'undefined' && window.categoryStatsData.labels.length > 0) {
            console.log('✅ Using window.categoryStatsData');
            return window.categoryStatsData;
        }

        console.log('❌ window.categoryStatsData bulunamadı, fallback kullanılıyor');

        // Fallback structure
        return {
            labels: ['Veri Yok'],
            datasets: [{
                data: [1],
                backgroundColor: ['rgba(200, 200, 200, 0.8)'],
                borderColor: ['rgba(200, 200, 200, 1)'],
                borderWidth: 2
            }]
        };
    }
    
    


    setupChartControls() {
        // Period selector for charts - Doğru selector kullan
        const periodSelectors = document.querySelectorAll('.period-option');
        periodSelectors.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const period = btn.dataset.period;
                const chartId = btn.dataset.chart;
                
                console.log(`Period değiştirildi: ${period} gün, Chart: ${chartId}`);
                
                // Dropdown butonunun textini güncelle
                const dropdownButton = document.getElementById(`periodSelector${chartId}`);
                if (dropdownButton) {
                    dropdownButton.textContent = `Son ${period} Gün`;
                }
                
                // Dropdown'ı kapat
                const dropdown = bootstrap.Dropdown.getInstance(dropdownButton);
                if (dropdown) {
                    dropdown.hide();
                }
                
                // Grafik verilerini yenile (şimdilik mock data)
                this.updateChartForPeriod(chartId, period);
            });
        });
        
        // Chart export buttons (mevcut kod aynı kalacak)
        const exportButtons = document.querySelectorAll('.chart-export-btn');
        exportButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.exportChart(btn.dataset.chartId, btn.dataset.format);
            });
        });
        
        // Chart refresh buttons (mevcut kod aynı kalacak)
        const refreshButtons = document.querySelectorAll('.chart-refresh-btn');
        refreshButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.refreshChart(btn.dataset.chartId);
            });
        });
    }
    
    updateChartForPeriod(chartId, period) {
        console.log(`Grafik güncelleniyor: ${chartId}, Period: ${period}`);
        
        // Şimdilik sadece console log, ileride API call olacak
        const chart = this.charts.get(chartId);
        if (chart) {
            // Mock data - ileride gerçek API'den veri gelecek
            chart.update('none');
            this.showNotification(`Grafik ${period} güne güncellendi.`, 'success');
        }
    }

    
    async fetchChartData(chartId, period) {
        const response = await fetch(`/dashboard/api/charts/${chartId}/?period=${period}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': this.getCSRFToken()
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    updateChart(chartId, newData) {
        const chart = this.charts.get(chartId);
        if (!chart) return;
        
        // Update chart data
        chart.data.labels = newData.labels;
        chart.data.datasets.forEach((dataset, index) => {
            if (newData.datasets[index]) {
                dataset.data = newData.datasets[index].data;
            }
        });
        
        // Animate update
        chart.update('active');
        
        console.log(`✅ Chart ${chartId} updated`);
    }
    
    exportChart(chartId, format = 'png') {
        const chart = this.charts.get(chartId);
        if (!chart) return;
        
        try {
            const url = chart.toBase64Image();
            const link = document.createElement('a');
            link.download = `chart-${chartId}-${new Date().toISOString().split('T')[0]}.${format}`;
            link.href = url;
            link.click();
            
            this.showNotification('Grafik başarıyla indirildi.', 'success');
        } catch (error) {
            console.error('Chart export error:', error);
            this.showNotification('Grafik indirilemedi.', 'error');
        }
    }
    
    refreshChart(chartId) {
        console.log(`🔄 Refreshing chart ${chartId}`);
        
        // Show loading state
        const chartContainer = document.getElementById(chartId)?.parentElement;
        if (chartContainer) {
            this.showLoadingState(chartContainer);
        }
        
        // Simulate data refresh
        setTimeout(() => {
            if (chartId === 'monthlyChart') {
                this.initializeMonthlyChart();
            } else if (chartId === 'categoryChart') {
                this.initializeCategoryChart();
            }
            
            this.showNotification('Grafik güncellendi.', 'success');
        }, 1000);
    }
    
    showLoadingState(container) {
        const overlay = document.createElement('div');
        overlay.className = 'chart-loading-overlay';
        overlay.style.cssText = `
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10;
        `;
        overlay.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Yükleniyor...</span></div>';
        
        container.style.position = 'relative';
        container.appendChild(overlay);
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (overlay.parentNode) {
                overlay.remove();
            }
        }, 3000);
    }
    
    showNoDataMessage(container, message) {
        container.innerHTML = `
            <div class="chart-no-data">
                <i class="fas fa-chart-bar mb-3"></i>
                <h6>${message}</h6>
                <p class="text-muted mb-0">Veriler yüklendiğinde grafik burada görünecektir.</p>
            </div>
        `;
    }
    
    showErrorMessage(container, message) {
        container.innerHTML = `
            <div class="chart-no-data">
                <i class="fas fa-exclamation-triangle text-warning mb-3"></i>
                <h6>${message}</h6>
                <p class="text-muted mb-0">Sayfayı yenilemeyi deneyin.</p>
                <button class="btn btn-sm btn-primary mt-2" onclick="location.reload()">
                    <i class="fas fa-refresh me-1"></i>Yenile
                </button>
            </div>
        `;
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        const icon = type === 'success' ? 'check-circle' : 
                    type === 'error' ? 'exclamation-circle' : 
                    type === 'warning' ? 'exclamation-triangle' : 'info-circle';
        
        notification.innerHTML = `
            <i class="fas fa-${icon} me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
    
    // Public methods for external use
    getChart(chartId) {
        return this.charts.get(chartId);
    }
    
    destroyChart(chartId) {
        const chart = this.charts.get(chartId);
        if (chart) {
            chart.destroy();
            this.charts.delete(chartId);
        }
    }
    
    destroyAllCharts() {
        this.charts.forEach((chart, chartId) => {
            chart.destroy();
        });
        this.charts.clear();
    }


    // Class'a YENİ METHOD ekle:
    setupThemeListener() {
        // Tema değişikliğini dinle
        document.addEventListener('themeChanged', (e) => {
            console.log('🎨 Theme changed, updating charts...', e.detail);
            this.updateChartsForTheme(e.detail.newTheme);
        });
    }


    updateChartsForTheme(theme) {
        // Tema renklerini al
        const isDark = theme === 'dark' || theme === 'reading';
        const textColor = isDark ? '#e2e8f0' : '#6c757d';
        const gridColor = isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)';
        
        // Tüm grafikleri güncelle
        this.charts.forEach((chart, chartId) => {
            // Grid renklerini güncelle
            if (chart.options.scales) {
                if (chart.options.scales.y) {
                    chart.options.scales.y.grid.color = gridColor;
                    chart.options.scales.y.ticks.color = textColor;
                }
                if (chart.options.scales.x) {
                    chart.options.scales.x.ticks.color = textColor;
                }
            }
            
            // Legend renklerini güncelle
            if (chart.options.plugins.legend) {
                chart.options.plugins.legend.labels.color = textColor;
            }
            
            // Grafiği yenile
            chart.update('none');
        });
        
        console.log('✅ Charts updated for theme:', theme);
    }


    
}

// Chart utilities
const ChartUtils = {
    // Generate color palette
    generateColors(count) {
        const colors = [
            'rgba(102, 126, 234, 0.8)',
            'rgba(17, 153, 142, 0.8)',
            'rgba(32, 156, 255, 0.8)',
            'rgba(247, 151, 30, 0.8)',
            'rgba(252, 70, 107, 0.8)',
            'rgba(153, 102, 255, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(255, 159, 64, 0.8)'
        ];
        
        if (count <= colors.length) {
            return colors.slice(0, count);
        }
        
        // Generate additional colors if needed
        const additionalColors = [];
        for (let i = colors.length; i < count; i++) {
            const hue = (i * 360 / count) % 360;
            additionalColors.push(`hsla(${hue}, 70%, 60%, 0.8)`);
        }
        
        return [...colors, ...additionalColors];
    },
    
    // Format numbers for display
    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    },
    
    // Calculate percentage
    calculatePercentage(part, total) {
        if (total === 0) return 0;
        return Math.round((part / total) * 100);
    }
};

// Initialize chart manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if Chart.js is available and we're on a page with charts
    if (typeof Chart !== 'undefined' && document.querySelector('canvas[id$="Chart"]')) {
        window.chartManager = new ChartManager();
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.chartManager) {
        window.chartManager.destroyAllCharts();
    }
});

// Export for global use
window.ChartManager = ChartManager;
window.ChartUtils = ChartUtils;