/**core\static\js\modal.js
 * Universal Image Modal System
 * Supports single image and gallery navigation
 */

class UniversalImageModal {
    constructor() {
        this.modal = document.getElementById('imageModal');
        this.backdrop = document.getElementById('imageModalBackdrop');
        this.closeBtn = document.getElementById('imageModalClose');
        this.prevBtn = document.getElementById('imageModalPrev');
        this.nextBtn = document.getElementById('imageModalNext');
        this.image = document.getElementById('imageModalImage');
        this.title = document.getElementById('imageModalTitle');
        this.description = document.getElementById('imageModalDescription');
        this.info = document.getElementById('imageModalInfo');
        this.meta = document.getElementById('imageModalMeta');
        this.date = document.getElementById('imageModalDate');
        this.category = document.getElementById('imageModalCategory');
        this.loading = document.getElementById('imageModalLoading');
        this.counter = document.getElementById('imageModalCounter');
        this.currentIndex = document.getElementById('imageModalCurrentIndex');
        this.totalImages = document.getElementById('imageModalTotal');
        
        this.images = [];
        this.currentImageIndex = 0;
        this.isOpen = false;
        
        this.init();
    }
    
    init() {
        if (!this.modal) return;
        
        this.setupEventListeners();
        this.setupKeyboardNavigation();
    }
    
    setupEventListeners() {
        // Close modal events
        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', () => this.close());
        }
        
        if (this.backdrop) {
            this.backdrop.addEventListener('click', () => this.close());
        }
        
