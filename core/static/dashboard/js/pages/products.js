// core\static\dashboard\js\pages\products.js - Ürün yönetimi
/**
 * ==========================================================================
 * PRODUCTS PAGE JAVASCRIPT
 * Product management page functionality
 * ==========================================================================
 */

class ProductsManager {
    constructor() {
        this.currentFilters = {};
        this.editModal = null;
        this.addModal = null;
        this.init();
    }
    
    init() {
        console.log('📦 Products Manager initializing...');
        
        this.setupFilterForm();
        this.setupModals();
        this.setupImagePreviews();
        this.setupTranslationTabs();
        this.setupFormValidation();
        this.setupBulkActions();
        this.updateProductStats();
        
        // Setup global functions for inline usage
        window.editProduct = (productId) => this.editProduct(productId);
        
        console.log('✅ Products Manager initialized successfully');
    }
    
    setupFilterForm() {
        const filterForm = document.getElementById('filterForm');
        const filterInputs = filterForm?.querySelectorAll('select, input');
        
        if (!filterForm) return;
        
        console.log('🔍 Setting up product filters...');
        
        filterInputs.forEach(input => {
            if (input.type !== 'submit') {
                input.addEventListener('change', () => {
                    if (input.name === 'search') {
                        clearTimeout(this.searchTimeout);
                        this.searchTimeout = setTimeout(() => this.applyFilters(), 500);
                    } else {
                        setTimeout(() => this.applyFilters(), 300);
                    }
                });
            }
        });
        
        // Reset filters function
        window.resetFilters = () => this.resetFilters();
    }
    
    applyFilters() {
        const filterForm = document.getElementById('filterForm');
        if (!filterForm) return;
        
        console.log('🔍 Applying product filters...');
        
        // Get filter values
        const formData = new FormData(filterForm);
        const filters = {};
        
        for (let [key, value] of formData.entries()) {
            if (value.trim()) {
                filters[key] = value;
            }
        }
        
        this.currentFilters = filters;
        
        // Submit form to apply server-side filtering
        setTimeout(() => filterForm.submit(), 300);
    }
    
    resetFilters() {
        const filterForm = document.getElementById('filterForm');
        if (!filterForm) return;
        
        console.log('🧹 Resetting product filters...');
        
        filterForm.querySelectorAll('select, input[type="text"]').forEach(input => {
            if (input.type === 'select-one') {
                input.selectedIndex = 0;
            } else {
                input.value = '';
            }
        });
        
        this.currentFilters = {};
        filterForm.submit();
    }

    setupDeleteModals() {
    // Delete modal'lar için özel handler
        document.addEventListener('click', (e) => {
            const deleteBtn = e.target.closest('[data-bs-toggle="modal"][data-bs-target*="delete"]');
            if (deleteBtn) {
                e.preventDefault();
                const modalSelector = deleteBtn.getAttribute('data-bs-target');
                const modalEl = document.querySelector(modalSelector);
                
                if (modalEl) {
                    // Manuel modal göster (backdrop hatası olmaz)
                    modalEl.style.display = 'block';
                    modalEl.classList.add('show');
                    modalEl.setAttribute('aria-hidden', 'false');
                    document.body.classList.add('modal-open');
                    
                    // Backdrop ekle
                    const backdrop = document.createElement('div');
                    backdrop.className = 'modal-backdrop fade show';
                    document.body.appendChild(backdrop);
                    
                    // Modal kapat butonları
                    modalEl.addEventListener('click', function(e) {
                        if (e.target.classList.contains('btn-secondary') || 
                            e.target.closest('.btn-close') || 
                            e.target.classList.contains('modal-backdrop')) {
                            
                            modalEl.style.display = 'none';
                            modalEl.classList.remove('show');
                            modalEl.setAttribute('aria-hidden', 'true');
                            document.body.classList.remove('modal-open');
                            backdrop.remove();
                        }
                    });
                }
            }
        });
    }
    
    setupModals() {
        console.log('Setting up product modals...');
        
        // Modal'ları manuel olarak yönet - Bootstrap'a bağımlı olmadan
        this.setupManualModals();
    }
    
