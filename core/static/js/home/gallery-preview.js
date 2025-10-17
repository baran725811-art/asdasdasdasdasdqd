/**core\static\js\home\gallery-preview.js
 * Gallery Preview Interactive Functions - Enhanced with Video Support
 * Horizontal scroll gallery with unified modal for images and videos
 */

class GalleryPreview {
    constructor() {
        this.scrollWrapper = document.getElementById('galleryScrollWrapper');
        this.prevBtn = document.getElementById('galleryPrev');
        this.nextBtn = document.getElementById('galleryNext');
        this.galleryCards = document.querySelectorAll('.gallery-card');
        this.modal = document.getElementById('homeGalleryModal');
        
        // Modal elements
        this.modalContainer = document.getElementById('homeModalContainer');
        this.modalContent = document.getElementById('homeModalContent');
        this.modalTitle = document.getElementById('homeModalTitle');
        this.modalDescription = document.getElementById('homeModalDescription');
        this.modalDate = document.getElementById('homeModalDate');
        this.modalType = document.getElementById('homeModalType');
        this.modalCurrentIndex = document.getElementById('homeModalCurrentIndex');
        this.modalTotal = document.getElementById('homeModalTotal');
        
        this.currentIndex = 0;
        this.scrollPosition = 0;
        this.cardWidth = 0;
        this.visibleCards = 0;
        this.isScrolling = false;
        this.isModalOpen = false;
        this.galleryItems = [];
        
        this.init();
    }
    
    init() {
        if (!this.scrollWrapper || this.galleryCards.length === 0) return;
        
        this.collectGalleryData();
        this.setupScrollNavigation();
        this.setupModal();
        this.setupTouchGestures();
        this.setupKeyboardNavigation();
        this.calculateDimensions();
        this.updateNavigationState();
        
        // Setup window resize handler
        window.addEventListener('resize', this.handleResize.bind(this));
    }
    
    /**
     * Collect gallery data from DOM
     */
    collectGalleryData() {
        // ÖNCE: Kart data attribute'larından veri topla
        this.galleryItems = Array.from(this.galleryCards).map((card, index) => {
            const mediaContainer = card.querySelector('.gallery-image-container');
            const mediaType = card.dataset.galleryType || 'image';
            
            let itemData = {
                id: card.dataset.galleryId || index.toString(),
                type: mediaType,
                title: card.dataset.galleryTitle || '',
                description: card.dataset.galleryDescription || '',
                date: card.dataset.galleryDate || '',
                element: card.closest('.gallery-item')
            };
            
            // Medya URL'lerini container'dan al
            // Medya URL'lerini container'dan al
            if (mediaContainer) {
                if (mediaType === 'image') {
                    itemData.imageUrl = mediaContainer.dataset.imageUrl;
                    const img = mediaContainer.querySelector('img');
                    if (img && !itemData.imageUrl) {
                        itemData.imageUrl = img.src; // Bu focal point'li URL olacak (kart)
                    }
                    // Original URL için script tag'dan al
                    itemData.originalImageUrl = itemData.imageUrl; // Geçici - script'ten gelecek
                    itemData.altText = img ? img.alt : itemData.title;
                } else if (mediaType === 'video') {
                    itemData.videoUrl = mediaContainer.dataset.videoUrl;
                    // Video source'dan URL al
                    const video = mediaContainer.querySelector('video source');
                    if (video && !itemData.videoUrl) {
                        itemData.videoUrl = video.src;
                    }
                    itemData.videoType = 'file';
                }
            }
            
            return itemData;
        });
        
        // SONRA: Script tag'larından ek bilgileri al
        const dataScripts = document.querySelectorAll('script[id^="home-gallery-data-"]');
        dataScripts.forEach(script => {
            try {
                const jsonData = JSON.parse(script.textContent);
                const itemId = script.id.replace('home-gallery-data-', '');
                
                // Mevcut öğeyi bul ve ek bilgileri ekle
                const existingItem = this.galleryItems.find(item => item.id === itemId);
                if (existingItem) {
                    // JSON'dan gelen ek bilgileri merge et
                    if (jsonData.embedUrl) existingItem.embedUrl = jsonData.embedUrl;
                    if (jsonData.videoType) existingItem.videoType = jsonData.videoType;
                    if (!existingItem.imageUrl && jsonData.imageUrl) existingItem.imageUrl = jsonData.imageUrl;
                    if (!existingItem.videoUrl && jsonData.videoUrl) existingItem.videoUrl = jsonData.videoUrl;
                }
            } catch (e) {
                console.error('Error parsing gallery JSON data:', e);
            }
        });
        
        
    }
    
