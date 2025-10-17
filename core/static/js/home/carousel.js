/**core\static\js\home\carousel.js
 * Home Carousel Interactive Functions
 * Advanced carousel controls with smooth animations
 */

class HomeCarousel {
    constructor() {
        this.carousel = document.getElementById('mainCarousel');
        this.playPauseBtn = document.getElementById('carouselPlayPause');
        this.indicators = document.querySelectorAll('.modern-indicators button');
        this.slides = document.querySelectorAll('.carousel-item');
        
        this.isPlaying = true;
        this.currentSlide = 0;
        this.slideInterval = 6000;
        this.progressInterval = null;
        this.autoplayTimeout = null;
        
        this.init();
    }
    
    init() {
        if (!this.carousel) return;
        
        this.setupEventListeners();
        this.setupProgressIndicators();
        this.setupKeyboardNavigation();
        this.setupSwipeGestures();
        this.startAutoplay();
    }
    
    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Play/Pause button
        if (this.playPauseBtn) {
            this.playPauseBtn.addEventListener('click', this.togglePlayPause.bind(this));
        }
        
        // Bootstrap carousel events
        this.carousel.addEventListener('slide.bs.carousel', this.handleSlideStart.bind(this));
        this.carousel.addEventListener('slid.bs.carousel', this.handleSlideEnd.bind(this));
        
        // Mouse events for auto-pause
        this.carousel.addEventListener('mouseenter', this.pauseOnHover.bind(this));
        this.carousel.addEventListener('mouseleave', this.resumeOnLeave.bind(this));
        
        // Window visibility change
        document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
        
