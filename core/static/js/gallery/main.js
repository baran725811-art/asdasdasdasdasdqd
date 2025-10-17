// Gallery Page JavaScript - Clean Unified Modal System core\static\js\gallery\main.js
class GalleryManager {
    constructor() {
        this.currentFilter = 'all';
        this.currentModalIndex = -1;
        this.galleryItems = [];
        this.homeGalleryItems = [];
        this.isModalOpen = false;
        this.currentGalleryType = null;
        
        this.init();
    }
    
    init() {
        // Initialize AOS
        if (typeof AOS !== 'undefined') {
            AOS.init({
                duration: 800,
                easing: 'ease-out-cubic',
                once: true,
                offset: 100
            });
        }
        
        this.cacheElements();
        this.setupEventListeners();
        this.collectGalleryData();
        this.collectHomeGalleryData();
        this.initializeComponents();
    }
    
    cacheElements() {
        // Gallery page elements
        this.galleryGrid = document.getElementById('galleryMasonry');
        this.filterTabs = document.querySelectorAll('.filter-tab');
        this.galleryModal = document.getElementById('galleryModal');
        this.galleryModalContent = document.getElementById('galleryModalContent');
        this.galleryModalTitle = document.getElementById('galleryModalTitle');
        this.galleryModalDescription = document.getElementById('galleryModalDescription');
        this.galleryModalDate = document.getElementById('galleryModalDate');
        this.galleryModalType = document.getElementById('galleryModalType');
        
        // Home gallery elements
        this.homeGalleryModal = document.getElementById('homeGalleryModal');
        this.homeModalContent = document.getElementById('homeModalContent');
        this.homeModalTitle = document.getElementById('homeModalTitle');
        this.homeModalDescription = document.getElementById('homeModalDescription');
        this.homeModalDate = document.getElementById('homeModalDate');
        this.homeModalType = document.getElementById('homeModalType');

        // Counter elements for home gallery
        this.homeModalCurrentIndex = document.getElementById('homeModalCurrentIndex');
        this.homeModalTotal = document.getElementById('homeModalTotal');
    }
    
    collectGalleryData() {
        const galleryItems = document.querySelectorAll('.gallery-item[data-id]');
        this.galleryItems = Array.from(galleryItems).map(item => {
            const dataScript = item.querySelector(`script[id="gallery-data-${item.dataset.id}"]`);
            if (dataScript) {
                try {
                    const data = JSON.parse(dataScript.textContent);
                    return { ...data, element: item };
                } catch (e) {
                    console.error('Error parsing gallery data:', e);
                }
            }
            return null;
        }).filter(Boolean);
        
        console.log('Gallery items collected:', this.galleryItems.length);
    }
    
    collectHomeGalleryData() {
        // Featured gallery items - script elementlerinden veri topla
        const featuredDataScripts = document.querySelectorAll('script[id^="featured-gallery-data-"]');
        this.homeGalleryItems = Array.from(featuredDataScripts).map(script => {
            try {
                const data = JSON.parse(script.textContent);
                // İlgili featured-item elementini bul
                const itemId = script.id.replace('featured-gallery-data-', '');
                const element = script.closest('.featured-item');
                return { ...data, element: element };
            } catch (e) {
                console.error('Error parsing featured gallery data:', e);
                return null;
            }
        }).filter(Boolean);
        
        console.log('Home gallery items collected:', this.homeGalleryItems.length);
    }
    
    setupEventListeners() {
        // Filter tabs
        this.filterTabs.forEach(tab => {
            tab.addEventListener('click', (e) => this.handleFilterClick(e));
        });
        
        // Keyboard navigation
        document.addEventListener('keydown', (e) => this.handleKeydown(e));
        
        // Window resize
        window.addEventListener('resize', debounce(() => this.updateMasonryLayout(), 250));
    }
    
    initializeComponents() {
        this.initializeCounters();
        this.initializeMasonry();
        this.initializeLazyLoading();
    }
    
    handleFilterClick(e) {
        e.preventDefault();
        const tab = e.currentTarget;
        const filter = tab.dataset.filter;
        this.filterGallery(filter);
        this.updateActiveFilter(tab);
    }
    
    filterGallery(filter) {
        this.currentFilter = filter;
        const items = document.querySelectorAll('.gallery-item');
        
        items.forEach((item, index) => {
            const shouldShow = filter === 'all' || item.dataset.type === filter;
            
            if (shouldShow) {
                item.style.display = 'block';
                setTimeout(() => item.classList.add('visible'), index * 50);
            } else {
                item.classList.remove('visible');
                setTimeout(() => {
                    if (!item.classList.contains('visible')) {
                        item.style.display = 'none';
                    }
                }, 300);
            }
        });
        
        setTimeout(() => this.updateMasonryLayout(), 500);
    }
    