        // Navigation events
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.showPrevious());
        }
        
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.showNext());
        }
        
        // Image load events
        if (this.image) {
            this.image.addEventListener('load', () => this.hideLoading());
            this.image.addEventListener('error', () => this.handleImageError());
        }
    }
    
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            if (!this.isOpen) return;
            
            switch (e.key) {
                case 'Escape':
                    e.preventDefault();
                    this.close();
                    break;
                case 'ArrowLeft':
                    e.preventDefault();
                    this.showPrevious();
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.showNext();
                    break;
            }
        });
    }
    
    /**
     * Open modal with single image
     * @param {Object} imageData - Image data object
     */
    openSingle(imageData) {
        this.images = [imageData];
        this.currentImageIndex = 0;
        this.open();
    }
    
    /**
     * Open modal with gallery images
     * @param {Array} imagesArray - Array of image data objects
     * @param {number} startIndex - Starting image index
     */
    openGallery(imagesArray, startIndex = 0) {
        this.images = imagesArray;
        this.currentImageIndex = Math.max(0, Math.min(startIndex, imagesArray.length - 1));
        this.open();
    }
    
    /**
     * Open modal and display current image
     */
    open() {
        if (!this.modal || this.images.length === 0) return;
        
        this.isOpen = true;
        this.updateModalDisplay();
        this.showModal();
        this.updateNavigation();
        
        // Focus management
        if (this.closeBtn) {
            this.closeBtn.focus();
        }
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        // Track analytics
        this.trackModalOpen();
    }
    
    /**
     * Close modal
     */
    close() {
        if (!this.modal || !this.isOpen) return;
        
        this.isOpen = false;
        this.hideModal();
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        // Clear images to free memory
        setTimeout(() => {
            if (!this.isOpen) {
                this.images = [];
                this.currentImageIndex = 0;
            }
        }, 300);
        
        // Track analytics
        this.trackModalClose();
    }
    
    /**
     * Show previous image
     */
    showPrevious() {
        if (this.images.length <= 1) return;
        
        this.currentImageIndex = this.currentImageIndex > 0 
            ? this.currentImageIndex - 1 
            : this.images.length - 1;
        
        this.updateModalDisplay();
        this.updateNavigation();
    }
    
    /**
     * Show next image
     */
    showNext() {
        if (this.images.length <= 1) return;
        
        this.currentImageIndex = this.currentImageIndex < this.images.length - 1 
            ? this.currentImageIndex + 1 
            : 0;
        
        this.updateModalDisplay();
        this.updateNavigation();
    }
    
    /**
     * Update modal display with current image
     */
    updateModalDisplay() {
        const currentImage = this.images[this.currentImageIndex];
        if (!currentImage) return;
        
        // Show loading
        this.showLoading();
        
        // Update image
        if (this.image) {
            this.image.src = currentImage.src || currentImage.url || currentImage.image;
            this.image.alt = currentImage.alt || currentImage.title || '';
        }
        
        // Update title
        if (this.title) {
            this.title.textContent = currentImage.title || '';
        }
        
        // Update description
        if (this.description) {
            const desc = currentImage.description || '';
            this.description.textContent = desc;
            this.description.style.display = desc ? 'block' : 'none';
        }
        
        // Update metadata
        this.updateMetadata(currentImage);
        
        // Update counter
        this.updateCounter();
        
        // Update modal class for single/multiple images
        this.updateModalClass();
    }
    
    /**
     * Update metadata display
     */
    updateMetadata(imageData) {
        let hasMetadata = false;
        
        // Update date
        if (this.date && imageData.date) {
            this.date.textContent = imageData.date;
            this.date.style.display = 'inline';
            hasMetadata = true;
        } else if (this.date) {
            this.date.style.display = 'none';
        }
        
        // Update category
        if (this.category && imageData.category) {
            this.category.textContent = imageData.category;
            this.category.style.display = 'inline';
            hasMetadata = true;
        } else if (this.category) {
            this.category.style.display = 'none';
        }
        
        // Show/hide metadata section
        if (this.meta) {
            this.meta.style.display = hasMetadata ? 'flex' : 'none';
        }
        
        // Show/hide info section
        if (this.info) {
            const hasDescription = imageData.description && imageData.description.trim();
            const shouldShow = hasDescription || hasMetadata;
            this.info.style.display = shouldShow ? 'block' : 'none';
        }
    }
    
    /**
     * Update counter display
     */
    updateCounter() {
        if (this.currentIndex && this.totalImages) {
            this.currentIndex.textContent = this.currentImageIndex + 1;
            this.totalImages.textContent = this.images.length;
        }
    }
    
    /**
     * Update modal class for styling
     */
    updateModalClass() {
        if (this.modal) {
            if (this.images.length === 1) {
                this.modal.classList.add('single-image');
            } else {
                this.modal.classList.remove('single-image');
            }
        }
    }
    
    /**
     * Update navigation buttons
     */
    updateNavigation() {
        const isSingle = this.images.length <= 1;
        
        if (this.prevBtn) {
            this.prevBtn.style.display = isSingle ? 'none' : 'flex';
            this.prevBtn.disabled = false; // Circular navigation
        }
        
        if (this.nextBtn) {
            this.nextBtn.style.display = isSingle ? 'none' : 'flex';
            this.nextBtn.disabled = false; // Circular navigation
        }
        
        if (this.counter) {
            this.counter.style.display = isSingle ? 'none' : 'block';
        }
    }
    
    /**
     * Show modal with animation
     */
    showModal() {
        if (this.modal) {
            this.modal.classList.add('show');
            this.modal.setAttribute('aria-hidden', 'false');
        }
    }
    
    /**
     * Hide modal with animation
     */
    hideModal() {
        if (this.modal) {
            this.modal.classList.remove('show');
            this.modal.setAttribute('aria-hidden', 'true');
        }
    }
    
    /**
     * Show loading indicator
     */
    showLoading() {
        if (this.loading) {
            this.loading.classList.add('show');
        }
        if (this.image) {
            this.image.style.opacity = '0.5';
        }
    }
    
    /**
     * Hide loading indicator
     */
    hideLoading() {
        if (this.loading) {
            this.loading.classList.remove('show');
        }
        if (this.image) {
            this.image.style.opacity = '1';
        }
    }
    
    /**
     * Handle image load error
     */
    handleImageError() {
        this.hideLoading();
        console.error('Failed to load image:', this.images[this.currentImageIndex]);
        
        if (this.image) {
            this.image.alt = 'Görsel yüklenemedi';
        }
    }
    
    /**
     * Track modal open event
     */
    trackModalOpen() {
        const currentImage = this.images[this.currentImageIndex];
        
        if (typeof gtag !== 'undefined') {
            gtag('event', 'modal_image_view', {
                event_category: 'engagement',
                event_label: currentImage?.title || 'untitled_image',
                event_value: this.currentImageIndex + 1
            });
        }
    }
    
    /**
     * Track modal close event
     */
    trackModalClose() {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'modal_close', {
                event_category: 'engagement',
                event_label: 'image_modal'
            });
        }
    }
    
    /**
     * Get current state
     */
    getState() {
        return {
            isOpen: this.isOpen,
            currentIndex: this.currentImageIndex,
            totalImages: this.images.length,
            currentImage: this.images[this.currentImageIndex] || null
        };
    }
    
    /**
     * Destroy modal instance
     */
    destroy() {
        this.close();
        
        // Remove event listeners
        if (this.closeBtn) {
            this.closeBtn.removeEventListener('click', this.close);
        }
        
        if (this.backdrop) {
            this.backdrop.removeEventListener('click', this.close);
        }
        
        if (this.prevBtn) {
            this.prevBtn.removeEventListener('click', this.showPrevious);
        }
        
        if (this.nextBtn) {
            this.nextBtn.removeEventListener('click', this.showNext);
        }
        
        this.images = [];
        this.currentImageIndex = 0;
    }
}

