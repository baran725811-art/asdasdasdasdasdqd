// core\static\dashboard\js\pages\reviews.js - Yorum yönetimi
/**
 * ==========================================================================
 * REVIEWS PAGE JAVASCRIPT
 * Reviews management page functionality
 * ==========================================================================
 */

class ReviewsManager {
    constructor() {
        this.currentFilters = {};
        this.autoRefreshInterval = null;
        this.refreshTime = 60000; // 1 minute
        this.init();
    }
    
    init() {
        console.log('⭐ Reviews Manager initializing...');
        
        this.setupFilterSystem();
        this.setupModals();
        this.setupBulkActions();
        this.setupAutoRefresh();
        this.updateReviewStats();
        this.setupRatingDisplay();
        
        console.log('✅ Reviews Manager initialized successfully');
    }
    
    setupFilterSystem() {
        console.log('🔍 Setting up review filters...');
        
        const searchInput = document.getElementById('reviewSearch');
        const statusFilter = document.getElementById('statusFilter');
        const ratingFilter = document.getElementById('ratingFilter');
        const dateFilter = document.getElementById('dateFilter');
        
        // Search functionality
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', () => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => this.filterReviews(), 500);
            });
        }
        
        // Status filter
        if (statusFilter) {
            statusFilter.addEventListener('change', () => this.filterReviews());
        }
        
        // Rating filter
        if (ratingFilter) {
            ratingFilter.addEventListener('change', () => this.filterReviews());
        }
        
        // Date filter
        if (dateFilter) {
            dateFilter.addEventListener('change', () => this.filterReviews());
        }
        
        // Quick filter buttons
        this.setupQuickFilters();
    }
    
    setupQuickFilters() {
        // Setup quick filter functions
        window.approveAll = () => this.approveAllPending();
        window.filterPending = () => this.filterPending();
        window.filterByRating = (rating) => this.filterByRating(rating);
    }
    
    filterReviews() {
        const searchInput = document.getElementById('reviewSearch');
        const statusFilter = document.getElementById('statusFilter');
        const ratingFilter = document.getElementById('ratingFilter');
        const dateFilter = document.getElementById('dateFilter');
        const table = document.getElementById('reviewsTable');
        
        if (!table) return;
        
        console.log('🔍 Filtering reviews...');
        
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        const statusValue = statusFilter ? statusFilter.value : '';
        const ratingValue = ratingFilter ? ratingFilter.value : '';
        const dateValue = dateFilter ? dateFilter.value : '';
        
        const rows = table.querySelectorAll('tbody tr');
        let visibleCount = 0;
        
        rows.forEach(row => {
            if (row.querySelector('.empty-state')) return;
            
            let show = true;
            
            // Search filter
            if (searchTerm) {
                const name = row.querySelector('td:nth-child(2)')?.textContent.toLowerCase() || '';
                const comment = row.querySelector('td:nth-child(4)')?.textContent.toLowerCase() || '';
                
                if (!name.includes(searchTerm) && !comment.includes(searchTerm)) {
                    show = false;
                }
            }
            
            // Status filter
            if (statusValue) {
                const status = row.dataset.status;
                if (status !== statusValue) {
                    show = false;
                }
            }
            
            // Rating filter
            if (ratingValue) {
                const rating = row.dataset.rating;
                if (rating !== ratingValue) {
                    show = false;
                }
            }
            
            // Date filter
            if (dateValue) {
                const reviewDate = new Date(row.dataset.date);
                const today = new Date();
                
                switch(dateValue) {
                    case 'today':
                        if (reviewDate.toDateString() !== today.toDateString()) {
                            show = false;
                        }
                        break;
                    case 'week':
                        const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
                        if (reviewDate < weekAgo) {
                            show = false;
                        }
                        break;
                    case 'month':
                        if (reviewDate.getMonth() !== today.getMonth() || 
                            reviewDate.getFullYear() !== today.getFullYear()) {
                            show = false;
                        }
                        break;
                }
            }
            
            row.style.display = show ? '' : 'none';
            if (show) visibleCount++;
        });
        
        this.updateResultsCount(visibleCount);
        this.updateFilterStats();
    }
    
    updateResultsCount(count) {
        const countElement = document.getElementById('resultsCount');
        if (countElement) {
            countElement.textContent = `${count} yorum gösteriliyor`;
        }
    }
    
    updateFilterStats() {
        const table = document.getElementById('reviewsTable');
        if (!table) return;
        
        const visibleRows = table.querySelectorAll('tbody tr[style=""], tbody tr:not([style])');
        
        let pendingCount = 0;
        let approvedCount = 0;
        let rejectedCount = 0;
        let totalRating = 0;
        let ratingCount = 0;
        
        visibleRows.forEach(row => {
            const status = row.dataset.status;
            const rating = parseFloat(row.dataset.rating);
            
            switch(status) {
                case 'pending':
                    pendingCount++;
                    break;
                case 'approved':
                    approvedCount++;
                    break;
                case 'rejected':
                    rejectedCount++;
                    break;
            }
            
            if (!isNaN(rating)) {
                totalRating += rating;
                ratingCount++;
            }
        });
        
        // Update filter summary
        const filterSummary = document.getElementById('filterSummary');
        if (filterSummary) {
            const avgRating = ratingCount > 0 ? (totalRating / ratingCount).toFixed(1) : '0.0';
            filterSummary.innerHTML = `
                <small class="text-muted">
                    Bekleyen: ${pendingCount} | 
                    Onaylı: ${approvedCount} | 
                    Reddedilen: ${rejectedCount} | 
                    Ortalama: ${avgRating}⭐
                </small>
            `;
        }
    }
    
    filterPending() {
        const statusFilter = document.getElementById('statusFilter');
        if (statusFilter) {
            statusFilter.value = 'pending';
            this.filterReviews();
            this.showNotification('Bekleyen yorumlar gösteriliyor.', 'info');
        }
    }
    
    filterByRating(rating) {
        const ratingFilter = document.getElementById('ratingFilter');
        if (ratingFilter) {
            ratingFilter.value = rating.toString();
            this.filterReviews();
            this.showNotification(`${rating} yıldızlı yorumlar gösteriliyor.`, 'info');
        }
    }
    
    approveAllPending() {
        const pendingForms = document.querySelectorAll('tr[data-status="pending"] form[action*="review_toggle"]');
        
        if (pendingForms.length === 0) {
            this.showNotification('Onaylanacak bekleyen yorum bulunamadı.', 'warning');
            return;
        }
        
        if (!confirm(`${pendingForms.length} bekleyen yorumu onaylamak istediğinizden emin misiniz?`)) {
            return;
        }
        
        console.log(`📝 Approving ${pendingForms.length} pending reviews...`);
        
        let completed = 0;
        let errors = 0;
        
        pendingForms.forEach((form, index) => {
            setTimeout(() => {
                const formData = new FormData(form);
                
                fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                })
                .then(response => {
                    if (response.ok) {
                        completed++;
                        // Update row status visually
                        const row = form.closest('tr');
                        if (row) {
                            row.dataset.status = 'approved';
                            const statusBadge = row.querySelector('.badge');
                            if (statusBadge) {
                                statusBadge.className = 'badge bg-success';
                                statusBadge.textContent = 'Onaylandı';
                            }
                        }
                    } else {
                        errors++;
                    }
                })
                .catch(() => {
                    errors++;
                })
                .finally(() => {
                    // Check if all requests completed
                    if (completed + errors === pendingForms.length) {
                        if (errors === 0) {
                            this.showNotification(`${completed} yorum başarıyla onaylandı.`, 'success');
                        } else {
                            this.showNotification(`${completed} yorum onaylandı, ${errors} hatada hata oluştu.`, 'warning');
                        }
                        
                        // Refresh stats
                        setTimeout(() => this.updateReviewStats(), 1000);
                    }
                });
            }, index * 200); // Stagger requests
        });
    }
    
    setupModals() {
        console.log('📱 Setting up review modals...');
        
        // Setup view modal
        this.setupViewModal();
        
        // Setup edit modal
        this.setupEditModal();
        
        // Setup delete confirmation
        this.setupDeleteModal();
    }
    
    setupViewModal() {
        // View review modal functionality is handled by Bootstrap
        document.querySelectorAll('[data-bs-target="#viewReviewModal"]').forEach(button => {
            button.addEventListener('click', () => {
                // Additional setup if needed
                console.log('👁️ Opening review view modal');
            });
        });
    }
    
    setupEditModal() {
        const editModal = document.getElementById('editReviewModal');
        if (!editModal) return;
        
        editModal.addEventListener('shown.bs.modal', () => {
            const firstInput = editModal.querySelector('input, textarea');
            if (firstInput) {
                firstInput.focus();
            }
        });
    }
    
    setupDeleteModal() {
        // Setup delete confirmation with enhanced security
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-bs-target*="delete"]')) {
                const reviewerName = e.target.closest('tr')?.querySelector('.fw-semibold')?.textContent;
                setTimeout(() => {
                    const modal = document.querySelector(e.target.dataset.bsTarget);
                    if (modal && reviewerName) {
                        const deleteForm = modal.querySelector('form');
                        if (deleteForm) {
                            deleteForm.addEventListener('submit', (submitEvent) => {
                                if (!confirm(`"${reviewerName}" kullanıcısının yorumunu kalıcı olarak silmek istediğinizden emin misiniz?`)) {
                                    submitEvent.preventDefault();
                                }
                            });
                        }
                    }
                }, 100);
            }
        });
    }
    
    setupBulkActions() {
        console.log('📦 Setting up bulk actions...');
        
        const selectAllCheckbox = document.getElementById('selectAllReviews');
        const reviewCheckboxes = document.querySelectorAll('.review-checkbox');
        
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', () => {
                reviewCheckboxes.forEach(checkbox => {
                    checkbox.checked = selectAllCheckbox.checked;
                });
                this.updateBulkActionsVisibility();
            });
        }
        
        reviewCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateBulkActionsVisibility();
                
                // Update select all state
                if (selectAllCheckbox) {
                    const checkedCount = document.querySelectorAll('.review-checkbox:checked').length;
                    selectAllCheckbox.checked = checkedCount === reviewCheckboxes.length;
                    selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < reviewCheckboxes.length;
                }
            });
        });
        
        // Bulk action buttons
        this.setupBulkActionButtons();
    }
    
    setupBulkActionButtons() {
        const bulkApproveBtn = document.getElementById('bulkApproveBtn');
        const bulkRejectBtn = document.getElementById('bulkRejectBtn');
        const bulkDeleteBtn = document.getElementById('bulkDeleteBtn');
        
        if (bulkApproveBtn) {
            bulkApproveBtn.addEventListener('click', () => this.executeBulkAction('approve'));
        }
        
        if (bulkRejectBtn) {
            bulkRejectBtn.addEventListener('click', () => this.executeBulkAction('reject'));
        }
        
        if (bulkDeleteBtn) {
            bulkDeleteBtn.addEventListener('click', () => this.executeBulkAction('delete'));
        }
    }
    
    updateBulkActionsVisibility() {
        const selectedCheckboxes = document.querySelectorAll('.review-checkbox:checked');
        const bulkActionsContainer = document.querySelector('.bulk-actions');
        
        if (bulkActionsContainer) {
            if (selectedCheckboxes.length > 0) {
                bulkActionsContainer.style.display = 'block';
            } else {
                bulkActionsContainer.style.display = 'none';
            }
        }
    }
    
    executeBulkAction(action) {
        const selectedCheckboxes = document.querySelectorAll('.review-checkbox:checked');
        const reviewIds = Array.from(selectedCheckboxes).map(cb => cb.value);
        
        if (reviewIds.length === 0) {
            this.showNotification('Lütfen en az bir yorum seçin.', 'warning');
            return;
        }
        
        let confirmMessage = '';
        switch (action) {
            case 'approve':
                confirmMessage = `${reviewIds.length} yorumu onaylamak istediğinizden emin misiniz?`;
                break;
            case 'reject':
                confirmMessage = `${reviewIds.length} yorumu reddetmek istediğinizden emin misiniz?`;
                break;
            case 'delete':
                confirmMessage = `${reviewIds.length} yorumu kalıcı olarak silmek istediğinizden emin misiniz?`;
                break;
        }
        
        if (!confirm(confirmMessage)) return;
        
        const data = new FormData();
        data.append('action', action);
        data.append('review_ids', JSON.stringify(reviewIds));
        data.append('csrfmiddlewaretoken', this.getCSRFToken());
        
        fetch('/dashboard/reviews/bulk-action/', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: data
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification(data.message || 'İşlem tamamlandı.', 'success');
                setTimeout(() => location.reload(), 1000);
            } else {
                this.showNotification(data.message || 'İşlem gerçekleştirilemedi.', 'error');
            }
        })
        .catch(error => {
            console.error('Bulk action error:', error);
            this.showNotification('Bir hata oluştu.', 'error');
        });
    }
    
    setupRatingDisplay() {
        console.log('⭐ Setting up rating displays...');
        
        // Enhanced star rating display
        document.querySelectorAll('.rating-display').forEach(container => {
            const rating = parseFloat(container.dataset.rating);
            if (!isNaN(rating)) {
                this.renderStarRating(container, rating);
            }
        });
    }
    
    renderStarRating(container, rating) {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
        
        let starsHtml = '';
        
        // Full stars
        for (let i = 0; i < fullStars; i++) {
            starsHtml += '<i class="fas fa-star text-warning"></i>';
        }
        
        // Half star
        if (hasHalfStar) {
            starsHtml += '<i class="fas fa-star-half-alt text-warning"></i>';
        }
        
        // Empty stars
        for (let i = 0; i < emptyStars; i++) {
            starsHtml += '<i class="far fa-star text-muted"></i>';
        }
        
        // Find or create stars container
        let starsContainer = container.querySelector('.stars');
        if (!starsContainer) {
            starsContainer = document.createElement('span');
            starsContainer.className = 'stars';
            container.prepend(starsContainer);
        }
        
        starsContainer.innerHTML = starsHtml;
    }
    
    setupAutoRefresh() {
        // Auto-refresh for new reviews
        this.autoRefreshInterval = setInterval(() => {
            this.checkForNewReviews();
        }, this.refreshTime);
        
        console.log(`🔄 Auto-refresh enabled (${this.refreshTime / 1000}s interval)`);
    }
    
    checkForNewReviews() {
        fetch('/dashboard/api/reviews/count/', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.new_reviews > 0) {
                this.showNewReviewsNotification(data.new_reviews);
            }
        })
        .catch(error => {
            console.log('Auto-refresh check failed:', error);
        });
    }
    
    showNewReviewsNotification(count) {
        const notification = document.createElement('div');
        notification.className = 'alert alert-info alert-dismissible position-fixed';
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            <i class="fas fa-bell me-2"></i>
            ${count} yeni yorum var. 
            <button class="btn btn-sm btn-outline-primary ms-2" onclick="location.reload()">
                Yenile
            </button>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 10000);
    }
    
    updateReviewStats() {
        const table = document.getElementById('reviewsTable');
        if (!table) return;
        
        const allRows = table.querySelectorAll('tbody tr');
        let totalReviews = 0;
        let pendingReviews = 0;
        let approvedReviews = 0;
        let rejectedReviews = 0;
        let totalRating = 0;
        let ratingCount = 0;
        
        allRows.forEach(row => {
            if (row.querySelector('.empty-state')) return;
            
            totalReviews++;
            const status = row.dataset.status;
            const rating = parseFloat(row.dataset.rating);
            
            switch(status) {
                case 'pending':
                    pendingReviews++;
                    break;
                case 'approved':
                    approvedReviews++;
                    break;
                case 'rejected':
                    rejectedReviews++;
                    break;
            }
            
            if (!isNaN(rating)) {
                totalRating += rating;
                ratingCount++;
            }
        });
        
        // Update stat elements
        const totalElement = document.getElementById('totalReviewsCount');
        const pendingElement = document.getElementById('pendingReviewsCount');
        const approvedElement = document.getElementById('approvedReviewsCount');
        const avgRatingElement = document.getElementById('avgRatingValue');
        
        if (totalElement) totalElement.textContent = totalReviews;
        if (pendingElement) pendingElement.textContent = pendingReviews;
        if (approvedElement) approvedElement.textContent = approvedReviews;
        if (avgRatingElement && ratingCount > 0) {
            avgRatingElement.textContent = (totalRating / ratingCount).toFixed(1);
        }
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
    refreshReviews() {
        console.log('🔄 Refreshing reviews...');
        location.reload();
    }
    
    exportReviews() {
        console.log('📊 Exporting reviews...');
        
        const visibleRows = Array.from(document.querySelectorAll('#reviewsTable tbody tr')).filter(row => 
            row.style.display !== 'none' && !row.querySelector('.empty-state')
        );
        
        const data = visibleRows.map(row => ({
            reviewer: row.querySelector('td:nth-child(2)')?.textContent || '',
            rating: row.dataset.rating || '',
            comment: row.querySelector('td:nth-child(4)')?.textContent || '',
            status: row.dataset.status || '',
            date: row.dataset.date || ''
        }));
        
        const csv = 'Yorumcu,Puan,Yorum,Durum,Tarih\n' + 
                   data.map(row => `"${row.reviewer}","${row.rating}","${row.comment}","${row.status}","${row.date}"`).join('\n');
        
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'yorumlar-' + new Date().toISOString().split('T')[0] + '.csv';
        link.click();
        
        this.showNotification('Yorumlar başarıyla indirildi.', 'success');
    }
    
    destroy() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
    }
}

// Review utilities
const ReviewUtils = {
    // Format review date
    formatReviewDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('tr-TR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    // Calculate time ago
    timeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) return 'Az önce';
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} dakika önce`;
        if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} saat önce`;
        if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} gün önce`;
        
        return date.toLocaleDateString('tr-TR');
    },
    
    // Truncate long comments
    truncateComment(comment, maxLength = 100) {
        if (comment.length <= maxLength) return comment;
        return comment.substring(0, maxLength) + '...';
    },
    
    // Validate rating
    isValidRating(rating) {
        const num = parseFloat(rating);
        return !isNaN(num) && num >= 1 && num <= 5;
    }
};

// Initialize reviews manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize on reviews pages
    if (document.querySelector('.reviews-page, .reviews-management')) {
        window.reviewsManager = new ReviewsManager();
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.reviewsManager) {
        window.reviewsManager.destroy();
    }
});

// Export for global use
window.ReviewsManager = ReviewsManager;
window.ReviewUtils = ReviewUtils;