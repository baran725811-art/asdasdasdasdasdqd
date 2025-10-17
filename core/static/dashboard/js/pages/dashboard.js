// core\static\dashboard\js\pages\dashboard.js - Dashboard fonksiyonları
/**
 * ==========================================================================
 * DASHBOARD HOME PAGE JAVASCRIPT
 * Main dashboard page functionality and interactions
 * ==========================================================================
 */

class DashboardManager {
    constructor() {
        this.refreshInterval = null;
        this.refreshIntervalTime = 30000; // 30 seconds
        this.init();
    }
    
    init() {
        console.log('🏠 Dashboard Manager initializing...');
        
        this.initializeCharts();
        this.setupCategoryModal();
        this.setupWelcomeSection();
        this.setupQuickActions();
        this.setupActivityFeed();
        this.setupAutoRefresh();
        this.loadDashboardStats();
        this.setupThemeIntegration();

        console.log('✅ Dashboard Manager initialized successfully');
    }
    
    initializeCharts() {
        // Initialize monthly statistics chart
        this.initializeMonthlyChart();
        
        // Initialize category distribution chart
        this.initializeCategoryChart();
    }
    
    initializeMonthlyChart() {
        const monthlyCtx = document.getElementById('monthlyChart');
        if (!monthlyCtx || typeof Chart === 'undefined') return;
        
        console.log('📈 Initializing monthly dashboard chart...');
        
        try {
            // Get data from template or API
            const monthlyData = this.getMonthlyStatsData();
            
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
                    animation: {
                        duration: 1000,
                        easing: 'easeInOutQuart'
                    }
                }
            });
            
            console.log('✅ Monthly chart initialized');
            
        } catch (error) {
            console.error('❌ Monthly chart error:', error);
        }
    }
    
    initializeCategoryChart() {
        const categoryCtx = document.getElementById('categoryChart');
        if (!categoryCtx || typeof Chart === 'undefined') return;
        
        console.log('🍩 Initializing category dashboard chart...');
        
        try {
            const categoryData = this.getCategoryStatsData();
            
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
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            cornerRadius: 8,
                            padding: 12,
                            callbacks: {
                                label: (context) => {
                                    const total = categoryData.datasets[0].data.reduce((a, b) => a + b, 0);
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
                        duration: 1000
                    }
                }
            });
            
            console.log('✅ Category chart initialized');
            
        } catch (error) {
            console.error('❌ Category chart error:', error);
        }
    }
    
    getMonthlyStatsData() {
        // Try to get data from global variables or data attributes
        if (typeof window.monthlyStatsData !== 'undefined') {
            return window.monthlyStatsData;
        }
        
        // Fallback data structure
        return {
            labels: [],
            datasets: [
                {
                    label: 'Ürünler',
                    data: [],
                    borderColor: 'rgba(102, 126, 234, 1)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6
                },
                {
                    label: 'Yorumlar',
                    data: [],
                    borderColor: 'rgba(17, 153, 142, 1)',
                    backgroundColor: 'rgba(17, 153, 142, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: 'rgba(17, 153, 142, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6
                },
                {
                    label: 'Mesajlar',
                    data: [],
                    borderColor: 'rgba(255, 193, 7, 1)',
                    backgroundColor: 'rgba(255, 193, 7, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: 'rgba(255, 193, 7, 1)',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6
                }
            ]
        };
    }
    
    getCategoryStatsData() {
        // Try to get data from global variables
        if (typeof window.categoryStatsData !== 'undefined') {
            return window.categoryStatsData;
        }
        
        // Fallback data
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
    
    setupCategoryModal() {
        // Category modal management
        const categoryModal = document.getElementById('categoriesModal');
        if (!categoryModal) return;
        
        console.log('🏷️ Setting up category modal...');
        
        // Load categories when modal is shown
        categoryModal.addEventListener('shown.bs.modal', () => {
            this.loadCategoriesModal();
        });
        
        // Setup modal interactions
        const categoryItems = categoryModal.querySelectorAll('.category-item-modern');
        categoryItems.forEach(item => {
            item.addEventListener('click', () => {
                this.toggleCategoryDetails(item);
            });
        });
    }
    
    loadCategoriesModal() {
        const modalContent = document.getElementById('categoryModalContent');
        if (!modalContent) return;
        
        // Show loading state
        modalContent.innerHTML = `
            <div class="text-center p-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Yükleniyor...</span>
                </div>
                <p class="mt-2 text-muted">Kategoriler yükleniyor...</p>
            </div>
        `;
        
        // Fetch categories
        fetch('/dashboard/api/categories/summary/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.renderCategoriesModal(data.categories);
            } else {
                this.showCategoriesError();
            }
        })
        .catch(error => {
            console.error('Categories load error:', error);
            this.showCategoriesError();
        });
    }
    
    renderCategoriesModal(categories) {
        const modalContent = document.getElementById('categoryModalContent');
        
        if (categories.length === 0) {
            modalContent.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">
                        <i class="fas fa-folder-open"></i>
                    </div>
                    <h6>Henüz kategori eklenmemiş</h6>
                    <p>Kategoriler ekledikçe burada görünecekler.</p>
                </div>
            `;
            return;
        }
        
        const categoryList = categories.map(category => `
            <div class="category-item-modern" data-category-id="${category.id}">
                <div class="category-info">
                    <div class="category-color-indicator" style="background-color: ${category.color || '#667eea'}"></div>
                    <div class="category-details">
                        <h6 class="category-name">${category.name}</h6>
                        <div class="category-progress">
                            <div class="progress-bar-modern">
                                <div class="progress-fill" style="width: ${category.percentage}%; background-color: ${category.color || '#667eea'}"></div>
                            </div>
                            <span class="progress-text">${category.percentage}%</span>
                        </div>
                    </div>
                </div>
                <div class="category-count">
                    <div class="count-badge">${category.product_count}</div>
                    <div class="count-label">Ürün</div>
                </div>
            </div>
        `).join('');
        
        modalContent.innerHTML = `
            <div class="category-list-modern">
                ${categoryList}
            </div>
        `;
    }
    
    showCategoriesError() {
        const modalContent = document.getElementById('categoryModalContent');
        modalContent.innerHTML = `
            <div class="text-center p-4">
                <i class="fas fa-exclamation-triangle text-warning mb-3" style="font-size: 3rem;"></i>
                <h6>Kategoriler yüklenemedi</h6>
                <p class="text-muted">Lütfen sayfayı yenilemeyi deneyin.</p>
                <button class="btn btn-primary btn-sm" onclick="location.reload()">
                    <i class="fas fa-refresh me-1"></i>Yenile
                </button>
            </div>
        `;
    }
    
    toggleCategoryDetails(item) {
        // Toggle category item expansion/details
        const isExpanded = item.classList.contains('expanded');
        
        // Close all other expanded items
        document.querySelectorAll('.category-item-modern.expanded').forEach(el => {
            el.classList.remove('expanded');
        });
        
        if (!isExpanded) {
            item.classList.add('expanded');
            // Load additional details if needed
            this.loadCategoryDetails(item.dataset.categoryId, item);
        }
    }
    
    loadCategoryDetails(categoryId, element) {
        // Optionally load more details for the category
        console.log(`Loading details for category ${categoryId}`);
    }
    
    setupWelcomeSection() {
        // Update welcome message with current time
        this.updateWelcomeTime();
        
        // Update time every minute
        setInterval(() => {
            this.updateWelcomeTime();
        }, 60000);
    }
    
    updateWelcomeTime() {
        const timeElement = document.querySelector('.welcome-time');
        if (!timeElement) return;
        
        const now = new Date();
        const timeString = now.toLocaleTimeString('tr-TR', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const dateString = now.toLocaleDateString('tr-TR', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        
        timeElement.textContent = `${dateString}, ${timeString}`;
    }
    
    setupQuickActions() {
        // Setup quick action buttons
        const quickActions = document.querySelectorAll('.quick-action-btn');
        
        quickActions.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = btn.dataset.action;
                this.executeQuickAction(action, btn);
            });
        });
    }
    
    executeQuickAction(action, button) {
        console.log(`Executing quick action: ${action}`);
        
        // Add loading state
        const originalHTML = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> İşleniyor...';
        button.disabled = true;
        
        switch (action) {
            case 'add-product':
                window.location.href = '/dashboard/products/add/';
                break;
            case 'add-category':
                this.openAddCategoryModal();
                break;
            case 'view-messages':
                window.location.href = '/dashboard/messages/';
                break;
            case 'view-analytics':
                window.location.href = '/dashboard/analytics/';
                break;
            default:
                console.log(`Unknown action: ${action}`);
        }
        
        // Restore button state
        setTimeout(() => {
            button.innerHTML = originalHTML;
            button.disabled = false;
        }, 1000);
    }
    
    openAddCategoryModal() {
        // Implementation for add category modal
        console.log('Opening add category modal...');
    }
    
    setupActivityFeed() {
        // Load recent activities
        this.loadRecentActivities();
        
        // Setup activity auto-refresh
        this.setupActivityAutoRefresh();
    }
    
    loadRecentActivities() {
        const activityContainer = document.getElementById('activityFeed');
        if (!activityContainer) return;
        
        fetch('/dashboard/api/activities/recent/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.renderActivities(data.activities);
            }
        })
        .catch(error => {
            console.error('Activities load error:', error);
        });
    }
    
    renderActivities(activities) {
        const container = document.getElementById('activityFeed');
        
        if (activities.length === 0) {
            container.innerHTML = `
                <div class="text-center p-4 text-muted">
                    <i class="fas fa-history mb-2" style="font-size: 2rem; opacity: 0.5;"></i>
                    <p>Henüz aktivite bulunmamaktadır.</p>
                </div>
            `;
            return;
        }
        
        const activityHTML = activities.map(activity => `
            <div class="activity-item">
                <div class="activity-avatar ${activity.type}">
                    <i class="fas fa-${activity.icon}"></i>
                </div>
                <div class="activity-content">
                    <h6 class="activity-title">${activity.title}</h6>
                    <p class="activity-description">${activity.description}</p>
                    <div class="activity-time">${activity.time_ago}</div>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = activityHTML;
    }
    
    setupActivityAutoRefresh() {
        // Refresh activities every 2 minutes
        setInterval(() => {
            this.loadRecentActivities();
        }, 120000);
    }
    
    setupAutoRefresh() {
        // Auto-refresh dashboard stats
        this.refreshInterval = setInterval(() => {
            this.loadDashboardStats();
        }, this.refreshIntervalTime);
    }
    
    loadDashboardStats() {
        console.log('📊 Stats loading temporarily disabled');
        // API çağrısı geçici olarak deaktive edildi
        /*
        fetch('/dashboard/api/stats/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.updateStatsCards(data.stats);
            }
        })
        .catch(error => {
            console.error('Stats load error:', error);
        });
        */
    }
    
    updateStatsCards(stats) {
        // Update stat numbers with animation
        Object.keys(stats).forEach(key => {
            const element = document.getElementById(`stat-${key}`);
            if (element) {
                this.animateNumber(element, parseInt(element.textContent), stats[key]);
            }
        });
    }
    
    animateNumber(element, start, end) {
        const duration = 1000;
        const stepTime = Math.abs(Math.floor(duration / (end - start)));
        const timer = setInterval(() => {
            start += (end > start) ? 1 : -1;
            element.textContent = start;
            if (start === end) {
                clearInterval(timer);
            }
        }, stepTime);
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
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
    
    // Public methods
    refreshDashboard() {
        console.log('🔄 Refreshing dashboard...');
        this.loadDashboardStats();
        this.loadRecentActivities();
        this.showNotification('Dashboard güncellendi.', 'success');
    }
    
    destroy() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    }



    // Class'a YENİ METHOD ekle:
    setupThemeIntegration() {
        // Tema değişikliğini dinle
        document.addEventListener('themeChanged', (e) => {
            console.log('🎨 Dashboard theme updated:', e.detail.newTheme);
            this.updateDashboardTheme(e.detail.newTheme);
        });
    }
    
    updateDashboardTheme(theme) {
        // İstatistik kartlarını güncelle
        const statCards = document.querySelectorAll('.stat-card');
        statCards.forEach(card => {
            card.style.transition = 'all 0.3s ease';
        });
        
        // Aktivite feed'i güncelle
        const activityItems = document.querySelectorAll('.activity-item');
        activityItems.forEach(item => {
            item.style.transition = 'all 0.3s ease';
        });
        
        console.log('✅ Dashboard components updated for theme');
    }
}

// Dashboard utilities
const DashboardUtils = {
    // Format numbers for stat cards
    formatStatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        } else if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    },
    
    // Calculate trend percentage
    calculateTrend(current, previous) {
        if (previous === 0) return 0;
        return Math.round(((current - previous) / previous) * 100);
    },
    
    // Get greeting based on time
    getTimeBasedGreeting() {
        const hour = new Date().getHours();
        if (hour < 12) return 'Günaydın';
        if (hour < 18) return 'İyi günler';
        return 'İyi akşamlar';
    }
};

// Initialize dashboard manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize on dashboard home page
    if (document.querySelector('.dashboard-page, .dashboard-home')) {
        window.dashboardManager = new DashboardManager();
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.dashboardManager) {
        window.dashboardManager.destroy();
    }
});

// Export for global use
window.DashboardManager = DashboardManager;
window.DashboardUtils = DashboardUtils;