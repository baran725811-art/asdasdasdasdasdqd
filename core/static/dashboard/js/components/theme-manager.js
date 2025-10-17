// core\static\dashboard\js\components\theme-manager.js - Tema yönetimi
/**
 * ========================================
 * THEME MANAGER COMPONENT
 * Tema değiştirme, saklama ve yönetim sistemi
 * ========================================
 */

class ThemeManager {
    constructor() {
        this.currentTheme = 'default';
        this.themeSelector = document.getElementById('themeSelector');
        this.themeOptions = document.querySelectorAll('.theme-option');
        this.storageKey = 'dashboard-theme';
        
        this.themes = {
            default: {
                name: 'Varsayılan',
                icon: 'fas fa-palette',
                description: 'Mavi gradient tema'
            },
            dark: {
                name: 'Karanlık Mod',
                icon: 'fas fa-moon',
                description: 'Gece modu'
            },
            reading: {
                name: 'Okuma Modu',
                icon: 'fas fa-book',
                description: 'Göz dostu tema'
            },
            blue: {
                name: 'Mavi',
                icon: 'fas fa-water',
                description: 'Mavi ton'
            },
            green: {
                name: 'Yeşil',
                icon: 'fas fa-leaf',
                description: 'Doğa teması'
            },
            purple: {
                name: 'Mor',
                icon: 'fas fa-gem',
                description: 'Lüks mor tema'
            },
            orange: {
                name: 'Turuncu',
                icon: 'fas fa-sun',
                description: 'Enerjik turuncu'
            }
        };

        this.init();
    }

    init() {
        this.loadSavedTheme();
        this.setupEventListeners();
        this.updateActiveIndicator();
        
        console.log('🎨 Theme Manager initialized with theme:', this.currentTheme);
    }