    updateActiveFilter(activeTab) {
        this.filterTabs.forEach(tab => tab.classList.remove('active'));
        activeTab.classList.add('active');
    }
    
    // Gallery Page Modal Functions
    openGalleryModal(itemId, mediaType) {
        console.log('Opening gallery modal:', itemId, mediaType);
        
        const itemData = this.galleryItems.find(item => item.id === itemId);
        if (!itemData) {
            console.error('Gallery item not found:', itemId);
            return;
        }
        
        this.currentGalleryType = 'page';
        this.currentModalIndex = this.galleryItems.findIndex(item => item.id === itemId);
        
        this.showModal(itemData, this.galleryModal, this.galleryModalContent, 
                      this.galleryModalTitle, this.galleryModalDescription, 
                      this.galleryModalDate, this.galleryModalType);
    }
    
    closeGalleryModal() {
        this.hideModal(this.galleryModal, this.galleryModalContent);
    }
    
    navigateGallery(direction) {
        if (!this.isModalOpen || this.currentGalleryType !== 'page') return;
        
        const visibleItems = this.galleryItems.filter(item => 
            item.element && item.element.style.display !== 'none'
        );
        
        let newIndex;
        if (direction === 'next') {
            newIndex = (this.currentModalIndex + 1) % visibleItems.length;
        } else {
            newIndex = (this.currentModalIndex - 1 + visibleItems.length) % visibleItems.length;
        }
        
        this.currentModalIndex = newIndex;
        const nextItem = visibleItems[newIndex];
        
        if (nextItem) {
            this.showModal(nextItem, this.galleryModal, this.galleryModalContent,
                          this.galleryModalTitle, this.galleryModalDescription,
                          this.galleryModalDate, this.galleryModalType);
        }
    }
    
    // Home Gallery Modal Functions
    openHomeGalleryModal(itemId, mediaType) {
        console.log('Opening home gallery modal:', itemId, mediaType);
        
        const itemData = this.homeGalleryItems.find(item => item.id === itemId);
        if (!itemData) {
            console.error('Home gallery item not found:', itemId);
            return;
        }
        
        this.currentGalleryType = 'home';
        this.currentModalIndex = this.homeGalleryItems.findIndex(item => item.id === itemId);
        
        // Get additional data from DOM for home gallery
        const element = itemData.element;
        const imgElement = element.querySelector('img, video, .video-thumbnail');
        const videoElement = element.querySelector('video source');
        
        const enhancedData = {
            ...itemData,
            imageUrl: imgElement ? (imgElement.src || this.extractBackgroundImageUrl(imgElement)) : null,
            videoUrl: videoElement ? videoElement.src : null,
            altText: imgElement ? imgElement.alt : itemData.title
        };
        
        // Update counter before showing modal
        if (this.homeModalCurrentIndex && this.homeModalTotal) {
            this.homeModalCurrentIndex.textContent = this.currentModalIndex + 1;
            this.homeModalTotal.textContent = this.homeGalleryItems.length;
        }

        this.showModal(enhancedData, this.homeGalleryModal, this.homeModalContent,
                      this.homeModalTitle, this.homeModalDescription,
                      this.homeModalDate, this.homeModalType);





    }
    
    closeHomeGalleryModal() {
        this.hideModal(this.homeGalleryModal, this.homeModalContent);
    }
    
