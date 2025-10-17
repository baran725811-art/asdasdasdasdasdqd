//# Navbar interaktifliği core\static\js\base\navbar.js
/**
 * Modern Navbar JavaScript
 * Handles scroll effects, mobile menu, language switching, and accessibility
 */

class ModernNavbar {
    constructor() {
        this.navbar = document.getElementById('mainNavbar');
        this.mobileOverlay = document.getElementById('mobileNavOverlay');
        this.navbarToggler = document.querySelector('.navbar-toggler');
        this.navbarCollapse = document.querySelector('.navbar-collapse');
        this.navLinks = document.querySelectorAll('.nav-link');
        this.languageForms = document.querySelectorAll('.language-form');
        
        this.isScrolled = false;
        this.isMobileMenuOpen = false;
        this.scrollThreshold = 100;
        this.lastScrollTop = 0;
        
        this.init();
    }
    
    init() {
        this.setupScrollEffects();
        this.setupMobileMenu();
        this.setupLanguageSwitcher();
        this.setupSmoothScrolling();
        this.setupAccessibility();
        this.setupPerformanceOptimizations();
        
        // Initialize on page load
        this.handleScroll();
    }
    
    /**
     * Setup scroll effects for navbar
     */
    setupScrollEffects() {
        let ticking = false;
        
        const handleScroll = () => {
            if (!ticking) {
                requestAnimationFrame(() => {
                    this.handleScroll();
                    ticking = false;
                });
                ticking = true;
            }
        };
        
        window.addEventListener('scroll', handleScroll, { passive: true });
        window.addEventListener('resize', this.handleResize.bind(this), { passive: true });
    }
    
    /**
     * Handle scroll events
     */
    handleScroll() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const shouldBeScrolled = scrollTop > this.scrollThreshold;
        
        // Add/remove scrolled class
        if (shouldBeScrolled !== this.isScrolled) {
            this.isScrolled = shouldBeScrolled;
            this.navbar.classList.toggle('scrolled', this.isScrolled);
        }
        
        // Hide/show navbar on scroll (optional enhancement)
        if (window.innerWidth > 991) {
            const isScrollingDown = scrollTop > this.lastScrollTop && scrollTop > 200;
            const isScrollingUp = scrollTop < this.lastScrollTop;
            
            if (isScrollingDown && !this.isMobileMenuOpen) {
                this.navbar.style.transform = 'translateY(-100%)';
            } else if (isScrollingUp || scrollTop < 100) {
                this.navbar.style.transform = 'translateY(0)';
            }
        }
        
