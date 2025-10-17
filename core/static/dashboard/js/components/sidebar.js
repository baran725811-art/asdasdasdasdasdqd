// core\static\dashboard\js\components\sidebar.js - Sidebar işlevleri
/**
 * ========================================
 * SIDEBAR COMPONENT JAVASCRIPT
 * Sidebar açma/kapama, responsive davranışlar
 * ========================================
 */

class SidebarManager {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.sidebarToggle = document.getElementById('sidebarToggle');
        this.sidebarClose = document.getElementById('sidebarClose');
        this.sidebarOverlay = document.getElementById('sidebarOverlay');
        this.isOpen = false;
        this.isDesktop = window.innerWidth >= 992;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.handleResize();
        this.setActiveLink();
        
        console.log('🎯 Sidebar Manager initialized');
    }

    setupEventListeners() {
        // Toggle button
        if (this.sidebarToggle) {
            this.sidebarToggle.addEventListener('click', () => this.toggle());
        }

        // Close button
        if (this.sidebarClose) {
            this.sidebarClose.addEventListener('click', () => this.close());
        }

        // Overlay click
        if (this.sidebarOverlay) {
            this.sidebarOverlay.addEventListener('click', () => this.close());
        }

        // ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen && !this.isDesktop) {
                this.close();
            }
        });

        // Window resize
        window.addEventListener('resize', () => this.handleResize());

        // Link hover effects (desktop only)
        this.setupLinkEffects();

        // Touch gestures (mobile)
        this.setupTouchGestures();
    }

    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        if (!this.sidebar) return;

        this.isOpen = true;
        this.sidebar.classList.add('show');
        
        if (this.sidebarOverlay) {
            this.sidebarOverlay.classList.add('show');
        }

        // Prevent body scroll on mobile
        if (!this.isDesktop) {
            document.body.style.overflow = 'hidden';
        }

        // Animation class
        this.sidebar.classList.add('sidebar-slide-in');
        setTimeout(() => {
            this.sidebar.classList.remove('sidebar-slide-in');
        }, 300);

        // Emit event
        this.emit('sidebar:opened');
    }

    close() {
        if (!this.sidebar) return;

        this.isOpen = false;
        this.sidebar.classList.remove('show');
        
        if (this.sidebarOverlay) {
            this.sidebarOverlay.classList.remove('show');
        }

        // Restore body scroll
        document.body.style.overflow = '';

        // Animation class
        this.sidebar.classList.add('sidebar-slide-out');
        setTimeout(() => {
            this.sidebar.classList.remove('sidebar-slide-out');
        }, 300);

        // Emit event
        this.emit('sidebar:closed');
    }

    handleResize() {
        const wasDesktop = this.isDesktop;
        this.isDesktop = window.innerWidth >= 992;

        if (wasDesktop !== this.isDesktop) {
            if (this.isDesktop) {
                // Switch to desktop mode
                this.close();
                document.body.style.overflow = '';
            } else {
                // Switch to mobile mode
                this.close();
            }
        }
    }

    setActiveLink() {
        const currentPath = window.location.pathname;
        const links = this.sidebar?.querySelectorAll('.sidebar-link');
        
        if (!links) return;

        links.forEach(link => {
            link.classList.remove('active');
            
            const href = link.getAttribute('href');
            if (href && (currentPath === href || currentPath.includes(href))) {
                link.classList.add('active');
                
                // Scroll active link into view
                setTimeout(() => {
                    link.scrollIntoView({
                        behavior: 'smooth',
                        block: 'nearest'
                    });
                }, 100);
            }
        });
    }

    setupLinkEffects() {
        if (!this.sidebar) return;

        const links = this.sidebar.querySelectorAll('.sidebar-link');
        
        links.forEach(link => {
            // Click animation
            link.addEventListener('click', (e) => {
                if (!this.isDesktop) {
                    // Close sidebar on mobile after link click
                    setTimeout(() => this.close(), 150);
                }

                // Ripple effect
                this.createRipple(e, link);
            });

            // Preload hover effect
            link.addEventListener('mouseenter', () => {
                if (this.isDesktop) {
                    link.style.transform = 'translateX(5px)';
                }
            });

            link.addEventListener('mouseleave', () => {
                if (this.isDesktop) {
                    link.style.transform = '';
                }
            });
        });
    }

    setupTouchGestures() {
        if (!this.sidebar) return;

        let startX = 0;
        let startTime = 0;
        const threshold = 50; // Minimum swipe distance
        const timeLimit = 300; // Maximum swipe time

        // Swipe to open (from left edge)
        document.addEventListener('touchstart', (e) => {
            if (e.touches[0].clientX < 30 && !this.isOpen) {
                startX = e.touches[0].clientX;
                startTime = Date.now();
            }
        });

        document.addEventListener('touchend', (e) => {
            if (startX > 0) {
                const endX = e.changedTouches[0].clientX;
                const distance = endX - startX;
                const time = Date.now() - startTime;

                if (distance > threshold && time < timeLimit && !this.isOpen) {
                    this.open();
                }
                
                startX = 0;
                startTime = 0;
            }
        });

        // Swipe to close (on sidebar)
        this.sidebar.addEventListener('touchstart', (e) => {
            if (this.isOpen) {
                startX = e.touches[0].clientX;
                startTime = Date.now();
            }
        });

        this.sidebar.addEventListener('touchend', (e) => {
            if (startX > 0 && this.isOpen) {
                const endX = e.changedTouches[0].clientX;
                const distance = startX - endX;
                const time = Date.now() - startTime;

                if (distance > threshold && time < timeLimit) {
                    this.close();
                }
                
                startX = 0;
                startTime = 0;
            }
        });
    }

    createRipple(event, element) {
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

        const ripple = document.createElement('span');
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            left: ${x}px;
            top: ${y}px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 50%;
            transform: scale(0);
            animation: ripple-animation 0.6s linear;
            pointer-events: none;
            z-index: 1;
        `;

        element.style.position = 'relative';
        element.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    }

    // Loading state
    setLoading(isLoading) {
        if (!this.sidebar) return;

        if (isLoading) {
            this.sidebar.classList.add('sidebar-loading');
        } else {
            this.sidebar.classList.remove('sidebar-loading');
        }
    }

    // Update active link programmatically
    updateActiveLink(path) {
        const links = this.sidebar?.querySelectorAll('.sidebar-link');
        if (!links) return;

        links.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === path) {
                link.classList.add('active');
            }
        });
    }

    // Event emitter
    emit(eventName, data = null) {
        const event = new CustomEvent(eventName, { 
            detail: data,
            bubbles: true 
        });
        document.dispatchEvent(event);
    }

    // Public API
    destroy() {
        // Clean up event listeners
        if (this.sidebarToggle) {
            this.sidebarToggle.removeEventListener('click', this.toggle);
        }
        if (this.sidebarClose) {
            this.sidebarClose.removeEventListener('click', this.close);
        }
        if (this.sidebarOverlay) {
            this.sidebarOverlay.removeEventListener('click', this.close);
        }
        
        document.removeEventListener('keydown', this.handleKeydown);
        window.removeEventListener('resize', this.handleResize);
    }
}

// CSS Animations
const sidebarAnimationCSS = `
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;

// Inject CSS
const sidebarAnimationStyle = document.createElement('style');
sidebarAnimationStyle.textContent = sidebarAnimationCSS;
document.head.appendChild(sidebarAnimationStyle);

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.sidebarManager = new SidebarManager();
    
    // Global access for debugging
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        window.sidebar = window.sidebarManager;
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SidebarManager;
}