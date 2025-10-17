// News Management JavaScript
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize news management functionality
    initViewToggle();
    initSearch();
    initFormHandlers();
    initDeleteHandlers();
    
    // View toggle functionality
    function initViewToggle() {
        const viewToggles = document.querySelectorAll('.btn-toggle');
        const gridView = document.getElementById('gridView');
        const listView = document.getElementById('listView');
        
        viewToggles.forEach(toggle => {
            toggle.addEventListener('click', function() {
                const view = this.getAttribute('data-view');
                
                // Update toggle states
                viewToggles.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                // Switch views with animation
                if (view === 'grid') {
                    listView.style.display = 'none';
                    gridView.style.display = 'block';
                    animateGridCards();
                } else {
                    gridView.style.display = 'none';
                    listView.style.display = 'block';
                }
                
                // Store preference
                localStorage.setItem('newsViewPreference', view);
            });
        });
        
        // Load saved preference
        const savedView = localStorage.getItem('newsViewPreference') || 'grid';
        const savedToggle = document.querySelector(`.btn-toggle[data-view="${savedView}"]`);
        if (savedToggle) {
            savedToggle.click();
        }
    }
    
    // Animate grid cards on view change
    function animateGridCards() {
        const cards = document.querySelectorAll('.news-card');
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.3s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }
    
    // Search functionality
    function initSearch() {
        const searchInput = document.getElementById('newsSearch');
        if (!searchInput) return;
        
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const searchTerm = this.value.toLowerCase().trim();
            
            searchTimeout = setTimeout(() => {
                filterNews(searchTerm);
            }, 300);
        });
        
        // Clear search
        const clearButton = searchInput.parentElement.querySelector('.btn-clear-search');
        if (clearButton) {
            clearButton.addEventListener('click', function() {
                searchInput.value = '';
                filterNews('');
            });
        }
    }
    
    // Filter news items
    function filterNews(searchTerm) {
        const newsCards = document.querySelectorAll('.news-card-wrapper');
        const listItems = document.querySelectorAll('.media-mention-card');
        let visibleCount = 0;
        
        // Filter grid view
        newsCards.forEach(card => {
            const title = card.getAttribute('data-title') || '';
            const source = card.getAttribute('data-source') || '';
            const shouldShow = !searchTerm || title.includes(searchTerm) || source.includes(searchTerm);
            
            if (shouldShow) {
                card.style.display = 'block';
                card.style.animation = 'fadeInUp 0.3s ease forwards';
                card.classList.toggle('search-match', searchTerm && (title.includes(searchTerm) || source.includes(searchTerm)));
                visibleCount++;
            } else {
                card.style.display = 'none';
                card.classList.remove('search-match');
            }
        });
        
        // Filter list view
        listItems.forEach(item => {
            const title = item.querySelector('.mention-title')?.textContent.toLowerCase() || '';
            const source = item.querySelector('.mention-source')?.textContent.toLowerCase() || '';
            const shouldShow = !searchTerm || title.includes(searchTerm) || source.includes(searchTerm);
            
            item.style.display = shouldShow ? 'block' : 'none';
            if (shouldShow && searchTerm) visibleCount++;
        });
        
        // Show/hide empty state
        toggleEmptyState(visibleCount === 0 && searchTerm !== '');
        
        // Update results count
        updateResultsCount(visibleCount);
    }
    
    // Toggle empty state
    function toggleEmptyState(show) {
        let emptyState = document.querySelector('.search-empty-state');
        
        if (show && !emptyState) {
            emptyState = createEmptyState();
            document.getElementById('gridView').appendChild(emptyState);
        } else if (!show && emptyState) {
            emptyState.remove();
        }
    }
    
    // Create empty state element
    function createEmptyState() {
        const emptyState = document.createElement('div');
        emptyState.className = 'search-empty-state text-center py-5';
        emptyState.innerHTML = `
            <div class="mb-3">
                <i class="fas fa-search fa-3x text-muted"></i>
            </div>
            <h5 class="text-muted">Arama sonucu bulunamadı</h5>
            <p class="text-muted">Arama kriterlerinizi değiştirmeyi deneyin.</p>
        `;
        return emptyState;
    }
    
    // Update results count
    function updateResultsCount(count) {
        const resultsCount = document.getElementById('resultsCount');
        if (resultsCount) {
            resultsCount.textContent = `${count} haber gösteriliyor`;
        }
    }
    
    // Form handlers
    function initFormHandlers() {
        // Add news form
        const addNewsForm = document.getElementById('mediaMentionForm');
        if (addNewsForm) {
            addNewsForm.addEventListener('submit', handleFormSubmit);
        }
        
        // Edit news forms
        document.querySelectorAll('form[id^="editNewsForm"]').forEach(form => {
            form.addEventListener('submit', handleFormSubmit);
        });
    }
    
    // Handle form submission
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        const isEdit = form.id.includes('editNewsForm');
        
        // Show loading state
        setButtonLoading(submitBtn, isEdit ? 'Güncelleniyor...' : 'Kaydediliyor...');
        
        try {
            const formData = new FormData(form);
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCsrfToken()
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                showNotification(
                    isEdit ? 'Haber başarıyla güncellendi!' : 'Haber başarıyla kaydedildi!', 
                    'success'
                );
                
                // Close modal and refresh
                setTimeout(() => {
                    const modal = form.closest('.modal');
                    if (modal) {
                        const modalInstance = bootstrap.Modal.getInstance(modal);
                        if (modalInstance) modalInstance.hide();
                    }
                    window.location.reload();
                }, 1000);
                
            } else {
                throw new Error('Form submission failed');
            }
            
        } catch (error) {
            console.error('Form submission error:', error);
            showNotification('Bir hata oluştu. Lütfen tekrar deneyin.', 'error');
        } finally {
            resetButton(submitBtn, originalText);
        }
    }
    
    // Delete handlers
    function initDeleteHandlers() {
        document.querySelectorAll('.delete-form').forEach(form => {
            form.addEventListener('submit', handleDeleteSubmit);
        });
    }
    
    // Handle delete submission
    async function handleDeleteSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const submitBtn = form.querySelector('.delete-confirm-btn');
        const originalText = submitBtn.innerHTML;
        const itemName = form.dataset.itemName || 'Bu öğe';
        
        setButtonLoading(submitBtn, 'Siliniyor...');
        
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCsrfToken()
                }
            });
            
            if (response.ok) {
                showNotification(`${itemName} başarıyla silindi!`, 'success');
                
                // Close modal
                const modal = form.closest('.modal');
                if (modal) {
                    const modalInstance = bootstrap.Modal.getInstance(modal);
                    if (modalInstance) modalInstance.hide();
                }
                
                // Remove card with animation
                const newsId = form.action.split('/').slice(-2, -1)[0];
                const cardWrapper = document.querySelector(`[data-news-id="${newsId}"]`)?.closest('.news-card-wrapper');
                
                if (cardWrapper) {
                    cardWrapper.style.transition = 'all 0.3s ease';
                    cardWrapper.style.transform = 'scale(0.8)';
                    cardWrapper.style.opacity = '0';
                    
                    setTimeout(() => {
                        cardWrapper.remove();
                    }, 300);
                } else {
                    setTimeout(() => window.location.reload(), 1000);
                }
                
            } else {
                throw new Error('Delete operation failed');
            }
            
        } catch (error) {
            console.error('Delete error:', error);
            showNotification('Silme işlemi başarısız. Lütfen tekrar deneyin.', 'error');
        } finally {
            resetButton(submitBtn, originalText);
        }
    }
    
    // Utility functions
    function setButtonLoading(button, text) {
        button.disabled = true;
        button.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>${text}`;
    }
    
    function resetButton(button, originalText) {
        button.disabled = false;
        button.innerHTML = originalText;
    }
    
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
    
    function showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    // Initialize card hover effects
    function initCardEffects() {
        const cards = document.querySelectorAll('.news-card');
        
        cards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-8px)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
            });
        });
    }
    
    // Initialize on page load
    initCardEffects();
    animateGridCards();
});

// Global functions for template usage
function viewNews(id) {
    // Haber detayı görüntüleme fonksiyonu - modal veya sayfa olarak
    alert('Haber detayı: ' + id); // Geçici, view sayfası yoksa
    // window.location.href = `/dashboard/media-mentions/${id}/view/`;
}

function editNews(id) {
    // Haber düzenleme fonksiyonu
    window.location.href = `/dashboard/media-mentions/edit/${id}/`;
}

function deleteMention(id, title) {
    const modal = document.getElementById('deleteModal');
    const itemName = modal.querySelector('#deleteItemName');
    const deleteForm = modal.querySelector('#deleteForm');
    
    if (itemName) itemName.textContent = title;
    if (deleteForm) deleteForm.action = `/dashboard/media-mentions/${id}/delete/`;
    
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

function clearFilters() {
    const searchInput = document.getElementById('newsSearch');
    if (searchInput) {
        searchInput.value = '';
        searchInput.dispatchEvent(new Event('input'));
    }
}

function exportData() {
    // Export functionality
    window.location.href = '/dashboard/media-mentions/export/';
}

// CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .news-card-wrapper {
        animation: fadeInUp 0.3s ease forwards;
    }
`;
document.head.appendChild(style);