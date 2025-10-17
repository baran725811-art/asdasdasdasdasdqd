// core\static\dashboard\js\pages\carousel.js - Carousel yönetimi
/**
 * ==========================================================================
 * CAROUSEL PAGE JAVASCRIPT
 * Carousel/Slider management page functionality
 * ==========================================================================
 */

class CarouselManager {
    constructor() {
        this.init();
    }
    
    init() {
        console.log('🎠 Carousel Manager initializing...');
        
        this.setupPreviewToggle();
        this.setupAltTextCounters();
        this.setupImagePreviews();
        this.setupFormValidation();
        this.setupSlideActions();
        this.updateStatistics();
        
        console.log('✅ Carousel Manager initialized successfully');
    }
    
    setupPreviewToggle() {
        const previewToggle = document.getElementById('previewToggle');
        const previewContainer = document.getElementById('carouselPreviewContainer');
        
        if (previewToggle && previewContainer) {
            let isHidden = false;
            
            previewToggle.addEventListener('click', function() {
                if (isHidden) {
                    previewContainer.style.display = 'block';
                    this.innerHTML = '<i class="fas fa-eye-slash me-1"></i>Önizlemeyi Gizle';
                    isHidden = false;
                } else {
                    previewContainer.style.display = 'none';
                    this.innerHTML = '<i class="fas fa-eye me-1"></i>Önizlemeyi Göster';
                    isHidden = true;
                }
            });
        }
    }
    
    setupAltTextCounters() {
        // Setup character counter for alt text fields
        this.setupCharCounter('input[name="alt_text"]', '#alt_text_counter');
        
        // Setup counters for translation fields
        document.querySelectorAll('.alt-text-input').forEach(input => {
            const lang = input.getAttribute('data-lang');
            const counter = document.querySelector(`.alt-counter[data-lang="${lang}"]`);
            
            if (counter) {
                this.initializeCounter(input, counter, 125);
            }
        });
        
        // Setup counters for edit modals
        document.querySelectorAll('[id^="editSlideModal"]').forEach(modal => {
            const altInput = modal.querySelector('input[name="alt_text"]');
            const counter = modal.querySelector('.alt_text_counter_edit');
            
            if (altInput && counter) {
                this.initializeCounter(altInput, counter, 125);
            }
        });
    }
    
    setupCharCounter(inputSelector, counterSelector) {
        const input = document.querySelector(inputSelector);
        const counter = document.querySelector(counterSelector);
        
        if (input && counter) {
            this.initializeCounter(input, counter, 125);
        }
    }
    
    initializeCounter(input, counter, maxLength) {
        // Set initial value
        this.updateCounter(input, counter, maxLength);
        
        // Add event listener
        input.addEventListener('input', () => {
            this.updateCounter(input, counter, maxLength);
        });
    }
    
    updateCounter(input, counter, maxLength) {
        const length = input.value.length;
        counter.textContent = `${length}/${maxLength}`;
        
        // Update color based on length
        counter.classList.remove('text-warning', 'text-danger');
        
        if (length >= maxLength * 0.9) {
            counter.classList.add('text-danger');
        } else if (length >= maxLength * 0.8) {
            counter.classList.add('text-warning');
        }
    }
    
