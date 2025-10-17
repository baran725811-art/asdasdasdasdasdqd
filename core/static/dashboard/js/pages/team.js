// Team Management JavaScript
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize team management functionality
    initViewToggle();
    initSearch();
    initFormHandlers();
    initDeleteHandlers();
    
    // View toggle functionality
    function initViewToggle() {
        const viewToggles = document.querySelectorAll('.btn-toggle');
        const gridView = document.getElementById('gridView');
        const tableView = document.getElementById('tableView');
        
        viewToggles.forEach(toggle => {
            toggle.addEventListener('click', function() {
                const view = this.getAttribute('data-view');
                
                // Update toggle states
                viewToggles.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                // Switch views with animation
                if (view === 'grid') {
                    tableView.style.display = 'none';
                    gridView.style.display = 'block';
                    animateGridCards();
                } else {
                    gridView.style.display = 'none';
                    tableView.style.display = 'block';
                }
                
                // Store preference
                localStorage.setItem('teamViewPreference', view);
            });
        });
        
        // Load saved preference
        const savedView = localStorage.getItem('teamViewPreference') || 'grid';
        const savedToggle = document.querySelector(`.btn-toggle[data-view="${savedView}"]`);
        if (savedToggle) {
            savedToggle.click();
        }
    }
    
    // Animate grid cards on view change
    function animateGridCards() {
        const cards = document.querySelectorAll('.team-card');
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
        const searchInput = document.getElementById('memberSearch');
        if (!searchInput) return;
        
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const searchTerm = this.value.toLowerCase().trim();
            
            searchTimeout = setTimeout(() => {
                filterTeamMembers(searchTerm);
            }, 300);
        });
        
        // Clear search
        const clearButton = searchInput.parentElement.querySelector('.btn-clear-search');
        if (clearButton) {
            clearButton.addEventListener('click', function() {
                searchInput.value = '';
                filterTeamMembers('');
            });
        }
    }
    
    // Filter team members
    function filterTeamMembers(searchTerm) {
        const teamCards = document.querySelectorAll('.team-card-wrapper');
        const tableRows = document.querySelectorAll('#teamTable tbody tr');
        let visibleCount = 0;
        
        // Filter grid view
        teamCards.forEach(card => {
            const name = card.getAttribute('data-name') || '';
            const position = card.getAttribute('data-position') || '';
            const shouldShow = !searchTerm || name.includes(searchTerm) || position.includes(searchTerm);
            
            if (shouldShow) {
                card.style.display = 'block';
                card.style.animation = 'fadeInUp 0.3s ease forwards';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });
        
        // Filter table view
        tableRows.forEach(row => {
            const text = row.textContent.toLowerCase();
            const shouldShow = !searchTerm || text.includes(searchTerm);
            row.style.display = shouldShow ? '' : 'none';
            if (shouldShow && row.getAttribute('data-member-id')) visibleCount++;
        });
        
        // Show/hide empty state
        toggleEmptyState(visibleCount === 0 && searchTerm !== '');
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
    
    // Form handlers
    function initFormHandlers() {
        // Add member form
        const addMemberForm = document.getElementById('addMemberForm');
        if (addMemberForm) {
            addMemberForm.addEventListener('submit', handleFormSubmit);
        }
        
        // Edit member forms
        document.querySelectorAll('form[id^="editMemberForm"]').forEach(form => {
            form.addEventListener('submit', handleFormSubmit);
        });
    }
    
    // Handle form submission
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        const isEdit = form.id.includes('editMemberForm');
        
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
                    isEdit ? 'Başarıyla güncellendi!' : 'Başarıyla kaydedildi!', 
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
                const memberId = form.action.split('/').slice(-2, -1)[0];
                const cardWrapper = document.querySelector(`[data-member-id="${memberId}"]`)?.closest('.team-card-wrapper');
                
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
        const cards = document.querySelectorAll('.team-card');
        
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
    
    .team-card-wrapper {
        animation: fadeInUp 0.3s ease forwards;
    }
`;
document.head.appendChild(style);