    /**
     * Setup scroll navigation
     */
    setupScrollNavigation() {
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.scrollPrevious());
        }
        
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.scrollNext());
        }
        
        // Setup scroll event listener
        this.scrollWrapper.addEventListener('scroll', this.handleScroll.bind(this), { passive: true });
    }
    
    /**
     * Setup modal functionality
     */
    setupModal() {
        if (!this.modal) return;
        
        // Setup click handlers for gallery cards - TÜM KARTA EVENT EKLE
        this.galleryCards.forEach((card, index) => {
            // Ana karta tıklama eventi
            card.addEventListener('click', (e) => {
                // Eğer tıklanan element bir link veya button değilse modal aç
                if (!e.target.closest('a, button')) {
                    const itemId = card.dataset.galleryId;
                    const mediaType = card.dataset.galleryType;
                    this.openModal(itemId, mediaType);
                }
            });
            
            // Zoom butonu için ayrı event (varsa)
            const zoomBtn = card.querySelector('.zoom-btn');
            if (zoomBtn) {
                zoomBtn.addEventListener('click', (e) => {
                    e.stopPropagation(); // Kart click'ini engelle
                    const itemId = card.dataset.galleryId;
                    const mediaType = card.dataset.galleryType;
                    this.openModal(itemId, mediaType);
                });
            }
            
            // Overlay'e tıklama eventi
            const overlay = card.querySelector('.gallery-overlay');
            if (overlay) {
                overlay.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const itemId = card.dataset.galleryId;
                    const mediaType = card.dataset.galleryType;
                    this.openModal(itemId, mediaType);
                });
            }
        });
        
        // Modal close handlers
        const modalClose = this.modal.querySelector('.image-modal-close');
        const modalBackdrop = this.modal.querySelector('.image-modal-backdrop');
        
        if (modalClose) {
            modalClose.addEventListener('click', () => this.closeModal());
        }
        
        if (modalBackdrop) {
            modalBackdrop.addEventListener('click', () => this.closeModal());
        }
        
        // Modal navigation
        const modalPrev = this.modal.querySelector('#homePrevBtn');
        const modalNext = this.modal.querySelector('#homeNextBtn');
        
        if (modalPrev) {
            modalPrev.addEventListener('click', () => this.showPreviousItem());
        }
        
        if (modalNext) {
            modalNext.addEventListener('click', () => this.showNextItem());
        }
        
        // Keyboard navigation for modal
        document.addEventListener('keydown', this.handleModalKeyboard.bind(this));
    }
    
    /**
     * Setup touch gestures
     */
    setupTouchGestures() {
        let startX = null;
        let startScrollLeft = null;
        const minSwipeDistance = 50;
        
        this.scrollWrapper.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startScrollLeft = this.scrollWrapper.scrollLeft;
        }, { passive: true });
        
        this.scrollWrapper.addEventListener('touchmove', (e) => {
            if (!startX) return;
            
            const currentX = e.touches[0].clientX;
            const diff = startX - currentX;
            
            this.scrollWrapper.scrollLeft = startScrollLeft + diff;
        }, { passive: true });
        
        this.scrollWrapper.addEventListener('touchend', (e) => {
            if (!startX) return;
            
            const endX = e.changedTouches[0].clientX;
            const diff = startX - endX;
            
            if (Math.abs(diff) > minSwipeDistance) {
                if (diff > 0) {
                    this.scrollNext();
                } else {
                    this.scrollPrevious();
                }
            }
            
            startX = null;
            startScrollLeft = null;
        }, { passive: true });
    }
    
    /**
     * Setup keyboard navigation
     */
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            if (this.isModalOpen) return; // Modal has its own keyboard handler
            
            if (!this.isGalleryFocused()) return;
            
            switch (e.key) {
                case 'ArrowLeft':
                    e.preventDefault();
                    this.scrollPrevious();
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.scrollNext();
                    break;
                case 'Enter':
                case ' ':
                    e.preventDefault();
                    const focusedCard = document.activeElement.closest('.gallery-card');
                    if (focusedCard) {
                        const itemId = focusedCard.dataset.galleryId;
                        const mediaType = focusedCard.dataset.galleryType;
                        this.openModal(itemId, mediaType);
                    }
                    break;
            }
        });
    }
    
    /**
     * Calculate dimensions for scroll navigation
     */
    calculateDimensions() {
        if (this.galleryCards.length === 0) return;
        
        const firstCard = this.galleryCards[0];
        const computedStyle = window.getComputedStyle(firstCard);
        const margin = parseInt(computedStyle.marginRight) || 32;
        
        this.cardWidth = firstCard.offsetWidth + margin;
        this.visibleCards = Math.floor(this.scrollWrapper.offsetWidth / this.cardWidth);
    }
    
    /**
     * Scroll navigation methods
     */
    scrollPrevious() {
        if (this.isScrolling) return;
        
        this.isScrolling = true;
        const scrollAmount = this.cardWidth * Math.min(this.visibleCards, 2);
        
        this.scrollWrapper.scrollTo({
            left: Math.max(0, this.scrollWrapper.scrollLeft - scrollAmount),
            behavior: 'smooth'
        });
        
        setTimeout(() => {
            this.isScrolling = false;
            this.updateNavigationState();
        }, 500);
    }
    
    scrollNext() {
        if (this.isScrolling) return;
        
        this.isScrolling = true;
        const scrollAmount = this.cardWidth * Math.min(this.visibleCards, 2);
        const maxScroll = this.scrollWrapper.scrollWidth - this.scrollWrapper.offsetWidth;
        
        this.scrollWrapper.scrollTo({
            left: Math.min(maxScroll, this.scrollWrapper.scrollLeft + scrollAmount),
            behavior: 'smooth'
        });
        
        setTimeout(() => {
            this.isScrolling = false;
            this.updateNavigationState();
        }, 500);
    }
    
    handleScroll() {
        if (!this.isScrolling) {
            this.updateNavigationState();
        }
    }
    
    updateNavigationState() {
        const scrollLeft = this.scrollWrapper.scrollLeft;
        const maxScroll = this.scrollWrapper.scrollWidth - this.scrollWrapper.offsetWidth;
        
        if (this.prevBtn) {
            this.prevBtn.classList.toggle('disabled', scrollLeft <= 0);
            this.prevBtn.disabled = scrollLeft <= 0;
        }
        
        if (this.nextBtn) {
            this.nextBtn.classList.toggle('disabled', scrollLeft >= maxScroll - 1);
            this.nextBtn.disabled = scrollLeft >= maxScroll - 1;
        }
    }
    
    /**
     * Modal methods - Enhanced for Video Support
     */
    openModal(itemId, mediaType) {
        
        
        const itemData = this.galleryItems.find(item => item.id === itemId);
        if (!itemData) {
            console.error('Gallery item not found:', itemId);
            return;
        }
        
        this.currentIndex = this.galleryItems.findIndex(item => item.id === itemId);
        
        // Update counter
        if (this.modalCurrentIndex && this.modalTotal) {
            this.modalCurrentIndex.textContent = this.currentIndex + 1;
            this.modalTotal.textContent = this.galleryItems.length;
        }
        
        this.showModalContent(itemData);
        
        // Show modal
        this.modal.classList.add('show');
        this.modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
        this.isModalOpen = true;
        
        // Focus management
        const modalClose = this.modal.querySelector('.image-modal-close');
        if (modalClose) {
            modalClose.focus();
        }
        
        this.trackGalleryView(itemData);
    }
    
    showModalContent(itemData) {
        
        
        // Set title and info
        if (this.modalTitle) this.modalTitle.textContent = itemData.title || '';
        if (this.modalDescription) this.modalDescription.textContent = itemData.description || '';
        if (this.modalDate) this.modalDate.textContent = itemData.date || '';
        if (this.modalType) {
            this.modalType.innerHTML = itemData.type === 'video' 
                ? '<i class="fas fa-play-circle"></i> Video'
                : '<i class="fas fa-image"></i> Resim';
        }
        
        // Clear previous content
        this.modalContent.innerHTML = '';
        
        // Check if we have required data
        if (itemData.type === 'video' && !itemData.videoUrl) {
            console.error('Video URL missing for video item:', itemData);
            this.createVideoErrorElement(this.modalContent);
            return;
        } else if (itemData.type === 'image' && !itemData.imageUrl) {
            console.error('Image URL missing for image item:', itemData);
            this.createImageErrorElement(this.modalContent);
            return;
        }
        
        // Add/remove video modal styling
        if (itemData.type === 'video') {
            this.modalContainer.classList.add('video-modal');
            this.createVideoContent(itemData, this.modalContent);
        } else {
            this.modalContainer.classList.remove('video-modal');
            this.createImageContent(itemData, this.modalContent);
        }
    }
    
    createImageErrorElement(container) {
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 200px;
            color: #666;
            text-align: center;
            padding: 2rem;
        `;
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 1rem; color: #f39c12;"></i>
            <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">Görsel yüklenemedi</p>
            <p style="font-size: 0.9rem; opacity: 0.8;">Lütfen daha sonra tekrar deneyin.</p>
        `;
        container.appendChild(errorDiv);
    }
    
    createImageContent(itemData, container) {
        const img = document.createElement('img');
        // Modal için orijinal URL kullan
        img.src = itemData.originalImageUrl || itemData.imageUrl;
        img.alt = itemData.altText || itemData.title;
        img.className = 'image-modal-image';
        img.style.cssText = `
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            border-radius: 12px;
        `;
        
        container.appendChild(img);
    }
    
    createVideoContent(itemData, container) {
        
        
        // Create video wrapper
        const videoWrapper = document.createElement('div');
        videoWrapper.style.cssText = `
            display: flex;
            align-items: center;
            justify-content: center;
            width: 100%;
            height: 100%;
            min-height: 400px;
            background: #000;
            border-radius: 12px;
            overflow: hidden;
        `;
        
        let videoElement = null;
        
        if (itemData.videoType === 'file' && itemData.videoUrl) {
            // Direct video file
            videoElement = this.createVideoElement(itemData.videoUrl);
        } else if (itemData.videoType === 'youtube' && itemData.embedUrl) {
            // YouTube iframe
            videoElement = this.createYouTubeIframe(itemData.embedUrl);
        } else if (itemData.videoType === 'vimeo' && itemData.embedUrl) {
            // Vimeo iframe
            videoElement = this.createVimeoIframe(itemData.embedUrl);
        } else if (itemData.videoUrl) {
            // Fallback for any video URL
            videoElement = this.createVideoElement(itemData.videoUrl);
        }
        
        if (videoElement) {
            videoWrapper.appendChild(videoElement);
            container.appendChild(videoWrapper);
            
            // Auto-focus for better UX
            setTimeout(() => {
                if (videoElement.tagName === 'VIDEO') {
                    videoElement.play().catch(e => console.log('Autoplay prevented:', e));
                }
            }, 300);
        } else {
            console.error('Could not create video element for:', itemData);
            this.createVideoErrorElement(videoWrapper);
            container.appendChild(videoWrapper);
        }
    }
    
    createVideoElement(videoUrl) {
        const video = document.createElement('video');
        
        // Video attributes
        video.controls = true;
        video.autoplay = true;
        video.muted = false;
        video.preload = 'metadata';
        video.playsInline = true;
        
        // Responsive video styling
        video.style.cssText = `
            width: 100%;
            max-width: 800px;
            height: auto;
            max-height: 450px;
            border-radius: 8px;
            background: #000;
        `;
        
        // Create source element
        const source = document.createElement('source');
        source.src = videoUrl;
        source.type = 'video/mp4';
        video.appendChild(source);
        
        // Error handling
        video.onerror = () => {
            console.error('Video load error for:', videoUrl);
        };
        
        video.onloadedmetadata = () => {
            console.log('Video metadata loaded:', video.videoWidth, 'x', video.videoHeight);
        };
        
        return video;
    }
    
    createYouTubeIframe(embedUrl) {
        const iframe = document.createElement('iframe');
        iframe.src = embedUrl + (embedUrl.includes('?') ? '&' : '?') + 'autoplay=1&rel=0&modestbranding=1';
        iframe.allowFullscreen = true;
        iframe.allow = 'autoplay; fullscreen';
        iframe.style.cssText = `
            width: 100%;
            max-width: 800px;
            height: 450px;
            border: none;
            border-radius: 8px;
            background: #000;
        `;
        
        return iframe;
    }
    
    createVimeoIframe(embedUrl) {
        const iframe = document.createElement('iframe');
        iframe.src = embedUrl + (embedUrl.includes('?') ? '&' : '?') + 'autoplay=1&title=0&byline=0&portrait=0';
        iframe.allowFullscreen = true;
        iframe.allow = 'autoplay; fullscreen';
        iframe.style.cssText = `
            width: 100%;
            max-width: 800px;
            height: 450px;
            border: none;
            border-radius: 8px;
            background: #000;
        `;
        
        return iframe;
    }
    
    createVideoErrorElement(container) {
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 200px;
            color: #666;
            text-align: center;
        `;
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle" style="font-size: 3rem; margin-bottom: 1rem; color: #f39c12;"></i>
            <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">Video yüklenemedi</p>
            <p style="font-size: 0.9rem; opacity: 0.8;">Lütfen daha sonra tekrar deneyin.</p>
        `;
        container.appendChild(errorDiv);
    }
    
    closeModal() {
        if (!this.isModalOpen) return;
        
        // Stop video/iframe content
        if (this.modalContent) {
            const video = this.modalContent.querySelector('video');
            const iframe = this.modalContent.querySelector('iframe');
            
            if (video) {
                video.pause();
                video.currentTime = 0;
                video.src = '';
            }
            
            if (iframe) {
                iframe.src = 'about:blank';
            }
            
            this.modalContent.innerHTML = '';
        }
        
        // Remove video modal styling
        this.modalContainer.classList.remove('video-modal');
        
        // Hide modal
        this.modal.classList.remove('show');
        this.modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
        this.isModalOpen = false;
        
        
    }
    
    showPreviousItem() {
        if (!this.isModalOpen) return;
        
        let newIndex = this.currentIndex - 1;
        if (newIndex < 0) {
            newIndex = this.galleryItems.length - 1; // Circular navigation
        }
        
        this.currentIndex = newIndex;
        const nextItem = this.galleryItems[newIndex];
        
        if (nextItem) {
            // Update counter
            if (this.modalCurrentIndex && this.modalTotal) {
                this.modalCurrentIndex.textContent = this.currentIndex + 1;
                this.modalTotal.textContent = this.galleryItems.length;
            }
            
            this.showModalContent(nextItem);
        }
    }
    
    showNextItem() {
        if (!this.isModalOpen) return;
        
        let newIndex = this.currentIndex + 1;
        if (newIndex >= this.galleryItems.length) {
            newIndex = 0; // Circular navigation
        }
        
        this.currentIndex = newIndex;
        const nextItem = this.galleryItems[newIndex];
        
        if (nextItem) {
            // Update counter
            if (this.modalCurrentIndex && this.modalTotal) {
                this.modalCurrentIndex.textContent = this.currentIndex + 1;
                this.modalTotal.textContent = this.galleryItems.length;
            }
            
            this.showModalContent(nextItem);
        }
    }
    
    /**
     * Handle modal keyboard navigation
     */
    handleModalKeyboard(e) {
        if (!this.isModalOpen) return;
        
        switch (e.key) {
            case 'Escape':
                e.preventDefault();
                this.closeModal();
                break;
            case 'ArrowLeft':
                e.preventDefault();
                this.showPreviousItem();
                break;
            case 'ArrowRight':
                e.preventDefault();
                this.showNextItem();
                break;
        }
    }
    
    /**
     * Utility methods
     */
    isGalleryFocused() {
        const gallerySection = document.getElementById('galleryPreview');
        return gallerySection && gallerySection.contains(document.activeElement);
    }
    
    handleResize() {
        this.calculateDimensions();
        this.updateNavigationState();
    }
    
    trackGalleryView(itemData) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'gallery_view', {
                event_category: 'engagement',
                event_label: `${itemData.type}_${itemData.title || 'untitled'}`,
                event_value: this.currentIndex + 1
            });
        }
    }
    
    /**
     * Get current gallery state
     */
    getState() {
        return {
            currentIndex: this.currentIndex,
            totalItems: this.galleryItems.length,
            scrollPosition: this.scrollWrapper.scrollLeft,
            isModalOpen: this.isModalOpen
        };
    }
    
    /**
     * Destroy gallery instance
     */
    destroy() {
        // Remove event listeners
        if (this.prevBtn) {
            this.prevBtn.removeEventListener('click', this.scrollPrevious);
        }
        
        if (this.nextBtn) {
            this.nextBtn.removeEventListener('click', this.scrollNext);
        }
        
        this.scrollWrapper.removeEventListener('scroll', this.handleScroll);
        window.removeEventListener('resize', this.handleResize);
        document.removeEventListener('keydown', this.handleModalKeyboard);
        
        // Clean up modal
        if (this.isModalOpen) {
            this.closeModal();
        }
    }
}