        this.lastScrollTop = scrollTop;
    }
    
    /**
     * Handle window resize
     */
    handleResize() {
        // Close mobile menu on desktop
        if (window.innerWidth > 991 && this.isMobileMenuOpen) {
            this.closeMobileMenu();
        }
        
        // Reset navbar transform on mobile
        if (window.innerWidth <= 991) {
            this.navbar.style.transform = 'translateY(0)';
        }
    }
    
    /**
     * Setup mobile menu functionality
     */
    setupMobileMenu() {
        if (!this.navbarToggler || !this.navbarCollapse) return;
        
        // Toggle button click
        this.navbarToggler.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggleMobileMenu();
        });

        // Overlay click
        if (this.mobileOverlay) {
            this.mobileOverlay.addEventListener('click', () => {
                this.closeMobileMenu();
            });
        }

        // DROPDOWN EVENT HANDLING - EKLE
        const languageDropdown = document.getElementById('languageDropdown');
        if (languageDropdown) {
            languageDropdown.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        }

        // Bootstrap dropdown events - EKLE
        document.addEventListener('click', (e) => {
            if (e.target.closest('.language-selector')) {
                e.stopPropagation();
            }
        });

        // Close menu when clicking nav links
        this.navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                // Dropdown toggle ise menüyü kapatma
                if (link.classList.contains('dropdown-toggle')) {
                    return;
                }

                if (window.innerWidth <= 991) {
                    setTimeout(() => this.closeMobileMenu(), 300);
                }
            });
        });
    









        
        // Close menu on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isMobileMenuOpen) {
                this.closeMobileMenu();
            }
        });
        
        // Handle Bootstrap collapse events
        this.navbarCollapse.addEventListener('shown.bs.collapse', () => {
            this.isMobileMenuOpen = true;
           this.mobileOverlay?.classList.add('show');
            document.body.style.overflow = 'hidden';
        });
        
        this.navbarCollapse.addEventListener('hidden.bs.collapse', () => {
            this.isMobileMenuOpen = false;
            this.mobileOverlay?.classList.remove('show');
            document.body.style.overflow = '';
        });
    } 
    
    /**     * Toggle mobile menu         */
    toggleMobileMenu() {
        const isExpanded = this.navbarToggler.getAttribute('aria-expanded') === 'true';
        
        if (isExpanded) {
            this.closeMobileMenu();
        } else {
            this.openMobileMenu();
        }
    }
    
    /**     * Open mobile menu      */
    openMobileMenu() {
        // Bootstrap Collapse API kullan
        if (this.navbarCollapse) {
            const bsCollapse = bootstrap.Collapse.getOrCreateInstance(this.navbarCollapse);
            bsCollapse.show();
        }
    }
    
    /**     * Close mobile menu      */
    closeMobileMenu() {
        // Bootstrap Collapse API kullan
        if (this.navbarCollapse) {
            const bsCollapse = bootstrap.Collapse.getOrCreateInstance(this.navbarCollapse);
            bsCollapse.hide();
        }
    }
    
    /**
     * Setup language switcher
     */
    setupLanguageSwitcher() {
        this.languageForms.forEach(form => {
            form.addEventListener('submit', (e) => {
                const button = form.querySelector('button[type="submit"]');
                if (button) {
                    button.disabled = true;
                    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Değiştiriliyor...';
                }
            });
        });
    }
    
    /**
     * Setup smooth scrolling for anchor links
     */
    setupSmoothScrolling() {
        this.navLinks.forEach(link => {
            const href = link.getAttribute('href');
            
            // Check if it's an anchor link
            if (href && href.startsWith('#')) {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    
                    const targetId = href.substring(1);
                    const targetElement = document.getElementById(targetId);
                    
                    if (targetElement) {
                        const navbarHeight = this.navbar.offsetHeight;
                        const targetPosition = targetElement.offsetTop - navbarHeight - 20;
                        
                        window.scrollTo({
                            top: targetPosition,
                            behavior: 'smooth'
                        });
                    }
                });
            }
        });
    }
    
    /**
     * Setup accessibility features
     */
    setupAccessibility() {
        // Add proper ARIA labels
        this.updateAriaLabels();
        
        // Handle keyboard navigation
        this.setupKeyboardNavigation();
        
        // Add focus management
        this.setupFocusManagement();
    }
    
    /**
     * Update ARIA labels based on current state
     */
    updateAriaLabels() {
        const currentPage = document.querySelector('.nav-link.active');
        if (currentPage) {
            currentPage.setAttribute('aria-current', 'page');
        }
    }
    
    /**
     * Setup keyboard navigation
     */
    setupKeyboardNavigation() {
        this.navLinks.forEach((link, index) => {
            link.addEventListener('keydown', (e) => {
                let nextIndex;
                
                switch (e.key) {
                    case 'ArrowRight':
                    case 'ArrowDown':
                        e.preventDefault();
                        nextIndex = (index + 1) % this.navLinks.length;
                        this.navLinks[nextIndex].focus();
                        break;
                        
                    case 'ArrowLeft':
                    case 'ArrowUp':
                        e.preventDefault();
                        nextIndex = (index - 1 + this.navLinks.length) % this.navLinks.length;
                        this.navLinks[nextIndex].focus();
                        break;
                        
                    case 'Home':
                        e.preventDefault();
                        this.navLinks[0].focus();
                        break;
                        
                    case 'End':
                        e.preventDefault();
                        this.navLinks[this.navLinks.length - 1].focus();
                        break;
                }
            });
        });
    }
    
    /**
     * Setup focus management
     */
    setupFocusManagement() {
        // Trap focus in mobile menu when open
        this.navbarCollapse.addEventListener('shown.bs.collapse', () => {
            const firstFocusable = this.navbarCollapse.querySelector('.nav-link');
            if (firstFocusable) {
                firstFocusable.focus();
            }
        });
        
        
    }
    
    /**
     * Setup performance optimizations
     */
    setupPerformanceOptimizations() {
        // Use will-change for animated elements
        this.navbar.style.willChange = 'transform';
        
        // Remove will-change after animations complete
        this.navbar.addEventListener('transitionend', (e) => {
            if (e.target === this.navbar) {
                this.navbar.style.willChange = 'auto';
            }
        });
        
        // Debounce resize events
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                this.handleResize();
            }, 150);
        });
    }
    
    /**
     * Update active navigation state
     */
    updateActiveNav(currentPath) {
        this.navLinks.forEach(link => {
            link.classList.remove('active');
            link.removeAttribute('aria-current');
            
            const href = link.getAttribute('href');
            if (href && currentPath.includes(href.replace('/', ''))) {
                link.classList.add('active');
                link.setAttribute('aria-current', 'page');
            }
        });
    }
    
    /**
     * Show/hide navbar
     */
    show() {
        this.navbar.style.transform = 'translateY(0)';
    }
    
    hide() {
        if (!this.isMobileMenuOpen) {
            this.navbar.style.transform = 'translateY(-100%)';
        }
    }
    
    /**
     * Destroy navbar instance
     */
    destroy() {
        // Remove event listeners and clean up
        window.removeEventListener('scroll', this.handleScroll);
        window.removeEventListener('resize', this.handleResize);
        
        // Reset styles
        this.navbar.style.transform = '';
        this.navbar.style.willChange = '';
        document.body.style.overflow = '';
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.modernNavbar = new ModernNavbar();
});

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.hidden && window.modernNavbar?.isMobileMenuOpen) {
        window.modernNavbar.closeMobileMenu();
    }
});

// Export for external use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ModernNavbar;
}