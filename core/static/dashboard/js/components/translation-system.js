// core\static\dashboard\js\components\translation-system.js - Çeviri sistemi
/**
 * ========================================
 * TRANSLATION SYSTEM COMPONENT
 * Multi-language form management, progress tracking
 * ========================================
 */

class TranslationSystem {
    constructor(options = {}) {
        this.options = {
            enabledLanguages: ['tr', 'en'],
            primaryLanguage: 'tr',
            translationEnabled: false,
            requiredFields: [],
            autoSave: false,
            showProgress: true,
            ...options
        };
        
        this.currentLanguage = this.options.primaryLanguage;
        this.translationStats = {};
        this.completionData = {};
        this.isInitialized = false;
        
        this.init();
    }

    init() {
        if (!this.options.translationEnabled || this.options.enabledLanguages.length <= 1) {
            console.log('Translation system disabled or insufficient languages');
            return;
        }

        this.setupTranslationTabs();
        this.setupEventListeners();
        this.initializeTranslationStats();
        this.setupFormValidation();
        
        if (this.options.showProgress) {
            this.createProgressTracker();
        }

        this.isInitialized = true;
        console.log('🌍 Translation System initialized for languages:', this.options.enabledLanguages);
    }

    setupTranslationTabs() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            this.processForm(form);
        });
    }

    processForm(form) {
        // Find translation containers
        const translationContainers = form.querySelectorAll('[data-translation-container]');
        
        translationContainers.forEach(container => {
            this.createTranslationInterface(container);
        });

        // Process existing translation tabs
        const existingTabs = form.querySelectorAll('.translation-tab');
        const existingContents = form.querySelectorAll('.translation-content');
        
        if (existingTabs.length > 0) {
            this.enhanceExistingTabs(existingTabs, existingContents);
        }
    }

    createTranslationInterface(container) {
        const fieldName = container.dataset.translationContainer;
        const tabsHTML = this.generateTabsHTML(fieldName);
        const contentsHTML = this.generateContentsHTML(fieldName, container);
        
        container.innerHTML = tabsHTML + contentsHTML;
        
        // Setup tab functionality
        this.setupTabEvents(container);
    }

    generateTabsHTML(fieldName) {
        const tabs = this.options.enabledLanguages.map((lang, index) => {
            const isActive = index === 0 ? 'active' : '';
            const langName = this.getLanguageName(lang);
            const flag = this.getLanguageFlag(lang);
            
            return `
                <button type="button" class="translation-tab ${isActive}" data-lang="${lang}" data-field="${fieldName}">
                    <span class="language-flag">${flag}</span>
                    ${langName}
                    <span class="translation-indicator ${lang === this.options.primaryLanguage ? 'complete' : 'required'}" id="indicator-${fieldName}-${lang}"></span>
                </button>
            `;
        }).join('');
        
        return `<div class="translation-tabs" data-field="${fieldName}">${tabs}</div>`;
    }

    generateContentsHTML(fieldName, container) {
        const originalContent = container.innerHTML;
        
        return this.options.enabledLanguages.map((lang, index) => {
            const isActive = index === 0 ? 'active' : '';
            const isRequired = lang !== this.options.primaryLanguage;
            const content = index === 0 ? originalContent : this.generateTranslationFields(fieldName, lang);
            
            return `
                <div class="translation-content ${isActive}" data-lang="${lang}" data-field="${fieldName}">
                    ${content}
                </div>
            `;
        }).join('');
    }

    generateTranslationFields(fieldName, lang) {
        // This should be customized based on your field requirements
        return `
            <div class="form-group">
                <label class="form-label required" for="${fieldName}_${lang}">
                    ${this.getFieldLabel(fieldName)} (${this.getLanguageName(lang)})
                </label>
                <input type="text" class="form-control required-translation" 
                       id="${fieldName}_${lang}" name="${fieldName}_${lang}" 
                       placeholder="${this.getFieldPlaceholder(fieldName, lang)}">
                <div class="invalid-feedback"></div>
            </div>
        `;
    }

    enhanceExistingTabs(tabs, contents) {
        // Set up existing tab functionality
        tabs.forEach((tab, index) => {
            tab.addEventListener('click', () => {
                this.switchToLanguage(tab.dataset.lang, tabs, contents);
            });
            
            // Add indicators if missing
            if (!tab.querySelector('.translation-indicator')) {
                const indicator = document.createElement('span');
                indicator.className = 'translation-indicator required';
                indicator.id = `indicator-${tab.dataset.lang}-${index}`;
                tab.appendChild(indicator);
            }
        });

        // Setup content monitoring
        contents.forEach(content => {
            this.setupContentMonitoring(content);
        });
    }

    setupTabEvents(container) {
        const tabs = container.querySelectorAll('.translation-tab');
        const contents = container.querySelectorAll('.translation-content');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                this.switchToLanguage(tab.dataset.lang, tabs, contents);
            });
        });
        
        contents.forEach(content => {
            this.setupContentMonitoring(content);
        });
    }

    switchToLanguage(targetLang, tabs, contents) {
        // Update tabs
        tabs.forEach(tab => {
            tab.classList.toggle('active', tab.dataset.lang === targetLang);
        });
        
        // Update contents
        contents.forEach(content => {
            content.classList.toggle('active', content.dataset.lang === targetLang);
        });
        
        this.currentLanguage = targetLang;
        this.emit('languageChanged', { language: targetLang });
        
        // Focus first input in active content
        const activeContent = Array.from(contents).find(c => c.classList.contains('active'));
        if (activeContent) {
            const firstInput = activeContent.querySelector('input, textarea');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
        }
    }

    setupContentMonitoring(content) {
        const inputs = content.querySelectorAll('input, textarea');
        
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                this.updateTranslationStatus(content.dataset.lang);
                this.updateProgressTracker();
            });
            
            input.addEventListener('blur', () => {
                this.validateTranslationField(input);
            });
        });
    }

    setupEventListeners() {
        // Form submission validation
        document.addEventListener('submit', (e) => {
            if (this.hasTranslationTabs(e.target)) {
                if (!this.validateAllTranslations(e.target)) {
                    e.preventDefault();
                }
            }
        });

        // Auto-save if enabled
        if (this.options.autoSave) {
            document.addEventListener('input', (e) => {
                if (e.target.matches('.required-translation')) {
                    this.debounce(this.autoSave.bind(this), 1000)();
                }
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.shiftKey) {
                const langIndex = parseInt(e.key) - 1;
                if (langIndex >= 0 && langIndex < this.options.enabledLanguages.length) {
                    e.preventDefault();
                    this.switchToLanguageIndex(langIndex);
                }
            }
        });
    }

    setupFormValidation() {
        // Add custom validation rules for translation fields
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateTranslations(form)) {
                    e.preventDefault();
                    this.showValidationErrors();
                }
            });
        });
    }

    validateTranslations(form) {
        let isValid = true;
        const missingTranslations = [];

        this.options.enabledLanguages.forEach(lang => {
            if (lang !== this.options.primaryLanguage) {
                const requiredFields = form.querySelectorAll(`[name$="_${lang}"][required], .required-translation[name$="_${lang}"]`);

                requiredFields.forEach(field => {
                    // GÜVENLİK: field.value undefined olabilir
                    const fieldValue = field.value || '';
                    if (!fieldValue.trim()) {
                        field.classList.add('is-invalid');
                        missingTranslations.push(field.name);
                        isValid = false;
                    } else {
                        field.classList.remove('is-invalid');
                        field.classList.add('is-valid');
                    }
                });
            }
        });

        if (missingTranslations.length > 0) {
            this.showMissingTranslationsAlert(missingTranslations);
        }

        return isValid;
    }

    validateTranslationField(field) {
        // GÜVENLİK: field.value undefined olabilir
        const value = (field.value || '').trim();

        if (field.classList.contains('required-translation') && !value) {
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

    updateTranslationStatus(language) {
        const fields = document.querySelectorAll(`[name$="_${language}"][required], .required-translation[name$="_${language}"]`);
        const completedFields = Array.from(fields).filter(field => {
            // GÜVENLİK: field.value undefined olabilir
            const fieldValue = field.value || '';
            return fieldValue.trim();
        });
        
        const completionRate = fields.length > 0 ? (completedFields.length / fields.length) * 100 : 100;
        
        this.translationStats[language] = {
            total: fields.length,
            completed: completedFields.length,
            completionRate: completionRate
        };
    
        this.updateLanguageIndicators(language, completionRate);
        this.emit('translationStatusChanged', { language, stats: this.translationStats[language] });
    }
    updateLanguageIndicators(language, completionRate) {
        const indicators = document.querySelectorAll(`[id*="indicator"][id*="${language}"]`);
        
        indicators.forEach(indicator => {
            indicator.className = 'translation-indicator';
            
            if (completionRate === 100) {
                indicator.classList.add('complete');
            } else if (completionRate > 0) {
                indicator.classList.add('partial');
            } else {
                indicator.classList.add('required');
            }
        });
    }

    createProgressTracker() {
        const tracker = document.createElement('div');
        tracker.className = 'translation-completion';
        tracker.id = 'translationCompletion';
        
        tracker.innerHTML = `
            <div class="translation-completion-header">
                <h6 class="translation-completion-title">Çeviri Durumu</h6>
                <button class="translation-completion-close" onclick="this.parentElement.parentElement.classList.remove('show')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="translation-completion-content" id="translationCompletionContent">
                <!-- Content will be updated dynamically -->
            </div>
        `;
        
        document.body.appendChild(tracker);
        this.updateProgressTracker();
    }

    updateProgressTracker() {
        const tracker = document.getElementById('translationCompletion');
        const content = document.getElementById('translationCompletionContent');
        
        if (!tracker || !content) return;

        let html = '';
        let totalCompletion = 0;
        let languageCount = 0;

        this.options.enabledLanguages.forEach(lang => {
            if (lang !== this.options.primaryLanguage) {
                this.updateTranslationStatus(lang);
                const stats = this.translationStats[lang] || { completionRate: 0, completed: 0, total: 0 };
                
                html += `
                    <div class="translation-stat-item">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <span class="language-flag">${this.getLanguageFlag(lang)}</span>
                            <span class="translation-status-badge ${this.getStatusClass(stats.completionRate)}">
                                ${Math.round(stats.completionRate)}%
                            </span>
                        </div>
                        <div class="translation-progress">
                            <div class="translation-progress-bar">
                                <div class="translation-progress-fill ${this.getStatusClass(stats.completionRate)}" 
                                     style="width: ${stats.completionRate}%"></div>
                            </div>
                            <div class="translation-progress-text">
                                ${stats.completed}/${stats.total} alan
                            </div>
                        </div>
                    </div>
                `;
                
                totalCompletion += stats.completionRate;
                languageCount++;
            }
        });

        content.innerHTML = html;

        // Show tracker if there are incomplete translations
        const avgCompletion = languageCount > 0 ? totalCompletion / languageCount : 100;
        if (avgCompletion < 100 && avgCompletion > 0) {
            tracker.classList.add('show');
        } else {
            tracker.classList.remove('show');
        }
    }

    showMissingTranslationsAlert(missingFields) {
        // Remove existing alert
        const existingAlert = document.querySelector('.missing-translations-alert');
        if (existingAlert) {
            existingAlert.remove();
        }

        const alert = document.createElement('div');
        alert.className = 'missing-translations-alert';
        alert.innerHTML = `
            <h6 class="mb-2"><strong>Eksik Çeviriler</strong></h6>
            <p class="mb-2">Seçtiğiniz diller için aşağıdaki alanların çevirileri eksik:</p>
            <ul class="missing-translations-list">
                ${missingFields.map(field => `<li>${this.getFieldDisplayName(field)}</li>`).join('')}
            </ul>
        `;

        // Insert before first form
        const firstForm = document.querySelector('form');
        if (firstForm) {
            firstForm.parentNode.insertBefore(alert, firstForm);
            alert.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    // Auto-save functionality
    autoSave() {
        const form = document.querySelector('form');
        if (!form) return;

        const formData = new FormData(form);
        formData.append('auto_save', 'true');

        fetch(form.action || window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': window.dashboardUtils.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.showAutoSaveIndicator();
            }
        })
        .catch(error => {
            console.error('Auto-save error:', error);
        });
    }

    showAutoSaveIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'auto-save-indicator';
        indicator.innerHTML = '<i class="fas fa-check text-success"></i> Otomatik kaydedildi';
        indicator.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: var(--success-color);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            z-index: 9999;
            animation: slideInUp 0.3s ease;
        `;

        document.body.appendChild(indicator);

        setTimeout(() => {
            indicator.style.animation = 'slideOutDown 0.3s ease';
            setTimeout(() => indicator.remove(), 300);
        }, 2000);
    }

    // Language switching methods
    switchToLanguageIndex(index) {
        if (index >= 0 && index < this.options.enabledLanguages.length) {
            const targetLang = this.options.enabledLanguages[index];
            const tabs = document.querySelectorAll('.translation-tab');
            const contents = document.querySelectorAll('.translation-content');
            
            this.switchToLanguage(targetLang, tabs, contents);
        }
    }

    switchToLanguageByCode(langCode) {
        const tabs = document.querySelectorAll('.translation-tab');
        const contents = document.querySelectorAll('.translation-content');
        
        this.switchToLanguage(langCode, tabs, contents);
    }

    // Utility methods
    getLanguageName(code) {
        const names = {
            'tr': 'Türkçe',
            'en': 'English',
            'de': 'Deutsch',
            'fr': 'Français',
            'es': 'Español',
            'ru': 'Русский',
            'ar': 'العربية'
        };
        return names[code] || code.toUpperCase();
    }

    getLanguageFlag(code) {
        const flags = {
            'tr': '🇹🇷',
            'en': '🇺🇸',
            'de': '🇩🇪',
            'fr': '🇫🇷',
            'es': '🇪🇸',
            'ru': '🇷🇺',
            'ar': '🇸🇦'
        };
        return flags[code] || '🌐';
    }

    getStatusClass(completionRate) {
        if (completionRate >= 100) return 'success';
        if (completionRate >= 50) return 'warning';
        return 'danger';
    }

    getFieldLabel(fieldName) {
        const labels = {
            'title': 'Başlık',
            'description': 'Açıklama',
            'content': 'İçerik',
            'summary': 'Özet',
            'name': 'Ad',
            'short_description': 'Kısa Açıklama'
        };
        return labels[fieldName] || fieldName;
    }

    getFieldPlaceholder(fieldName, lang) {
        const langName = this.getLanguageName(lang);
        return `${this.getFieldLabel(fieldName)} (${langName})`;
    }

    getFieldDisplayName(fieldWithLang) {
        const parts = fieldWithLang.split('_');
        const lang = parts.pop();
        const field = parts.join('_');
        return `${this.getFieldLabel(field)} (${this.getLanguageName(lang)})`;
    }

    hasTranslationTabs(form) {
        return form.querySelector('.translation-tab') !== null;
    }

    validateAllTranslations(form) {
        return this.validateTranslations(form);
    }

    showValidationErrors() {
        const firstInvalidField = document.querySelector('.is-invalid');
        if (firstInvalidField) {
            firstInvalidField.focus();
            firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    initializeTranslationStats() {
        this.options.enabledLanguages.forEach(lang => {
            if (lang !== this.options.primaryLanguage) {
                this.updateTranslationStatus(lang);
            }
        });
    }

    // Event emitter
    emit(eventName, data) {
        const event = new CustomEvent(eventName, {
            detail: data,
            bubbles: true
        });
        document.dispatchEvent(event);
    }

    // Utility: debounce function
    debounce(func, wait) {
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

    // Public API
    getCurrentLanguage() {
        return this.currentLanguage;
    }

    getTranslationStats() {
        return this.translationStats;
    }

    getCompletionRate() {
        const rates = Object.values(this.translationStats).map(stat => stat.completionRate);
        return rates.length > 0 ? rates.reduce((a, b) => a + b, 0) / rates.length : 0;
    }

    isTranslationComplete(language) {
        const stats = this.translationStats[language];
        return stats ? stats.completionRate === 100 : false;
    }

    destroy() {
        const tracker = document.getElementById('translationCompletion');
        if (tracker) {
            tracker.remove();
        }
        
        const alerts = document.querySelectorAll('.missing-translations-alert');
        alerts.forEach(alert => alert.remove());
    }
}

// CSS for auto-save indicator
const translationSystemCSS = `
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideOutDown {
        from {
            opacity: 1;
            transform: translateY(0);
        }
        to {
            opacity: 0;
            transform: translateY(20px);
        }
    }
    
    .auto-save-indicator {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
`;


// Inject CSS
const translationStyles = document.createElement('style');
translationStyles.textContent = translationSystemCSS;
document.head.appendChild(translationStyles);

// Global initialization
document.addEventListener('DOMContentLoaded', function() {
    // Check if translation is enabled via meta tags or global variables
    const translationEnabled = document.querySelector('meta[name="translation-enabled"]')?.content === 'true' ||
                              window.translation_enabled === true;
    
    const enabledLanguages = JSON.parse(document.querySelector('meta[name="enabled-languages"]')?.content || '["tr"]');
    const primaryLanguage = document.querySelector('meta[name="primary-language"]')?.content || 'tr';
    
    if (translationEnabled && enabledLanguages.length > 1) {
        window.translationSystem = new TranslationSystem({
            translationEnabled: translationEnabled,
            enabledLanguages: enabledLanguages,
            primaryLanguage: primaryLanguage,
            autoSave: false,
            showProgress: true
        });
        
        // Global access for debugging
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            window.translation = window.translationSystem;
        }
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TranslationSystem;
}