/**
 * Global modal instance
 */
let universalModal = null;

/**
 * Initialize modal when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    universalModal = new UniversalImageModal();
});

/**
 * Cleanup on page unload
 */
window.addEventListener('beforeunload', () => {
    if (universalModal) {
        universalModal.destroy();
    }
});

/**
 * Global helper functions for easy access
 */
window.openImageModal = function(imageData) {
    if (universalModal) {
        universalModal.openSingle(imageData);
    }
};

window.openGalleryModal = function(imagesArray, startIndex = 0) {
    if (universalModal) {
        universalModal.openGallery(imagesArray, startIndex);
    }
};

window.closeImageModal = function() {
    if (universalModal) {
        universalModal.close();
    }
};

/**
 * Auto-setup for common image patterns
 */
document.addEventListener('DOMContentLoaded', () => {
    // Auto-setup for images with data-modal attributes
    setupAutoModal();
});

function setupAutoModal() {
    // Single images with data-modal-image
    document.querySelectorAll('[data-modal-image]').forEach(element => {
        element.addEventListener('click', (e) => {
            e.preventDefault();
            
            const imageData = {
                src: element.dataset.modalImage,
                title: element.dataset.modalTitle || '',
                description: element.dataset.modalDescription || '',
                date: element.dataset.modalDate || '',
                category: element.dataset.modalCategory || ''
            };
            
            window.openImageModal(imageData);
        });
    });
    
    // Gallery groups with data-gallery-group
    const galleryGroups = {};
    
    document.querySelectorAll('[data-gallery-group]').forEach(element => {
        const groupName = element.dataset.galleryGroup;
        
        if (!galleryGroups[groupName]) {
            galleryGroups[groupName] = [];
        }
        
        const imageData = {
            src: element.dataset.galleryImage || element.src,
            title: element.dataset.galleryTitle || '',
            description: element.dataset.galleryDescription || '',
            date: element.dataset.galleryDate || '',
            category: element.dataset.galleryCategory || '',
            element: element
        };
        
        galleryGroups[groupName].push(imageData);
        
        element.addEventListener('click', (e) => {
            e.preventDefault();
            
            const index = galleryGroups[groupName].findIndex(img => img.element === element);
            window.openGalleryModal(galleryGroups[groupName], index);
        });
    });
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UniversalImageModal;
}