        // Indicator clicks
        this.indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => this.goToSlide(index));
        });
    }
    
    /**
     * Setup progress indicators animation
     */
    setupProgressIndicators() {
        this.indicators.forEach((indicator, index) => {
            const progressBar = indicator.querySelector('.indicator-progress');
            if (progressBar) {
                progressBar.style.width = index === 0 ? '100%' : '0%';
            }
        });
    }
    
    /**
     * Start progress animation for current indicator
     */
    startProgressAnimation(index) {
        this.indicators.forEach((indicator, i) => {
            const progressBar = indicator.querySelector('.indicator-progress');
            if (progressBar) {
                if (i === index) {
                    progressBar.style.transition = `width ${this.slideInterval}ms linear`;
                    progressBar.style.width = '100%';
                } else {
                    progressBar.style.transition = 'none';
                    progressBar.style.width = '0%';
                }
            }
        });
    }
    
    /**
     * Setup keyboard navigation
     */
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            if (!this.isCarouselFocused()) return;
            
            switch (e.key) {
                case 'ArrowLeft':
                    e.preventDefault();
                    this.previousSlide();
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.nextSlide();
                    break;
                case ' ':
                    e.preventDefault();
                    this.togglePlayPause();
                    break;
                case 'Home':
                    e.preventDefault();
                    this.goToSlide(0);
                    break;
                case 'End':
                    e.preventDefault();
                    this.goToSlide(this.slides.length - 1);
                    break;
            }
        });
    }
    
    /**
     * Setup touch/swipe gestures
     */
    setupSwipeGestures() {
        let startX = null;
        let startY = null;
        const minSwipeDistance = 50;
        
        this.carousel.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        }, { passive: true });
        
        this.carousel.addEventListener('touchmove', (e) => {
            if (!startX || !startY) return;
            
            const currentX = e.touches[0].clientX;
            const currentY = e.touches[0].clientY;
            
            const diffX = startX - currentX;
            const diffY = startY - currentY;
            
            // Prevent vertical scrolling during horizontal swipe
            if (Math.abs(diffX) > Math.abs(diffY)) {
                e.preventDefault();
            }
        }, { passive: false });
        
        this.carousel.addEventListener('touchend', (e) => {
            if (!startX || !startY) return;
            
            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            
            const diffX = startX - endX;
            const diffY = startY - endY;
            
            // Check if horizontal swipe
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > minSwipeDistance) {
                if (diffX > 0) {
                    this.nextSlide();
                } else {
                    this.previousSlide();
                }
            }
            
            startX = null;
            startY = null;
        }, { passive: true });
    }
    
    /**
     * Handle slide start event
     */
    handleSlideStart(e) {
        this.currentSlide = e.to;
        this.pauseAutoplay();
        
        // Update indicators
        this.indicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index === this.currentSlide);
        });
    }
    
    /**
     * Handle slide end event
     */
    handleSlideEnd(e) {
        this.currentSlide = e.to;
        
        if (this.isPlaying) {
            this.startProgressAnimation(this.currentSlide);
            this.startAutoplay();
        }
        
        // Trigger custom event
        this.carousel.dispatchEvent(new CustomEvent('carousel:slideChanged', {
            detail: { currentSlide: this.currentSlide }
        }));
    }
    
    /**
     * Toggle play/pause
     */
    togglePlayPause() {
        if (this.isPlaying) {
            this.pause();
        } else {
            this.play();
        }
    }
    
    /**
     * Play carousel
     */
    play() {
        this.isPlaying = true;
        this.updatePlayPauseButton();
        this.startProgressAnimation(this.currentSlide);
        this.startAutoplay();
    }
    
    /**
     * Pause carousel
     */
    pause() {
        this.isPlaying = false;
        this.updatePlayPauseButton();
        this.pauseAutoplay();
        this.pauseProgressAnimation();
    }
    
    /**
     * Start autoplay
     */
    startAutoplay() {
        if (!this.isPlaying) return;
        
        this.autoplayTimeout = setTimeout(() => {
            this.nextSlide();
        }, this.slideInterval);
    }
    
    /**
     * Pause autoplay
     */
    pauseAutoplay() {
        if (this.autoplayTimeout) {
            clearTimeout(this.autoplayTimeout);
            this.autoplayTimeout = null;
        }
    }
    
    /**
     * Pause progress animation
     */
    pauseProgressAnimation() {
        this.indicators.forEach(indicator => {
            const progressBar = indicator.querySelector('.indicator-progress');
            if (progressBar) {
                const computedStyle = window.getComputedStyle(progressBar);
                const currentWidth = computedStyle.width;
                progressBar.style.transition = 'none';
                progressBar.style.width = currentWidth;
            }
        });
    }
    
    /**
     * Update play/pause button
     */
    updatePlayPauseButton() {
        if (!this.playPauseBtn) return;
        
        const icon = this.playPauseBtn.querySelector('i');
        if (icon) {
            icon.className = this.isPlaying ? 'fas fa-pause' : 'fas fa-play';
        }
        
        this.playPauseBtn.title = this.isPlaying ? 'Duraklat' : 'Oynat';
        this.playPauseBtn.setAttribute('aria-label', this.isPlaying ? 'Carousel duraklat' : 'Carousel oynat');
    }
    
    /**
     * Go to specific slide
     */
    goToSlide(index) {
        if (index >= 0 && index < this.slides.length && index !== this.currentSlide) {
            const bsCarousel = bootstrap.Carousel.getInstance(this.carousel);
            if (bsCarousel) {
                bsCarousel.to(index);
            }
        }
    }
    
    /**
     * Go to next slide
     */
    nextSlide() {
        const bsCarousel = bootstrap.Carousel.getInstance(this.carousel);
        if (bsCarousel) {
            bsCarousel.next();
        }
    }
    
    /**
     * Go to previous slide
     */
    previousSlide() {
        const bsCarousel = bootstrap.Carousel.getInstance(this.carousel);
        if (bsCarousel) {
            bsCarousel.prev();
        }
    }
    
    /**
     * Pause on hover
     */
    pauseOnHover() {
        if (this.isPlaying) {
            this.pauseAutoplay();
            this.pauseProgressAnimation();
        }
    }
    
    /**
     * Resume on mouse leave
     */
    resumeOnLeave() {
        if (this.isPlaying) {
            this.startProgressAnimation(this.currentSlide);
            this.startAutoplay();
        }
    }
    
    /**
     * Handle visibility change (tab switching)
     */
    handleVisibilityChange() {
        if (document.hidden) {
            this.pauseAutoplay();
            this.pauseProgressAnimation();
        } else if (this.isPlaying) {
            this.startProgressAnimation(this.currentSlide);
            this.startAutoplay();
        }
    }
    
    /**
     * Check if carousel is focused
     */
    isCarouselFocused() {
        return this.carousel.contains(document.activeElement) || 
               document.activeElement === this.carousel;
    }
    
    /**
     * Get current slide info
     */
    getCurrentSlideInfo() {
        return {
            currentSlide: this.currentSlide,
            totalSlides: this.slides.length,
            isPlaying: this.isPlaying
        };
    }
    
    /**
     * Destroy carousel instance
     */
    destroy() {
        this.pauseAutoplay();
        
        // Remove event listeners
        if (this.playPauseBtn) {
            this.playPauseBtn.removeEventListener('click', this.togglePlayPause);
        }
        
        this.carousel.removeEventListener('slide.bs.carousel', this.handleSlideStart);
        this.carousel.removeEventListener('slid.bs.carousel', this.handleSlideEnd);
        this.carousel.removeEventListener('mouseenter', this.pauseOnHover);
        this.carousel.removeEventListener('mouseleave', this.resumeOnLeave);
        
        document.removeEventListener('visibilitychange', this.handleVisibilityChange);
    }
}

/**
 * Smooth scroll to next section
 */
function scrollToNextSection() {
    const carousel = document.getElementById('heroCarousel');
    if (!carousel) return;
    
    const nextSection = carousel.nextElementSibling;
    if (nextSection) {
        const targetPosition = nextSection.offsetTop - 80; // Account for navbar
        
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    }
}

/**
 * Initialize carousel when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    // Initialize carousel
    window.homeCarousel = new HomeCarousel();
    
    // Setup scroll indicator click
    const scrollIndicator = document.querySelector('.scroll-indicator');
    if (scrollIndicator) {
        scrollIndicator.addEventListener('click', scrollToNextSection);
        scrollIndicator.style.cursor = 'pointer';
    }
    
    // Setup floating elements animation
    const floatingElements = document.querySelectorAll('.floating-shape');
    floatingElements.forEach((element, index) => {
        element.style.animationDelay = `${index * 2}s`;
    });
});

/**
 * Cleanup on page unload
 */
window.addEventListener('beforeunload', () => {
    if (window.homeCarousel) {
        window.homeCarousel.destroy();
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HomeCarousel;
}