    setupEventListeners() {
        // Theme option clicks
        this.themeOptions.forEach(option => {
            option.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();

                const theme = option.dataset.theme;
                this.setTheme(theme);
                this.closeDropdown();
            });
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.theme-selector')) {
                this.closeDropdown();
            }
        });

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeDropdown();
            }
        });

        // Listen for system theme changes
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            mediaQuery.addEventListener('change', () => {
                if (this.currentTheme === 'auto') {
                    this.applySystemTheme();
                }
            });
        }
    }

    setTheme(themeName) {
        if (!this.themes[themeName]) {
            console.warn('Unknown theme:', themeName);
            return;
        }

        const oldTheme = this.currentTheme;
        this.currentTheme = themeName;
        
        // Apply theme
        this.applyTheme(themeName);
        
        // Save to storage
        this.saveTheme(themeName);
        
        // Update UI
        this.updateActiveIndicator();
        
        // Emit event
        this.emit('themeChanged', {
            oldTheme,
            newTheme: themeName,
            themeData: this.themes[themeName]
        });

        // Show feedback
        if (window.notificationSystem) {
            window.notificationSystem.success(
                `Tema "${this.themes[themeName].name}" uygulandı`, 
                2000
            );
        }

        console.log('🎨 Theme changed to:', themeName);
    }

    
    




    applyTheme(themeName) {
        // Remove old theme classes
        document.body.className = document.body.className
            .replace(/theme-\w+/g, '')
            .trim();
        
        // Set data attribute
        document.body.setAttribute('data-theme', themeName);
        
        // Add theme class
        document.body.classList.add(`theme-${themeName}`);
        
        // Update meta theme-color
        this.updateMetaThemeColor(themeName);
        
        // ✅ YENİ: Tüm bileşenlere tema değişikliğini bildir
        this.broadcastThemeChange(themeName);
        
        // Animate theme transition
        this.animateThemeTransition();
    }
    
    // ✅ YENİ METOD EKLE:
    broadcastThemeChange(themeName) {
        // Tüm tablolara tema uygula
        const tables = document.querySelectorAll('.table, .modern-table');
        tables.forEach(table => {
            table.style.transition = 'all 0.3s ease';
        });
        
        // Tüm kartlara tema uygula
        const cards = document.querySelectorAll('.card, .team-card, .catalog-card, .settings-card');
        cards.forEach(card => {
            card.style.transition = 'all 0.3s ease';
        });
        
        // Form elementlerine tema uygula
        const formElements = document.querySelectorAll('input, select, textarea');
        formElements.forEach(element => {
            element.style.transition = 'all 0.3s ease';
        });
        
        // Force repaint
        document.body.offsetHeight;
        
        console.log('✅ Theme broadcasted to all components:', themeName);
    }

















    updateMetaThemeColor(themeName) {
        let themeColor = '#667eea'; // default
        
        const colorMap = {
            default: '#667eea',
            dark: '#2d3748',
            reading: '#fef7ed',
            blue: '#3498db',
            green: '#2ecc71',
            purple: '#9b59b6',
            orange: '#e67e22'
        };

        themeColor = colorMap[themeName] || colorMap.default;

        let metaThemeColor = document.querySelector('meta[name=theme-color]');
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        metaThemeColor.content = themeColor;
    }

    animateThemeTransition() {
        document.body.style.transition = 'all 0.3s ease';
        
        setTimeout(() => {
            document.body.style.transition = '';
        }, 300);
    }

    applySystemTheme() {
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            this.applyTheme('dark');
        } else {
            this.applyTheme('default');
        }
    }

    loadSavedTheme() {
        try {
            const savedTheme = localStorage.getItem(this.storageKey);
            if (savedTheme && this.themes[savedTheme]) {
                this.currentTheme = savedTheme;
                this.applyTheme(savedTheme);
            } else {
                // Apply default theme
                this.applyTheme('default');
            }
        } catch (e) {
            console.warn('Could not load saved theme:', e);
            this.applyTheme('default');
        }
    }

    saveTheme(themeName) {
        try {
            localStorage.setItem(this.storageKey, themeName);
        } catch (e) {
            console.warn('Could not save theme:', e);
        }
    }

    updateActiveIndicator() {
        this.themeOptions.forEach(option => {
            option.classList.remove('active');
            if (option.dataset.theme === this.currentTheme) {
                option.classList.add('active');
            }
        });
    }

    closeDropdown() {
        if (this.themeSelector) {
            const dropdown = bootstrap.Dropdown.getOrCreateInstance(this.themeSelector);
            dropdown.hide();
        }
    }

    // Auto theme based on time
    enableAutoTheme() {
        const hour = new Date().getHours();
        let themeToApply;

        if (hour >= 6 && hour < 18) {
            // Day time
            themeToApply = 'default';
        } else if (hour >= 18 && hour < 22) {
            // Evening
            themeToApply = 'reading';
        } else {
            // Night time
            themeToApply = 'dark';
        }

        this.setTheme(themeToApply);
    }

    // Get current theme info
    getCurrentTheme() {
        return {
            name: this.currentTheme,
            data: this.themes[this.currentTheme]
        };
    }

    // Get all available themes
    getAvailableThemes() {
        return this.themes;
    }

    // Theme preview functionality
    previewTheme(themeName, duration = 2000) {
        if (!this.themes[themeName]) return;

        const originalTheme = this.currentTheme;
        this.applyTheme(themeName);

        // Show preview indicator
        this.showPreviewIndicator(themeName, duration);

        setTimeout(() => {
            this.applyTheme(originalTheme);
        }, duration);
    }

    showPreviewIndicator(themeName, duration) {
        const indicator = document.createElement('div');
        indicator.className = 'theme-preview-indicator';
        indicator.innerHTML = `
            <i class="fas fa-eye me-2"></i>
            ${this.themes[themeName].name} temasını önizliyorsunuz
        `;
        indicator.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--primary-gradient);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 25px;
            z-index: 9999;
            font-size: 0.9rem;
            font-weight: 600;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            animation: slideInDown 0.3s ease;
        `;

        document.body.appendChild(indicator);

        setTimeout(() => {
            indicator.style.animation = 'slideOutUp 0.3s ease';
            setTimeout(() => indicator.remove(), 300);
        }, duration - 300);
    }

    // Accessibility features
    enableHighContrast() {
        document.body.classList.add('high-contrast');
        this.savePreference('high-contrast', true);
    }

    disableHighContrast() {
        document.body.classList.remove('high-contrast');
        this.savePreference('high-contrast', false);
    }

    enableReducedMotion() {
        document.body.classList.add('reduced-motion');
        this.savePreference('reduced-motion', true);
    }

    disableReducedMotion() {
        document.body.classList.remove('reduced-motion');
        this.savePreference('reduced-motion', false);
    }

    savePreference(key, value) {
        try {
            localStorage.setItem(`dashboard-${key}`, JSON.stringify(value));
        } catch (e) {
            console.warn('Could not save preference:', e);
        }
    }

    loadPreference(key, defaultValue = false) {
        try {
            const saved = localStorage.getItem(`dashboard-${key}`);
            return saved ? JSON.parse(saved) : defaultValue;
        } catch (e) {
            console.warn('Could not load preference:', e);
            return defaultValue;
        }
    }

    // Event emitter
    emit(eventName, data) {
        const event = new CustomEvent(eventName, {
            detail: data,
            bubbles: true
        });
        document.dispatchEvent(event);
    }

    // Keyboard shortcuts
    enableKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Shift + T = Toggle theme
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'T') {
                e.preventDefault();
                this.toggleTheme();
            }
            
            // Ctrl/Cmd + Shift + D = Toggle dark mode
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
                e.preventDefault();
                this.currentTheme === 'dark' ? this.setTheme('default') : this.setTheme('dark');
            }
        });
    }

    toggleTheme() {
        const themes = Object.keys(this.themes);
        const currentIndex = themes.indexOf(this.currentTheme);
        const nextIndex = (currentIndex + 1) % themes.length;
        this.setTheme(themes[nextIndex]);
    }

    // Public API
    destroy() {
        // Clean up event listeners
        this.themeOptions.forEach(option => {
            option.removeEventListener('click', this.handleThemeClick);
        });
        
        document.removeEventListener('click', this.handleDocumentClick);
        document.removeEventListener('keydown', this.handleKeydown);
    }
}

// CSS for theme manager animations
const themeManagerCSS = `
    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateX(-50%) translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }
    }
    
    @keyframes slideOutUp {
        from {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }
        to {
            opacity: 0;
            transform: translateX(-50%) translateY(-20px);
        }
    }

    .high-contrast {
        filter: contrast(150%) brightness(110%);
    }

    .reduced-motion * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
`;

// Inject CSS
const themeStyle = document.createElement('style');
themeStyle.textContent = themeManagerCSS;
document.head.appendChild(themeStyle);

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.themeManager = new ThemeManager();
    
    // Enable keyboard shortcuts
    window.themeManager.enableKeyboardShortcuts();
    
    // Load accessibility preferences
    if (window.themeManager.loadPreference('high-contrast')) {
        window.themeManager.enableHighContrast();
    }
    
    if (window.themeManager.loadPreference('reduced-motion')) {
        window.themeManager.enableReducedMotion();
    }
    
    // Global access for debugging
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        window.theme = window.themeManager;
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}