    navigateHomeGallery(direction) {
        if (!this.isModalOpen || this.currentGalleryType !== 'home') return;
        
        let newIndex;
        if (direction === 'next') {
            newIndex = (this.currentModalIndex + 1) % this.homeGalleryItems.length;
        } else {
            newIndex = (this.currentModalIndex - 1 + this.homeGalleryItems.length) % this.homeGalleryItems.length;
        }
        
        this.currentModalIndex = newIndex;
        const nextItem = this.homeGalleryItems[newIndex];
        
        if (nextItem) {
            this.openHomeGalleryModal(nextItem.id, nextItem.type);
        }
        
        // Update counter - EKLE
        if (this.homeModalCurrentIndex && this.homeModalTotal) {
            this.homeModalCurrentIndex.textContent = this.currentModalIndex + 1;
            this.homeModalTotal.textContent = this.homeGalleryItems.length;
        }
    }
    
    
    // Unified Modal Display Logic - UPDATED
    showModal(itemData, modalElement, contentElement, titleElement, descriptionElement, dateElement, typeElement) {
        console.log('Showing modal for item:', itemData);

        if (!modalElement || !contentElement) {
            console.error('Modal elements not found');
            return;
        }

        modalElement.style.display = 'flex';
        modalElement.setAttribute('aria-hidden', 'false');

        // Clear previous content
        contentElement.innerHTML = '';

        // Set modal info
        if (titleElement) titleElement.textContent = itemData.title || '';
        if (descriptionElement) descriptionElement.textContent = itemData.description || '';
        if (dateElement) dateElement.textContent = itemData.date || '';
        if (typeElement) {
            typeElement.innerHTML = itemData.type === 'video' 
                ? '<i class="fas fa-play-circle"></i> Video'
                : '<i class="fas fa-image"></i> Resim';
        }

        // Get modal container for video-specific styling
        const modalContainer = modalElement.querySelector('.image-modal-container');

        // Create content based on media type
        if (itemData.type === 'image') {
            // Remove video-specific styling
            if (modalContainer) {
                modalContainer.classList.remove('video-modal');
            }
            this.createImageContent(itemData, contentElement);

        } else if (itemData.type === 'video') {
            // Add video-specific styling
            if (modalContainer) {
                modalContainer.classList.add('video-modal');
            }
            this.createVideoContent(itemData, contentElement);
        }

        // Show modal
        modalElement.classList.add('show');
        this.isModalOpen = true;
        document.body.style.overflow = 'hidden';

        // Force reflow to ensure styles are applied
        modalElement.offsetHeight;
    }



    
    createImageContent(itemData, container) {
        console.log('DEBUG - Modal Image URLs:');
        console.log('imageUrl:', itemData.imageUrl);
        console.log('originalImageUrl:', itemData.originalImageUrl);
        console.log('modalImageUrl:', itemData.modalImageUrl);
        
        const img = document.createElement('img');
        // Modal için optimize edilmiş orijinal URL kullan (focal point'siz)
        img.src = itemData.originalImageUrl || itemData.imageUrl;
        img.alt = itemData.altText || itemData.title;
        img.style.maxWidth = '100%';
        img.style.maxHeight = '80vh';
        img.style.objectFit = 'contain';
        img.style.borderRadius = '15px';
        img.style.display = 'block';
        img.style.margin = '0 auto';
        
        console.log('Final image src:', img.src);
        
        container.appendChild(img);
    }
    
    