    setupImagePreviews() {
        // Setup image previews for file uploads
        const imageInputs = document.querySelectorAll('input[type="file"][name="image"]');
        
        imageInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                this.handleImagePreview(e.target);
            });
        });
    }
    
    handleImagePreview(input) {
        const file = input.files[0];
        if (!file) return;
        
        // Validate file type
        if (!file.type.startsWith('image/')) {
            this.showNotification('Lütfen geçerli bir resim dosyası seçin.', 'error');
            input.value = '';
            return;
        }
        
        // Validate file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            this.showNotification('Resim dosyası 5MB\'dan büyük olamaz.', 'error');
            input.value = '';
            return;
        }
        
        const reader = new FileReader();
        reader.onload = (e) => {
            let preview = input.parentNode.querySelector('.image-preview');
            if (!preview) {
                preview = document.createElement('div');
                preview.className = 'image-preview mt-2';
                input.parentNode.appendChild(preview);
            }
            
            preview.innerHTML = `
                <img src="${e.target.result}" class="image-modern" style="max-width: 200px; max-height: 120px; border-radius: 8px;">
                <p class="small text-muted mt-1">${file.name}</p>
                <small class="text-success">✓ Resim seçildi</small>
            `;
        };
        reader.readAsDataURL(file);
    }
    
    setupFormValidation() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                    this.showNotification('Lütfen tüm gerekli alanları doldurun.', 'error');
                }
            });
        });
    }
    
    validateForm(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
                field.classList.add('is-valid');
            }
        });
        
        return isValid;
    }
    
    setupSlideActions() {
        // Setup slide ordering
        this.setupSlideOrdering();
        
        // Setup bulk actions
        this.setupBulkActions();
        
        // Setup slide status toggles
        this.setupStatusToggles();
    }
    
    setupSlideOrdering() {
        const orderButtons = document.querySelectorAll('.btn-order');
        
        orderButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const action = button.dataset.action;
                const slideId = button.dataset.slideId;
                
                this.reorderSlide(slideId, action);
            });
        });
    }
    
    reorderSlide(slideId, action) {
        const data = new FormData();
        data.append('slide_id', slideId);
        data.append('action', action);
        data.append('csrfmiddlewaretoken', this.getCSRFToken());
        
        fetch('/dashboard/carousel/reorder/', {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: data
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showNotification('Sıralama güncellendi.', 'success');
                setTimeout(() => location.reload(), 1000);
            } else {
                this.showNotification('Sıralama güncellenirken hata oluştu.', 'error');
            }
        })
        .catch(error => {
            console.error('Reorder error:', error);
            this.showNotification('Bir hata oluştu.', 'error');
        });
    }
    
    setupBulkActions() {
        const selectAllCheckbox = document.getElementById('selectAllSlides');
        const slideCheckboxes = document.querySelectorAll('.slide-checkbox');
        const bulkActionsContainer = document.querySelector('.bulk-actions');
        
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', () => {
                slideCheckboxes.forEach(checkbox => {
                    checkbox.checked = selectAllCheckbox.checked;
                });
                this.updateBulkActionsVisibility();
            });
        }
        
        slideCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateBulkActionsVisibility();
            });
        });
        
        // Bulk action buttons
        const bulkDeleteBtn = document.getElementById('bulkDeleteBtn');
        const bulkActivateBtn = document.getElementById('bulkActivateBtn');
        const bulkDeactivateBtn = document.getElementById('bulkDeactivateBtn');
        
        if (bulkDeleteBtn) {
            bulkDeleteBtn.addEventListener('click', () => this.executeBulkAction('delete'));
        }
        
        if (bulkActivateBtn) {
            bulkActivateBtn.addEventListener('click', () => this.executeBulkAction('activate'));
        }
        
        if (bulkDeactivateBtn) {
            bulkDeactivateBtn.addEventListener('click', () => this.executeBulkAction('deactivate'));
        }
    }
    
    updateBulkActionsVisibility() {
        const selectedCheckboxes = document.querySelectorAll('.slide-checkbox:checked');
        const bulkActionsContainer = document.querySelector('.bulk-actions');
        
        if (bulkActionsContainer) {
            if (selectedCheckboxes.length > 0) {
                bulkActionsContainer.classList.add('show');
            } else {
                bulkActionsContainer.classList.remove('show');
            }
        }
    }
    
    executeBulkAction(action) {
        const selectedCheckboxes = document.querySelectorAll('.slide-checkbox:checked');
        const slideIds = Array.from(selectedCheckboxes).map(cb => cb.value);
        
        if (slideIds.length === 0) {
            this.showNotification('Lütfen en az bir slayt seçin.', 'warning');
            return;
        }
        
        let confirmMessage = '';
        switch (action) {
            case 'delete':
                confirmMessage = `${slideIds.length} slaytı silmek istediğinizden emin misiniz?`;
                break;
            case 'activate':
                confirmMessage = `${slideIds.length} slaytı aktif yapmak istediğinizden emin misiniz?`;
                break;
            case 'deactivate':
                confirmMessage = `${slideIds.length} slaytı pasif yapmak istediğinizden emin misiniz?`;
                break;
        }
        
        if (!confirm(confirmMessage)) return;
        
        const data = new FormData();
        data.append('action', action);
        data.append('slide_ids', JSON.stringify(slideIds));
        data.append('csrfmiddlewaretoken', this.getCSRFToken());
        
        fetch('/dashboard/carousel/bulk-action/', {
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
    
    setupStatusToggles() {
        const statusButtons = document.querySelectorAll('.btn-toggle-status');
        
        statusButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const slideId = button.dataset.slideId;
                const currentStatus = button.dataset.status;
                
                this.toggleSlideStatus(slideId, currentStatus, button);
            });
        });
    }
    
    toggleSlideStatus(slideId, currentStatus, button) {
        const data = new FormData();
        data.append('slide_id', slideId);
        data.append('csrfmiddlewaretoken', this.getCSRFToken());
        
        fetch(`/dashboard/carousel/${slideId}/toggle-status/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: data
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update button
                const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
                button.dataset.status = newStatus;
                
                if (newStatus === 'active') {
                    button.innerHTML = '<i class="fas fa-eye-slash"></i>';
                    button.classList.remove('btn-outline-success');
                    button.classList.add('btn-outline-danger');
                    button.title = 'Pasif Yap';
                } else {
                    button.innerHTML = '<i class="fas fa-eye"></i>';
                    button.classList.remove('btn-outline-danger');
                    button.classList.add('btn-outline-success');
                    button.title = 'Aktif Yap';
                }
                
                this.showNotification('Durum güncellendi.', 'success');
                this.updateStatistics();
            } else {
                this.showNotification('Durum güncellenirken hata oluştu.', 'error');
            }
        })
        .catch(error => {
            console.error('Status toggle error:', error);
            this.showNotification('Bir hata oluştu.', 'error');
        });
    }
    
    updateStatistics() {
        // Update active slides count
        let activeCount = 0;
        document.querySelectorAll('tbody tr').forEach(row => {
            const statusBadge = row.querySelector('.badge-modern.success');
            if (statusBadge) activeCount++;
        });
        
        const activeCountElement = document.getElementById('activeSlidesCount');
        if (activeCountElement) {
            activeCountElement.textContent = activeCount;
        }
        
        // Update total slides count
        const totalCount = document.querySelectorAll('tbody tr').length;
        const totalCountElement = document.getElementById('totalSlidesCount');
        if (totalCountElement) {
            totalCountElement.textContent = totalCount;
        }
        
        // Update inactive slides count
        const inactiveCountElement = document.getElementById('inactiveSlidesCount');
        if (inactiveCountElement) {
            inactiveCountElement.textContent = totalCount - activeCount;
        }
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
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
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }
}

// Additional utility functions for carousel management
const CarouselUtils = {
    // Generate slug from title
    generateSlug(title) {
        return title
            .toLowerCase()
            .replace(/ğ/g, 'g')
            .replace(/ü/g, 'u')
            .replace(/ş/g, 's')
            .replace(/ı/g, 'i')
            .replace(/ö/g, 'o')
            .replace(/ç/g, 'c')
            .replace(/[^\w\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/-+/g, '-')
            .trim('-');
    },
    
    // Auto-generate alt text from title
    generateAltText(title, description = '') {
        let altText = title;
        if (description && description.length > 0) {
            altText += ' - ' + description.substring(0, 50);
        }
        return altText.substring(0, 125);
    },
    
    // Validate image dimensions
    validateImageDimensions(file, minWidth = 800, minHeight = 400) {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => {
                resolve({
                    valid: img.width >= minWidth && img.height >= minHeight,
                    width: img.width,
                    height: img.height,
                    message: `Resim boyutu en az ${minWidth}x${minHeight} piksel olmalıdır. Mevcut boyut: ${img.width}x${img.height}`
                });
            };
            img.src = URL.createObjectURL(file);
        });
    },
    
    // Preview carousel slide
    previewSlide(imageUrl, title, description) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Slayt Önizleme</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body p-0">
                        <div class="carousel-slide-preview">
                            <img src="${imageUrl}" alt="${title}" style="width: 100%; height: 300px; object-fit: cover;">
                            <div class="carousel-caption">
                                <h5>${title}</h5>
                                <p>${description}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
        
        // Clean up after modal is hidden
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    }
};

// Initialize carousel manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize on carousel pages
    if (document.querySelector('.carousel-management, .carousel-page')) {
        window.carouselManager = new CarouselManager();
    }
});

// Export for global use
window.CarouselManager = CarouselManager;
window.CarouselUtils = CarouselUtils;