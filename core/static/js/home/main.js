/**core\static\js\home\main.js
 * Home Page Main JavaScript
 * Coordinates all home page functionality and provides global utilities
 */

class HomePageManager {
    constructor() {
        this.sections = new Map();
        this.observers = new Map();
        this.isInitialized = false;
        this.scrollPosition = 0;
        this.ticking = false;
        
        this.init();
    }
    
    init() {
        this.setupSectionObservers();
        this.setupScrollEffects();
        this.setupSmoothScrolling();
        this.setupLazyLoading();
        this.setupPerformanceOptimizations();
        this.setupAccessibility();
        this.isInitialized = true;
        
        
    }
    
    /**
     * Setup section observers for animations
     */
    setupSectionObservers() {
        const sections = document.querySelectorAll('section[id]');
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const sectionObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.handleSectionInView(entry.target);
                }
            });
        }, observerOptions);
        
        sections.forEach(section => {
            sectionObserver.observe(section);
            this.sections.set(section.id, {
                element: section,
                isVisible: false,
                hasAnimated: false
            });
        });
        
        this.observers.set('sections', sectionObserver);
    }
    
    /**
     * Handle section coming into view
     */
    handleSectionInView(section) {
        const sectionData = this.sections.get(section.id);
        if (!sectionData || sectionData.hasAnimated) return;
        
        sectionData.isVisible = true;
        sectionData.hasAnimated = true;
        
        // Trigger section-specific animations
        this.triggerSectionAnimations(section);
        
        // Track section view for analytics
        this.trackSectionView(section.id);
    }
    
    /**
     * Trigger animations for specific section
     */
    triggerSectionAnimations(section) {
        const sectionId = section.id;
        
        switch (sectionId) {
            case 'statisticsSection':
                // Statistics counter is handled by its own module
                break;
                
            case 'aboutPreview':
                this.animateAboutElements(section);
                break;
                
            case 'servicesGrid':
                this.animateServiceCards(section);
                break;
                
            case 'galleryPreview':
                this.animateGalleryCards(section);
                break;
                
            case 'reviewsSection':
                this.animateReviewCards(section);
                break;
        }
    }
    
    /**
     * Animate about section elements
     */
    animateAboutElements(section) {
        const features = section.querySelectorAll('.feature-item');
        features.forEach((feature, index) => {
            setTimeout(() => {
                feature.classList.add('fade-in-up');
            }, index * 100);
        });
    }
    
    /**
     * Animate service cards
     */
    animateServiceCards(section) {
        const cards = section.querySelectorAll('.service-card');
        cards.forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('fade-in-up');
            }, index * 150);
        });
    }
    
    /**
     * Animate gallery cards
     */
    animateGalleryCards(section) {
        const cards = section.querySelectorAll('.gallery-item');
        cards.forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('fade-in-up');
            }, index * 100);
        });
    }
    
    /**
     * Animate review cards
     */
    animateReviewCards(section) {
        const reviewCard = section.querySelector('.review-card');
        if (reviewCard) {
            reviewCard.classList.add('fade-in');
        }
    }
    
    /**
     * Setup scroll effects
     */
    setupScrollEffects() {
        window.addEventListener('scroll', () => {
            if (!this.ticking) {
                requestAnimationFrame(() => {
                    this.handleScroll();
                    this.ticking = false;
                });
                this.ticking = true;
            }
        }, { passive: true });
    }
    
    /**
     * Handle scroll events
     */
    handleScroll() {
        this.scrollPosition = window.pageYOffset;
        
        // Update navbar
        this.updateNavbarOnScroll();
        
        // Parallax effects
        this.updateParallaxEffects();
        
        // Progress indicators
        this.updateReadingProgress();
    }
    
    /**
     * Update navbar based on scroll
     */
    updateNavbarOnScroll() {
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            navbar.classList.toggle('scrolled', this.scrollPosition > 100);
        }
    }
    
    /**
     * Update parallax effects
     */
    updateParallaxEffects() {
        const parallaxElements = document.querySelectorAll('[data-parallax]');
        
        parallaxElements.forEach(element => {
            const speed = parseFloat(element.dataset.parallax) || 0.5;
            const yPos = -(this.scrollPosition * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });
    }
    
    /**
     * Update reading progress
     */
    updateReadingProgress() {
        const winHeight = window.innerHeight;
        const docHeight = document.documentElement.scrollHeight - winHeight;
        const progress = (this.scrollPosition / docHeight) * 100;
        
        // Update any progress indicators
        const progressBars = document.querySelectorAll('.reading-progress');
        progressBars.forEach(bar => {
            bar.style.width = `${Math.min(progress, 100)}%`;
        });
    }
    
    /**
     * Setup smooth scrolling for anchor links
     */
    setupSmoothScrolling() {
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[href^="#"]');
            if (!link) return;
            
            const href = link.getAttribute('href');
            if (href === '#') return;
            
            const target = document.querySelector(href);
            if (!target) return;
            
            e.preventDefault();
            this.smoothScrollTo(target);
        });
    }
    
    /**
     * Smooth scroll to element
     */
    smoothScrollTo(target, offset = 80) {
        const targetPosition = target.offsetTop - offset;
        
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
        
        // Update URL without triggering scroll
        history.replaceState(null, null, `#${target.id}`);
    }
    
    /**
     * Setup lazy loading for images
     */
    setupLazyLoading() {
        const images = document.querySelectorAll('img[loading="lazy"]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        this.loadImage(img);
                        imageObserver.unobserve(img);
                    }
                });
            });
            
            images.forEach(img => imageObserver.observe(img));
            this.observers.set('images', imageObserver);
        } else {
            // Fallback for browsers without IntersectionObserver
            images.forEach(img => this.loadImage(img));
        }
    }
    
    /**
     * Load image with error handling
     */
    loadImage(img) {
        img.addEventListener('load', () => {
            img.classList.add('loaded');
        });
        
        img.addEventListener('error', () => {
            img.classList.add('error');
            // Optionally set a fallback image
            const fallback = img.dataset.fallback;
            if (fallback) {
                img.src = fallback;
            }
        });
        
        // Trigger loading if not already loaded
        if (!img.src && img.dataset.src) {
            img.src = img.dataset.src;
        }
    }
    
    /**
     * Setup performance optimizations
     */
    setupPerformanceOptimizations() {
        // Preload critical resources
        this.preloadCriticalResources();
        
        // Setup resource hints
        this.setupResourceHints();
        
        // Monitor performance
        this.monitorPerformance();
    }
    
    /**
     * Preload critical resources
     */
    preloadCriticalResources() {
        // Preload hero images
        const heroImages = document.querySelectorAll('.carousel-item img[loading="eager"]');
        heroImages.forEach(img => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = 'image';
            link.href = img.src;
            document.head.appendChild(link);
        });
    }
    
    /**
     * Setup resource hints
     */
    setupResourceHints() {
        // DNS prefetch for external domains
        const externalDomains = ['fonts.googleapis.com', 'cdn.jsdelivr.net'];
        
        externalDomains.forEach(domain => {
            const link = document.createElement('link');
            link.rel = 'dns-prefetch';
            link.href = `//${domain}`;
            document.head.appendChild(link);
        });
    }
    
    /**
     * Monitor performance
     */
    monitorPerformance() {
        if ('performance' in window) {
            window.addEventListener('load', () => {
                setTimeout(() => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    
                    if (perfData.loadEventEnd - perfData.loadEventStart > 3000) {
                        
                    }
                    
                    // Track performance metrics
                    this.trackPerformanceMetrics(perfData);
                }, 0);
            });
        }
    }
    
    /**
     * Setup accessibility enhancements
     */
    setupAccessibility() {
        // Skip link functionality
        this.setupSkipLinks();
        
        // Focus management
        this.setupFocusManagement();
        
        // ARIA updates
        this.setupAriaUpdates();
        
        // Reduced motion support
        this.setupReducedMotion();
    }
    
    /**
     * Setup skip links
     */
    setupSkipLinks() {
        const skipLinks = document.querySelectorAll('.skip-link');
        
        skipLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(link.getAttribute('href'));
                if (target) {
                    target.focus();
                    target.scrollIntoView();
                }
            });
        });
    }
    
    /**
     * Setup focus management
     */
    setupFocusManagement() {
        // Ensure proper focus on page load
        document.addEventListener('DOMContentLoaded', () => {
            const hash = window.location.hash;
            if (hash) {
                const target = document.querySelector(hash);
                if (target) {
                    setTimeout(() => {
                        target.focus();
                    }, 100);
                }
            }
        });
    }
    
    /**
     * Setup ARIA updates
     */
    setupAriaUpdates() {
        // Update ARIA labels for dynamic content
        const dynamicElements = document.querySelectorAll('[data-aria-dynamic]');
        
        dynamicElements.forEach(element => {
            const observer = new MutationObserver(() => {
                this.updateAriaLabels(element);
            });
            
            observer.observe(element, {
                childList: true,
                subtree: true,
                characterData: true
            });
        });
    }
    
    /**
     * Setup reduced motion support
     */
    setupReducedMotion() {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.documentElement.classList.add('reduced-motion');
            
            // Disable autoplay for carousels
            const carousels = document.querySelectorAll('[data-bs-ride="carousel"]');
            carousels.forEach(carousel => {
                carousel.removeAttribute('data-bs-ride');
            });
        }
    }
    
    /**
     * Track section view for analytics
     */
    trackSectionView(sectionId) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'section_view', {
                event_category: 'engagement',
                event_label: sectionId,
                page_title: document.title
            });
        }
    }
    
    /**
     * Track performance metrics
     */
    trackPerformanceMetrics(perfData) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'page_performance', {
                event_category: 'performance',
                event_label: 'home_page',
                value: Math.round(perfData.loadEventEnd - perfData.loadEventStart)
            });
        }
    }
    
    /**
     * Get page state
     */
    getPageState() {
        return {
            isInitialized: this.isInitialized,
            scrollPosition: this.scrollPosition,
            visibleSections: Array.from(this.sections.entries())
                .filter(([id, data]) => data.isVisible)
                .map(([id]) => id),
            totalSections: this.sections.size
        };
    }
    
    /**
     * Destroy page manager
     */
    destroy() {
        // Clean up observers
        this.observers.forEach(observer => observer.disconnect());
        this.observers.clear();
        
        // Clean up sections
        this.sections.clear();
        
        // Remove event listeners
        window.removeEventListener('scroll', this.handleScroll);
        
        this.isInitialized = false;
    }
}