    // Video element oluşturma metodlarını güncelle
    createVideoContent(itemData, container) {
        console.log('Creating video content:', itemData);
        
        // Create video wrapper for better control
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
            console.log('Video element created and added to wrapper');

            // Auto-focus for better UX
            setTimeout(() => {
                if (videoElement.tagName === 'VIDEO') {
                    videoElement.play().catch(e => console.log('Autoplay prevented:', e));
                }
            }, 300);

        } else {
            console.error('Could not create video element for:', itemData);
            // Show error message in modal
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
            videoWrapper.appendChild(errorDiv);
            container.appendChild(videoWrapper);
        }
    }
    
    // Yeni gelişmiş video element metodunu ekle
    createEnhancedVideoElement(videoUrl) {
        const video = document.createElement('video');
        
        // Video ayarları
        video.controls = true;
        video.autoplay = true;
        video.muted = false; // Ses için
        video.preload = 'auto'; // Tüm videoyu yükle
        video.playsInline = true; // Mobil için
        
        // CSS stilleri
        video.style.cssText = `
            width: 80vw;
            height: 45vw;
            max-width: 1200px;
            max-height: 675px;
            border-radius: 15px;
            background-color: #000;
        `;
        
        // Multiple format support
        const supportedFormats = [
            { src: videoUrl, type: 'video/mp4' },
            { src: videoUrl.replace('.mp4', '.webm'), type: 'video/webm' },
            { src: videoUrl.replace('.mp4', '.ogg'), type: 'video/ogg' }
        ];
        
        // Ana format
        const mainSource = document.createElement('source');
        mainSource.src = videoUrl;
        mainSource.type = 'video/mp4';
        video.appendChild(mainSource);
        
        // Error handling
        video.onerror = (e) => {
            console.error('Video load error:', e);
            console.log('Trying alternative approach...');
            
            // Alternative approach: Direct src
            video.innerHTML = '';
            video.src = videoUrl;
            video.load();
        };
        
        video.onloadedmetadata = () => {
            console.log('Video metadata loaded successfully');
            console.log('Video dimensions:', video.videoWidth, 'x', video.videoHeight);
        };
        
        video.oncanplay = () => {
            console.log('Video can start playing');
        };
        
        video.onplay = () => {
            console.log('Video started playing');
        };
        
        // Force load
        video.load();
        
        return video;
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
    
    hideModal(modalElement, contentElement) {
        if (!modalElement) return;
        
        // Önce video/iframe durdur
        if (contentElement) {
            const video = contentElement.querySelector('video');
            const iframe = contentElement.querySelector('iframe');

            if (video) {
                video.pause();
                video.currentTime = 0;
                video.src = ''; // Video kaynağını temizle
            }

            if (iframe) {
                iframe.src = 'about:blank'; // iframe'i temizle
            }

            // Content'i hemen temizle
            contentElement.innerHTML = '';
        }

        // Modal container'dan video-modal class'ını kaldır
        const modalContainer = modalElement.querySelector('.image-modal-container');
        if (modalContainer) {
            modalContainer.classList.remove('video-modal');
        }

        // Modal'ı gizle - doğru class'ları kullan
        modalElement.classList.remove('show');
        modalElement.style.display = 'none';
        modalElement.setAttribute('aria-hidden', 'true');

        // State'i temizle
        this.isModalOpen = false;
        this.currentGalleryType = null;
        document.body.style.overflow = '';

        console.log('Modal closed and cleaned up');
    }
    
    handleKeydown(e) {
        if (!this.isModalOpen) return;
        
        switch (e.key) {
            case 'Escape':
                if (this.currentGalleryType === 'page') {
                    this.closeGalleryModal();
                } else if (this.currentGalleryType === 'home') {
                    this.closeHomeGalleryModal();
                }
                break;
            case 'ArrowLeft':
                if (this.currentGalleryType === 'page') {
                    this.navigateGallery('prev');
                } else if (this.currentGalleryType === 'home') {
                    this.navigateHomeGallery('prev');
                }
                break;
            case 'ArrowRight':
                if (this.currentGalleryType === 'page') {
                    this.navigateGallery('next');
                } else if (this.currentGalleryType === 'home') {
                    this.navigateHomeGallery('next');
                }
                break;
        }
    }
    
    extractBackgroundImageUrl(element) {
        const bgImage = element.style.backgroundImage;
        if (bgImage) {
            const matches = bgImage.match(/url\(["']?([^"']*)["']?\)/);
            return matches ? matches[1] : null;
        }
        return null;
    }
    
    initializeCounters() {
        const counters = document.querySelectorAll('.stat-number[data-counter]');
        if (!counters.length) return;
        
        if ('IntersectionObserver' in window) {
            const counterObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.animateCounter(entry.target);
                        counterObserver.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });
            
            counters.forEach(counter => counterObserver.observe(counter));
        }
    }
    
    animateCounter(element) {
        const target = parseInt(element.dataset.counter);
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;
        
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                element.textContent = target.toLocaleString();
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current).toLocaleString();
            }
        }, 16);
    }
    
    initializeMasonry() {
        this.updateMasonryLayout();
    }
    
    updateMasonryLayout() {
        if (!this.galleryGrid) return;
        
        const items = Array.from(this.galleryGrid.children);
        const columns = Math.floor(this.galleryGrid.offsetWidth / 320);
        
        if (columns <= 1) return;
        
        const columnHeights = new Array(columns).fill(0);
        
        items.forEach(item => {
            if (item.style.display === 'none') return;
            
            const shortestColumnIndex = columnHeights.indexOf(Math.min(...columnHeights));
            
            item.style.position = 'absolute';
            item.style.left = `${(shortestColumnIndex * 100) / columns}%`;
            item.style.top = `${columnHeights[shortestColumnIndex]}px`;
            item.style.width = `${100 / columns}%`;
            
            columnHeights[shortestColumnIndex] += item.offsetHeight + 32;
        });
        
        this.galleryGrid.style.height = `${Math.max(...columnHeights)}px`;
        this.galleryGrid.style.position = 'relative';
    }
    
    initializeLazyLoading() {
        if (!('IntersectionObserver' in window)) return;
        
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        img.classList.remove('lazy');
                    }
                    imageObserver.unobserve(img);
                }
            });
        }, { rootMargin: '50px 0px' });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            img.classList.add('lazy');
            imageObserver.observe(img);
        });
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Global functions for modal controls
window.openGalleryModal = function(itemId, mediaType) {
    console.log('Global openGalleryModal called:', itemId, mediaType);
    if (window.galleryManager) {
        window.galleryManager.openGalleryModal(itemId, mediaType);
    } else {
        console.error('GalleryManager not initialized');
    }
};

window.closeGalleryModal = function() {
    if (window.galleryManager) {
        window.galleryManager.closeGalleryModal();
    }
};

window.navigateGallery = function(direction) {
    if (window.galleryManager) {
        window.galleryManager.navigateGallery(direction);
    }
};

window.openHomeGalleryModal = function(itemId, mediaType) {
    console.log('Global openHomeGalleryModal called:', itemId, mediaType);
    if (window.galleryManager) {
        window.galleryManager.openHomeGalleryModal(itemId, mediaType);
    } else {
        console.error('GalleryManager not initialized');
    }
};

window.closeHomeGalleryModal = function() {
    if (window.galleryManager) {
        window.galleryManager.closeHomeGalleryModal();
    }
};

window.navigateHomeGallery = function(direction) {
    if (window.galleryManager) {
        window.galleryManager.navigateHomeGallery(direction);
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing GalleryManager...');
    window.galleryManager = new GalleryManager();
    console.log('GalleryManager initialized:', window.galleryManager);
});