/**
 * Global functions for modal controls
 */
window.openHomeGalleryModal = function(itemId, mediaType) {
    console.log('Global openHomeGalleryModal called:', itemId, mediaType);
    if (window.homeGalleryPreview) {
        window.homeGalleryPreview.openModal(itemId, mediaType);
    } else {
        console.error('GalleryPreview not initialized');
    }
};

window.closeHomeGalleryModal = function() {
    if (window.homeGalleryPreview) {
        window.homeGalleryPreview.closeModal();
    }
};

window.navigateHomeGallery = function(direction) {
    if (window.homeGalleryPreview) {
        if (direction === 'prev') {
            window.homeGalleryPreview.showPreviousItem();
        } else if (direction === 'next') {
            window.homeGalleryPreview.showNextItem();
        }
    }
};

/**
 * Gallery scroll utility functions - Backwards compatibility
 */
window.scrollGallery = function(direction) {
    if (window.homeGalleryPreview) {
        if (direction === 'prev') {
            window.homeGalleryPreview.scrollPrevious();
        } else if (direction === 'next') {
            window.homeGalleryPreview.scrollNext();
        }
    }
};

/**
 * Initialize gallery when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    
    window.homeGalleryPreview = new GalleryPreview();
    console.log('Home GalleryPreview initialized:', window.homeGalleryPreview);
});

/**
 * Cleanup on page unload
 */
window.addEventListener('beforeunload', () => {
    if (window.homeGalleryPreview) {
        window.homeGalleryPreview.destroy();
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GalleryPreview;
}