/**
 * Utility functions
 */
window.scrollToSection = function(sectionId) {
    const target = document.getElementById(sectionId);
    if (target && window.homePageManager) {
        window.homePageManager.smoothScrollTo(target);
    }
};

window.getHomePageState = function() {
    if (window.homePageManager) {
        return window.homePageManager.getPageState();
    }
    return null;
};

/**
 * Initialize when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    window.homePageManager = new HomePageManager();
    
    // Set up global error handling
    window.addEventListener('error', (e) => {
        console.error('Home page error:', e.error);
    });
    
    // Set up unhandled promise rejections
    window.addEventListener('unhandledrejection', (e) => {
        console.error('Unhandled promise rejection:', e.reason);
    });
});

/**
 * Cleanup on page unload
 */
window.addEventListener('beforeunload', () => {
    if (window.homePageManager) {
        window.homePageManager.destroy();
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HomePageManager;
}




// Products Carousel Enhanced Functionality
document.addEventListener('DOMContentLoaded', function() {
    const carousel = document.getElementById('productsCarousel');
    if (!carousel) return;

    const indicatorButtons = document.querySelectorAll('.indicator-btn');
    const prevButton = document.querySelector('.nav-prev');
    const nextButton = document.querySelector('.nav-next');
    
    let currentSlide = 0;
    const totalSlides = indicatorButtons.length;

    // Bootstrap carousel instance
    const bsCarousel = new bootstrap.Carousel(carousel, {
        interval: false,
        wrap: true,
        keyboard: true,
        pause: 'hover'
    });

    // Update active indicator
    function updateActiveIndicator(index) {
        indicatorButtons.forEach((btn, i) => {
            if (i === index) {
                btn.classList.add('active');
                btn.setAttribute('aria-current', 'true');
            } else {
                btn.classList.remove('active');
                btn.removeAttribute('aria-current');
            }
        });
    }

    // Update navigation buttons state
    function updateNavigationState(index) {
        if (prevButton && nextButton) {
            // Always keep buttons enabled since we support wrapping
            prevButton.disabled = false;
            nextButton.disabled = false;
        }
    }

    // Handle carousel slide events - DÜZELTİLDİ
    carousel.addEventListener('slide.bs.carousel', function(e) {
        currentSlide = e.to;
        updateActiveIndicator(currentSlide);
        updateNavigationState(currentSlide);
    });

    // Carousel slid event - Slide tamamlandığında da güncelle
    carousel.addEventListener('slid.bs.carousel', function(e) {
        currentSlide = e.to;
        updateActiveIndicator(currentSlide);
        updateNavigationState(currentSlide);
    });

    // Handle indicator button clicks - DÜZELTİLDİ
    indicatorButtons.forEach((btn, index) => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            currentSlide = index;
            bsCarousel.to(index);
        });
    });

    // Handle prev/next button clicks
    if (prevButton) {
        prevButton.addEventListener('click', function(e) {
            e.preventDefault();
            bsCarousel.prev();
        });
    }

    if (nextButton) {
        nextButton.addEventListener('click', function(e) {
            e.preventDefault();
            bsCarousel.next();
        });
    }

    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (e.target.closest('.products-navigation')) {
            switch(e.key) {
                case 'ArrowLeft':
                    e.preventDefault();
                    bsCarousel.prev();
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    bsCarousel.next();
                    break;
                case 'Home':
                    e.preventDefault();
                    bsCarousel.to(0);
                    break;
                case 'End':
                    e.preventDefault();
                    bsCarousel.to(totalSlides - 1);
                    break;
            }
        }
    });

    // Touch/Swipe support for mobile
    let touchStartX = 0;
    let touchEndX = 0;

    carousel.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
    });

    carousel.addEventListener('touchend', function(e) {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
    });

    function handleSwipe() {
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;

        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                // Swipe left - next slide
                bsCarousel.next();
            } else {
                // Swipe right - previous slide
                bsCarousel.prev();
            }
        }
    }

    // Initialize first state
    updateActiveIndicator(0);
    updateNavigationState(0);

    // Intersection Observer for performance
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                carousel.classList.add('carousel-visible');
            } else {
                carousel.classList.remove('carousel-visible');
            }
        });
    }, {
        threshold: 0.5
    });

    observer.observe(carousel);

    // Debug: Console log for testing
    
});