    setupManualModals() {
        // Tüm modal butonlarına click handler ekle
        document.addEventListener('click', (e) => {
            const button = e.target.closest('[data-bs-toggle="modal"]');
            if (!button) return;
            
            const targetSelector = button.getAttribute('data-bs-target');
            if (!targetSelector) return;
            
            e.preventDefault();
            e.stopPropagation();
            
            const modalElement = document.querySelector(targetSelector);
            if (!modalElement) return;
            
            // Manuel modal açma
            this.showModalManually(modalElement);
            
            // Modal kapatma event'lerini ekle
            this.setupModalCloseHandlers(modalElement);
        });
    }
    
    showModalManually(modalElement) {
        // Modal'ı göster
        modalElement.style.display = 'block';
        modalElement.classList.add('show');
        modalElement.setAttribute('aria-hidden', 'false');
        modalElement.setAttribute('aria-modal', 'true');
        modalElement.setAttribute('role', 'dialog');
        
        // Body'yi modal-open yap
        document.body.classList.add('modal-open');
        document.body.style.overflow = 'hidden';
        
        // Backdrop ekle
        const backdrop = document.createElement('div');
        backdrop.className = 'modal-backdrop fade show';
        backdrop.setAttribute('data-modal-id', modalElement.id);
        document.body.appendChild(backdrop);
        
        // ESC tuşu ile kapatma
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                this.hideModalManually(modalElement);
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);
    }
    
    hideModalManually(modalElement) {
        // Modal'ı gizle
        modalElement.style.display = 'none';
        modalElement.classList.remove('show');
        modalElement.setAttribute('aria-hidden', 'true');
        modalElement.removeAttribute('aria-modal');
        modalElement.removeAttribute('role');
        
        // Body'yi normale döndür
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
        
        // Backdrop'u kaldır
        const backdrop = document.querySelector(`[data-modal-id="${modalElement.id}"]`);
        if (backdrop) {
            backdrop.remove();
        }
    }
    
    setupModalCloseHandlers(modalElement) {
        // Close butonları
        const closeButtons = modalElement.querySelectorAll('[data-bs-dismiss="modal"], .btn-close');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.hideModalManually(modalElement);
            });
        });
        
        // Backdrop click
        const backdrop = document.querySelector(`[data-modal-id="${modalElement.id}"]`);
        if (backdrop) {
            backdrop.addEventListener('click', () => {
                this.hideModalManually(modalElement);
            });
        }
    }
    
    setupAddModal() {
        const addModal = document.getElementById('addProductModal');
        if (!addModal) return;
        
        console.log('➕ Setting up add product modal...');
        
        this.addModal = addModal;
        
        // Setup modal events
        addModal.addEventListener('shown.bs.modal', () => {
            const firstInput = addModal.querySelector('input:not([type="hidden"])');
            if (firstInput) {
                firstInput.focus();
            }
        });
        
        // Setup form submission
        const addForm = addModal.querySelector('form');
        if (addForm) {
            addForm.addEventListener('submit', (e) => this.handleAddFormSubmit(e));
        }
    }
    
    setupEditModal() {
        const editModal = document.getElementById('editProductModal');
        if (!editModal) return;
        
        console.log('✏️ Setting up edit product modal...');
        
        this.editModal = editModal;
        
        editModal.addEventListener('shown.bs.modal', () => {
            const firstInput = editModal.querySelector('input:not([type="hidden"])');
            if (firstInput) {
                firstInput.focus();
            }
        });
    }
    
    /*setupDeleteModal() {
        // Setup delete confirmation modals
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-bs-target*="delete"]')) {
                const productName = e.target.closest('tr')?.querySelector('.fw-semibold')?.textContent;
                setTimeout(() => {
                    const modal = document.querySelector(e.target.dataset.bsTarget);
                    if (modal && productName) {
                        const deleteForm = modal.querySelector('form');
                        if (deleteForm) {
                            deleteForm.addEventListener('submit', (submitEvent) => {
                                if (!confirm(`"${productName}" ürününü kalıcı olarak silmek istediğinizden emin misiniz?`)) {
                                    submitEvent.preventDefault();
                                }
                            });
                        }
                    }
                }, 100);
            }
        });
    }
    */
    editProduct(productId) {
        const editButton = document.querySelector(`button[onclick="editProduct(${productId})"]`);
        const editUrl = editButton?.getAttribute('data-edit-url');
        
        if (!editUrl) {
            console.error('Edit URL not found for product:', productId);
            this.showNotification('Düzenleme URL\'si bulunamadı.', 'error');
            return;
        }
        
        console.log('✏️ Editing product:', productId);
        
        // Show loading state
        this.showModalLoading();
        
        fetch(editUrl, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.modal_content) {
                document.getElementById('editModalContent').innerHTML = data.modal_content;
                
                // Initialize edit modal
                const editModal = new bootstrap.Modal(document.getElementById('editProductModal'));
                editModal.show();
                
                // Setup form submit handler
                this.setupEditFormHandler(productId);
                
                // Setup translation tabs for edit modal
                this.setupEditModalTranslations();
                
                // Setup image preview for edit modal
                this.setupEditModalImagePreview();
                
                console.log('✅ Edit modal loaded successfully');
            } else {
                throw new Error('Modal content not received');
            }
        })
        .catch(error => {
            console.error('❌ Edit error:', error);
            this.showNotification('Ürün düzenlenirken hata oluştu.', 'error');
        });
    }
    
    setupEditFormHandler(productId) {
        const editForm = document.getElementById('editProductForm');
        if (!editForm) return;
        
        editForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitEditForm(productId);
        });
    }
    
    submitEditForm(productId) {
        const form = document.getElementById('editProductForm');
        const formData = new FormData(form);
        const editButton = document.querySelector(`button[onclick="editProduct(${productId})"]`);
        const editUrl = editButton?.getAttribute('data-edit-url');
        
        if (!editUrl) {
            this.showNotification('Düzenleme URL\'si bulunamadı.', 'error');
            return;
        }
        
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Kaydediliyor...';
        submitBtn.disabled = true;
        
        fetch(editUrl, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Close modal
                const editModal = bootstrap.Modal.getInstance(document.getElementById('editProductModal'));
                editModal.hide();
                
                this.showNotification('Ürün başarıyla güncellendi.', 'success');
                
                // Reload page after short delay
                setTimeout(() => location.reload(), 1000);
            } else {
                this.showNotification('Form hatası! Lütfen alanları kontrol edin.', 'error');
                console.error('Form errors:', data.errors);
                
                // Restore button
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        })
        .catch(error => {
            console.error('Submit error:', error);
            this.showNotification('Bir hata oluştu!', 'error');
            
            // Restore button
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        });
    }
    
    handleAddFormSubmit(e) {
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        // Basic validation
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
        
        if (!isValid) {
            e.preventDefault();
            this.showNotification('Lütfen tüm gerekli alanları doldurun.', 'error');
            
            // Focus first invalid field
            const firstInvalid = form.querySelector('.is-invalid');
            if (firstInvalid) {
                firstInvalid.focus();
            }
            return;
        }
        
        // Show loading state
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Kaydediliyor...';
        submitBtn.disabled = true;
        
        // Form will be submitted normally
        // Restore button state after delay (in case of error)
        setTimeout(() => {
            if (submitBtn) {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        }, 3000);
    }
    
    setupImagePreviews() {
        console.log('🖼️ Setting up image previews...');
        
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
        
        // Validate file
        const validation = this.validateImageFile(file);
        if (!validation.valid) {
            this.showNotification(validation.message, 'error');
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
                <img src="${e.target.result}" class="image-modern" style="max-width: 150px; max-height: 150px; border-radius: 8px;">
                <p class="small text-muted mt-1">${file.name}</p>
                <small class="text-success">✓ Görsel seçildi</small>
            `;
        };
        reader.readAsDataURL(file);
    }
    
    setupEditModalImagePreview() {
        const editModal = document.getElementById('editProductModal');
        const imageInput = editModal?.querySelector('input[type="file"][name="image"]');
        
        if (imageInput) {
            imageInput.addEventListener('change', (e) => {
                this.handleImagePreview(e.target);
            });
        }
    }
    
    validateImageFile(file) {
        // Check file type
        if (!file.type.startsWith('image/')) {
            return {
                valid: false,
                message: 'Lütfen geçerli bir resim dosyası seçin.'
            };
        }
        
        // Check file size (max 5MB)
        if (file.size > 5 * 1024 * 1024) {
            return {
                valid: false,
                message: 'Resim dosyası 5MB\'dan büyük olamaz.'
            };
        }
        
        return { valid: true };
    }
    
    setupTranslationTabs() {
        console.log('🌐 Setting up translation tabs...');
        
        // Add modal translation tabs
        this.setupModalTranslationTabs('addProductModal');
    }
    
    setupModalTranslationTabs(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        
        modal.addEventListener('shown.bs.modal', () => {
            this.initializeTranslationTabs(modal);
        });
    }
    
    setupEditModalTranslations() {
        const editModal = document.getElementById('editProductModal');
        if (editModal) {
            this.initializeTranslationTabs(editModal);
        }
    }
    
    initializeTranslationTabs(container) {
        const tabs = container.querySelectorAll('.translation-tab');
        const contents = container.querySelectorAll('.translation-content');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const targetLang = tab.getAttribute('data-lang');
                
                // Update active tab
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Show corresponding content
                contents.forEach(content => {
                    if (content.getAttribute('data-lang') === targetLang) {
                        content.classList.add('active');
                    } else {
                        content.classList.remove('active');
                    }
                });
            });
        });
    }
    
    setupFormValidation() {
        console.log('✅ Setting up form validation...');
        
        // Real-time validation for required fields
        document.addEventListener('input', (e) => {
            if (e.target.hasAttribute('required')) {
                this.validateField(e.target);
            }
        });
        
        document.addEventListener('blur', (e) => {
            if (e.target.hasAttribute('required')) {
                this.validateField(e.target);
            }
        }, true);
    }
    
    validateField(field) {
        const value = field.value.trim();
        
        if (field.hasAttribute('required') && !value) {
            field.classList.add('is-invalid');
            field.classList.remove('is-valid');
            return false;
        } else if (value) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            return true;
        }
        
        return true;
    }
    
    setupBulkActions() {
        // Setup bulk selection
        const selectAllCheckbox = document.getElementById('selectAllProducts');
        const productCheckboxes = document.querySelectorAll('.product-checkbox');
        
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', () => {
                productCheckboxes.forEach(checkbox => {
                    checkbox.checked = selectAllCheckbox.checked;
                });
                this.updateBulkActionsVisibility();
            });
        }
        
        productCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateBulkActionsVisibility();
                
                // Update select all checkbox
                if (selectAllCheckbox) {
                    const checkedCount = document.querySelectorAll('.product-checkbox:checked').length;
                    selectAllCheckbox.checked = checkedCount === productCheckboxes.length;
                    selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < productCheckboxes.length;
                }
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
        const selectedCheckboxes = document.querySelectorAll('.product-checkbox:checked');
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
        const selectedCheckboxes = document.querySelectorAll('.product-checkbox:checked');
        const productIds = Array.from(selectedCheckboxes).map(cb => cb.value);
        
        if (productIds.length === 0) {
            this.showNotification('Lütfen en az bir ürün seçin.', 'warning');
            return;
        }
        
        let confirmMessage = '';
        switch (action) {
            case 'delete':
                confirmMessage = `${productIds.length} ürünü silmek istediğinizden emin misiniz?`;
                break;
            case 'activate':
                confirmMessage = `${productIds.length} ürünü aktif yapmak istediğinizden emin misiniz?`;
                break;
            case 'deactivate':
                confirmMessage = `${productIds.length} ürünü pasif yapmak istediğinizden emin misiniz?`;
                break;
        }
        
        if (!confirm(confirmMessage)) return;
        
        // Execute bulk action
        const data = new FormData();
        data.append('action', action);
        data.append('product_ids', JSON.stringify(productIds));
        data.append('csrfmiddlewaretoken', this.getCSRFToken());
        
        fetch('/dashboard/products/bulk-action/', {
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
    
    updateProductStats() {
        // Update product statistics if elements exist
        const totalProducts = document.querySelectorAll('tbody tr').length;
        const activeProducts = document.querySelectorAll('.badge-modern.success').length;
        
        const totalElement = document.getElementById('totalProductsCount');
        const activeElement = document.getElementById('activeProductsCount');
        const inactiveElement = document.getElementById('inactiveProductsCount');
        
        if (totalElement) totalElement.textContent = totalProducts;
        if (activeElement) activeElement.textContent = activeProducts;
        if (inactiveElement) inactiveElement.textContent = totalProducts - activeProducts;
    }
    
    showModalLoading() {
        const modalContent = document.getElementById('editModalContent');
        if (modalContent) {
            modalContent.innerHTML = `
                <div class="text-center p-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Yükleniyor...</span>
                    </div>
                    <p class="mt-2 text-muted">Ürün bilgileri yükleniyor...</p>
                </div>
            `;
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
    refreshProducts() {
        console.log('🔄 Refreshing products...');
        location.reload();
    }
    
    exportProducts() {
        console.log('📊 Exporting products...');
        window.open('/dashboard/products/export/', '_blank');
    }
}

// Product utilities
const ProductUtils = {
    // Generate product slug
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
    
    // Format price
    formatPrice(price) {
        return new Intl.NumberFormat('tr-TR', {
            style: 'currency',
            currency: 'TRY'
        }).format(price);
    },
    
    // Validate SKU format
    isValidSKU(sku) {
        // Allow alphanumeric characters, hyphens, and underscores
        const skuRegex = /^[A-Z0-9_-]+$/i;
        return skuRegex.test(sku) && sku.length >= 3 && sku.length <= 20;
    },
    
    // Calculate discount percentage
    calculateDiscountPercentage(originalPrice, salePrice) {
        if (originalPrice <= 0 || salePrice >= originalPrice) return 0;
        return Math.round(((originalPrice - salePrice) / originalPrice) * 100);
    }
};

// Initialize products manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize on products pages
    if (document.querySelector('.products-page, .products-management')) {
        window.productsManager = new ProductsManager();
    }
});

// Export for global use
window.ProductsManager = ProductsManager;
window.ProductUtils = ProductUtils;



// products.js dosyasının sonuna eklenecek kod

// Global Delete Handler - Tüm delete formları için
// Global Delete Handler - TEK ve KESIN ÇÖZÜM
(function() {
    'use strict';
    
    let deleteHandlerInitialized = false;
    
    function initializeDeleteHandler() {
        if (deleteHandlerInitialized) return;
        deleteHandlerInitialized = true;
        
        console.log('🗑️ Delete handler initializing...');
        
        // Form submit handler
        document.addEventListener('submit', async function(e) {
            if (!e.target.classList.contains('delete-form')) return;
            
            e.preventDefault();
            
            const form = e.target;
            const submitBtn = form.querySelector('.delete-confirm-btn');
            const originalText = submitBtn.innerHTML;
            const itemName = form.dataset.itemName || 'Bu öğe';
            
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Siliniyor...';
            
            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    body: new FormData(form),
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });
                
                if (response.ok) {
                    // Notification
                    if (window.productsManager?.showNotification) {
                        window.productsManager.showNotification(`${itemName} başarıyla silindi!`, 'success');
                    }
                    
                    // Modal kapat - Bootstrap'a bağımlı olmadan
                    const modalElement = form.closest('.modal');
                    if (modalElement) {
                        // Manuel kapat - backdrop hatası olmaz
                        modalElement.style.display = 'none';
                        modalElement.classList.remove('show');
                        modalElement.setAttribute('aria-hidden', 'true');
                        document.body.classList.remove('modal-open');
                        document.body.style.overflow = '';
                        document.body.style.paddingRight = '';
                        
                        // Backdrop temizle
                        document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
                            backdrop.remove();
                        });
                    }
                    
                    // Sayfa yenile
                    setTimeout(() => window.location.reload(), 1000);
                    
                } else {
                    throw new Error('Silme işlemi başarısız');
                }
            } catch (error) {
                console.error('Delete error:', error);
                alert(`Hata: ${error.message}`);
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
        
        console.log('✅ Delete handler initialized successfully');
    }
    
    // Initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeDeleteHandler);
    } else {
        initializeDeleteHandler();
    }
})();