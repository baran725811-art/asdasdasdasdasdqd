// core\static\dashboard\js\components\modal-manager.js - Modal yönetimi
/**
 * ========================================
 * MODAL MANAGER COMPONENT
 * Modal açma/kapama, form handling, loading states
 * ========================================
 */

class ModalManager {
    constructor() {
        this.activeModals = new Map();
        this.defaultOptions = {
            backdrop: true,
            keyboard: true,
            focus: true,
            loading: false,
            autoClose: false,
            onShow: null,
            onHide: null,
            onSubmit: null
        };
        
        this.init();
    }

    init() {
        this.setupGlobalEventListeners();
        this.initializeExistingModals();
        
        console.log('🎭 Modal Manager initialized');
    }

    setupGlobalEventListeners() {
        // Global modal events
        document.addEventListener('show.bs.modal', (e) => {
            this.handleModalShow(e);
        });

        document.addEventListener('hide.bs.modal', (e) => {
            this.handleModalHide(e);
        });

        document.addEventListener('hidden.bs.modal', (e) => {
            this.handleModalHidden(e);
        });

        // ESC key handler
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeTopModal();
            }
        });

        // Form submission in modals
        document.addEventListener('submit', (e) => {
            const modal = e.target.closest('.modal');
            if (modal) {
                this.handleModalFormSubmit(e, modal);
            }
        });

        // Auto-initialize modal triggers
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-modal-action]')) {
                this.handleModalAction(e);
            }
        });
    }

    initializeExistingModals() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            this.registerModal(modal);
        });
    }

    registerModal(modalElement, options = {}) {
        const modalId = modalElement.id;
        if (!modalId) {
            console.warn('Modal element must have an ID');
            return;
        }

        const finalOptions = { ...this.defaultOptions, ...options };
        
        this.activeModals.set(modalId, {
            element: modalElement,
            instance: null,
            options: finalOptions,
            isOpen: false
        });

        // Setup modal-specific handlers
        this.setupModalHandlers(modalElement);
    }

    setupModalHandlers(modalElement) {
        // Close button handlers
        const closeButtons = modalElement.querySelectorAll('[data-bs-dismiss="modal"], .btn-close-modern');
        closeButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                this.hide(modalElement.id);
            });
        });

        // Form validation
        const forms = modalElement.querySelectorAll('form');
        forms.forEach(form => {
            window.formUtils.enableRealTimeValidation(form);
        });

        // Image preview setup
        const imageInputs = modalElement.querySelectorAll('input[type="file"][accept*="image"]');
        imageInputs.forEach(input => {
            window.imageUtils.setupPreview(input);
        });

        // Auto-focus first input
        modalElement.addEventListener('shown.bs.modal', () => {
            const firstInput = modalElement.querySelector('input:not([type="hidden"]):not([type="checkbox"]), textarea, select');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
        });
    }

    // Public API Methods

    show(modalId, options = {}) {
        const modalData = this.activeModals.get(modalId);
        if (!modalData) {
            console.error('Modal not found:', modalId);
            return null;
        }

        const finalOptions = { ...modalData.options, ...options };
        
        // Create Bootstrap modal instance if not exists
        if (!modalData.instance) {
            modalData.instance = new bootstrap.Modal(modalData.element, {
                backdrop: finalOptions.backdrop,
                keyboard: finalOptions.keyboard,
                focus: finalOptions.focus
            });
        }

        // Apply loading state
        if (finalOptions.loading) {
            this.setLoading(modalId, true);
        }

        // Show modal
        modalData.instance.show();
        modalData.isOpen = true;

        // Auto close
        if (finalOptions.autoClose && finalOptions.autoClose > 0) {
            setTimeout(() => {
                this.hide(modalId);
            }, finalOptions.autoClose);
        }

        // Callback
        if (finalOptions.onShow) {
            finalOptions.onShow(modalData.element);
        }

        return modalData.instance;
    }

    hide(modalId) {
        const modalData = this.activeModals.get(modalId);
        if (!modalData || !modalData.instance) {
            return;
        }

        modalData.instance.hide();
        modalData.isOpen = false;

        // Callback
        if (modalData.options.onHide) {
            modalData.options.onHide(modalData.element);
        }
    }

    setLoading(modalId, isLoading) {
        const modalData = this.activeModals.get(modalId);
        if (!modalData) return;

        const modalContent = modalData.element.querySelector('.modal-content');
        if (!modalContent) return;

        if (isLoading) {
            modalContent.classList.add('modal-loading');
            
            // Disable form elements
            const formElements = modalData.element.querySelectorAll('input, textarea, select, button');
            formElements.forEach(el => {
                el.disabled = true;
                el.dataset.wasDisabled = el.disabled;
            });
        } else {
            modalContent.classList.remove('modal-loading');
            
            // Re-enable form elements
            const formElements = modalData.element.querySelectorAll('input, textarea, select, button');
            formElements.forEach(el => {
                if (el.dataset.wasDisabled !== 'true') {
                    el.disabled = false;
                }
                delete el.dataset.wasDisabled;
            });
        }
    }

    updateContent(modalId, content, section = 'body') {
        const modalData = this.activeModals.get(modalId);
        if (!modalData) return;

        const targetElement = modalData.element.querySelector(`.modal-${section}`);
        if (targetElement) {
            targetElement.innerHTML = content;
            
            // Re-setup handlers for new content
            this.setupModalHandlers(modalData.element);
        }
    }

    // Dynamic Modal Creation
    createModal(config) {
        const modalId = config.id || 'modal-' + Date.now();
        const modalHTML = this.generateModalHTML(modalId, config);
        
        // Insert into DOM
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        const modalElement = document.getElementById(modalId);
        if (modalElement) {
            this.registerModal(modalElement, config.options || {});
            
            // Auto-remove after hide
            modalElement.addEventListener('hidden.bs.modal', () => {
                setTimeout(() => {
                    this.destroy(modalId);
                }, 500);
            });
            
            return modalId;
        }
        
        return null;
    }

    generateModalHTML(modalId, config) {
        const {
            title = 'Modal',
            subtitle = '',
            body = '',
            footer = '',
            type = 'default',
            size = '',
            icon = 'fas fa-info-circle',
            closable = true
        } = config;

        const sizeClass = size ? `modal-${size}` : '';
        const typeClass = type !== 'default' ? `${type}-modal` : '';
        
        return `
            <div class="modal fade ${typeClass}" id="${modalId}" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog ${sizeClass}">
                    <div class="modal-content">
                        <div class="modal-header ${type}">
                            <div class="modal-title-wrapper">
                                <div class="modal-icon ${type}">
                                    <i class="${icon}"></i>
                                </div>
                                <div class="modal-title-content">
                                    <h5 class="modal-title">${title}</h5>
                                    ${subtitle ? `<p class="modal-subtitle">${subtitle}</p>` : ''}
                                </div>
                            </div>
                            ${closable ? '<button type="button" class="btn-close-modern" data-bs-dismiss="modal" aria-label="Close"></button>' : ''}
                        </div>
                        <div class="modal-body">
                            ${body}
                        </div>
                        ${footer ? `<div class="modal-footer">${footer}</div>` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    // Specific Modal Types
    
    showConfirmModal(config) {
        const confirmId = this.createModal({
            id: 'confirm-modal-' + Date.now(),
            title: config.title || 'Onay',
            subtitle: config.subtitle || 'Bu işlemi gerçekleştirmek istediğinizden emin misiniz?',
            body: `
                <div class="text-center">
                    <div class="confirmation-icon ${config.type || 'warning'}">
                        <i class="${config.icon || 'fas fa-exclamation-triangle'}"></i>
                    </div>
                    <p class="mb-0">${config.message || 'Bu işlem geri alınamaz.'}</p>
                </div>
            `,
            footer: `
                <div class="modal-actions">
                    <button type="button" class="btn btn-modern secondary" data-bs-dismiss="modal">
                        <i class="fas fa-times me-2"></i>İptal
                    </button>
                    <button type="button" class="btn btn-modern ${config.type || 'warning'}" id="confirm-action">
                        <i class="${config.confirmIcon || 'fas fa-check'} me-2"></i>${config.confirmText || 'Onayla'}
                    </button>
                </div>
            `,
            type: 'confirmation',
            size: 'sm',
            closable: true
        });

        if (confirmId) {
            const modal = document.getElementById(confirmId);
            const confirmBtn = modal.querySelector('#confirm-action');
            
            confirmBtn.addEventListener('click', () => {
                if (config.onConfirm) {
                    config.onConfirm();
                }
                this.hide(confirmId);
            });
            
            this.show(confirmId);
        }
        
        return confirmId;
    }

    showDeleteModal(config) {
        return this.showConfirmModal({
            title: 'Silme Onayı',
            subtitle: 'Bu öğe kalıcı olarak silinecek',
            message: `<strong class="delete-item-name">${config.itemName}</strong> öğesini silmek istediğinizden emin misiniz?`,
            type: 'danger',
            icon: 'fas fa-trash',
            confirmText: 'Sil',
            confirmIcon: 'fas fa-trash',
            onConfirm: config.onConfirm
        });
    }

    showSuccessModal(config) {
        const successId = this.createModal({
            id: 'success-modal-' + Date.now(),
            title: config.title || 'Başarılı',
            subtitle: config.subtitle || 'İşlem başarıyla tamamlandı',
            body: `
                <div class="text-center">
                    <div class="confirmation-icon success">
                        <i class="fas fa-check"></i>
                    </div>
                    <p class="mb-0">${config.message || 'İşleminiz başarıyla gerçekleştirildi.'}</p>
                </div>
            `,
            footer: `
                <div class="modal-actions center">
                    <button type="button" class="btn btn-modern success" data-bs-dismiss="modal">
                        <i class="fas fa-check me-2"></i>Tamam
                    </button>
                </div>
            `,
            type: 'success',
            size: 'sm',
            options: {
                autoClose: config.autoClose || 3000
            }
        });

        if (successId) {
            this.show(successId);
        }
        
        return successId;
    }

    showImagePreviewModal(imageSrc, title = 'Görsel Önizleme') {
        const previewId = this.createModal({
            id: 'image-preview-' + Date.now(),
            title: title,
            body: `<img src="${imageSrc}" alt="${title}" class="img-fluid">`,
            type: 'view',
            size: 'xl',
            closable: true
        });

        if (previewId) {
            const modal = document.getElementById(previewId);
            modal.classList.add('image-preview-modal');
            this.show(previewId);
        }
        
        return previewId;
    }

    // Form Handling
    handleModalFormSubmit(event, modalElement) {
        const modalId = modalElement.id;
        const modalData = this.activeModals.get(modalId);
        
        if (!modalData || !modalData.options.onSubmit) return;

        event.preventDefault();
        
        const form = event.target;
        
        // Validate form
        if (!window.formUtils.validateForm(form)) {
            window.notificationSystem.error('Lütfen tüm gerekli alanları doldurun.');
            return;
        }

        // Set loading state
        this.setLoading(modalId, true);
        
        // Call submit handler
        modalData.options.onSubmit(form, modalElement)
            .then(() => {
                this.setLoading(modalId, false);
                this.hide(modalId);
            })
            .catch((error) => {
                this.setLoading(modalId, false);
                console.error('Modal form submit error:', error);
                window.notificationSystem.error('Bir hata oluştu: ' + error.message);
            });
    }

    // Event Handlers
    handleModalShow(event) {
        const modal = event.target;
        const modalId = modal.id;
        const modalData = this.activeModals.get(modalId);
        
        if (modalData) {
            modalData.isOpen = true;
        }

        // Add show animation
        modal.classList.add('modal-slide-in');
        setTimeout(() => {
            modal.classList.remove('modal-slide-in');
        }, 300);
    }

    handleModalHide(event) {
        const modal = event.target;
        
        // Add hide animation
        modal.classList.add('modal-slide-out');
    }

    handleModalHidden(event) {
        const modal = event.target;
        const modalId = modal.id;
        const modalData = this.activeModals.get(modalId);
        
        if (modalData) {
            modalData.isOpen = false;
        }

        // Remove animation classes
        modal.classList.remove('modal-slide-out');
    }

    handleModalAction(event) {
        event.preventDefault();
        
        const trigger = event.target;
        const action = trigger.dataset.modalAction;
        const targetModal = trigger.dataset.modalTarget;
        
        switch (action) {
            case 'show':
                if (targetModal) {
                    this.show(targetModal);
                }
                break;
                
            case 'hide':
                if (targetModal) {
                    this.hide(targetModal);
                } else {
                    this.closeTopModal();
                }
                break;
                
            case 'edit':
                this.handleEditAction(trigger);
                break;
                
            case 'delete':
                this.handleDeleteAction(trigger);
                break;
                
            case 'view':
                this.handleViewAction(trigger);
                break;
        }
    }

    handleEditAction(trigger) {
        const editUrl = trigger.dataset.editUrl;
        const itemId = trigger.dataset.itemId;
        
        if (!editUrl) return;
        
        this.loadEditModal(editUrl, itemId);
    }

    handleDeleteAction(trigger) {
        const deleteUrl = trigger.dataset.deleteUrl;
        const itemName = trigger.dataset.itemName || 'Bu öğe';
        
        this.showDeleteModal({
            itemName: itemName,
            onConfirm: () => {
                if (deleteUrl) {
                    this.performDelete(deleteUrl);
                }
            }
        });
    }

    handleViewAction(trigger) {
        const viewUrl = trigger.dataset.viewUrl;
        const imageSrc = trigger.dataset.imageSrc;
        
        if (imageSrc) {
            this.showImagePreviewModal(imageSrc);
        } else if (viewUrl) {
            this.loadViewModal(viewUrl);
        }
    }

    async loadEditModal(url, itemId) {
        try {
            const response = await window.dashboardUtils.get(url);
            const data = await response.json();
            
            if (data.modal_content) {
                const editModalId = 'editModal' + (itemId || '');
                let editModal = document.getElementById(editModalId);
                
                if (!editModal) {
                    // Create modal if doesn't exist
                    document.body.insertAdjacentHTML('beforeend', `
                        <div class="modal fade edit-modal" id="${editModalId}" tabindex="-1">
                            <div class="modal-dialog modal-lg">
                                <div class="modal-content" id="editModalContent">
                                </div>
                            </div>
                        </div>
                    `);
                    editModal = document.getElementById(editModalId);
                    this.registerModal(editModal);
                }
                
                // Update content
                document.getElementById('editModalContent').innerHTML = data.modal_content;
                this.setupModalHandlers(editModal);
                this.show(editModalId);
            }
        } catch (error) {
            console.error('Error loading edit modal:', error);
            window.notificationSystem.error('Modal yüklenirken hata oluştu.');
        }
    }

    async performDelete(url) {
        try {
            const response = await window.dashboardUtils.apiRequest(url, {
                method: 'POST'
            });
            
            if (response.ok) {
                window.notificationSystem.success('Öğe başarıyla silindi.');
                setTimeout(() => location.reload(), 1000);
            } else {
                throw new Error('Silme işlemi başarısız');
            }
        } catch (error) {
            console.error('Delete error:', error);
            window.notificationSystem.error('Silme işlemi sırasında hata oluştu.');
        }
    }

    // Utility Methods
    closeTopModal() {
        const openModals = Array.from(this.activeModals.values())
            .filter(modal => modal.isOpen)
            .sort((a, b) => {
                const aZIndex = parseInt(getComputedStyle(a.element).zIndex) || 0;
                const bZIndex = parseInt(getComputedStyle(b.element).zIndex) || 0;
                return bZIndex - aZIndex;
            });
            
        if (openModals.length > 0) {
            this.hide(openModals[0].element.id);
        }
    }

    getActiveModals() {
        return Array.from(this.activeModals.values()).filter(modal => modal.isOpen);
    }

    isModalOpen(modalId) {
        const modalData = this.activeModals.get(modalId);
        return modalData ? modalData.isOpen : false;
    }

    destroy(modalId) {
        const modalData = this.activeModals.get(modalId);
        if (!modalData) return;

        // Hide modal if open
        if (modalData.isOpen) {
            this.hide(modalId);
        }

        // Dispose Bootstrap instance
        if (modalData.instance) {
            modalData.instance.dispose();
        }

        // Remove from DOM
        setTimeout(() => {
            modalData.element.remove();
            this.activeModals.delete(modalId);
        }, 300);
    }

    destroyAll() {
        this.activeModals.forEach((_, modalId) => {
            this.destroy(modalId);
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.modalManager = new ModalManager();
    
    // Global access for debugging
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        window.modal = window.modalManager;
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModalManager;
}