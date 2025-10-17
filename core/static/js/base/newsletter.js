//# Newsletter fonksiyonları
/**
 * Newsletter Form Handler
 * Handles form submission, validation, and user feedback
 */

class NewsletterForm {
    constructor() {
        this.form = document.getElementById('newsletterForm');
        this.emailInput = document.getElementById('newsletter-email');
        this.submitBtn = this.form?.querySelector('.newsletter-btn');
        this.errorMessage = document.getElementById('email-error');
        this.successMessage = document.getElementById('newsletter-success');
        
        this.isSubmitting = false;
        this.emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        this.init();
    }
    
    init() {
        if (!this.form) return;
        
        this.setupEventListeners();
        this.setupValidation();
        this.setupAccessibility();
    }
    
    /**
     * Setup all event listeners
     */
    setupEventListeners() {
        // Form submission
        this.form.addEventListener('submit', this.handleSubmit.bind(this));
        
        // Real-time validation
        this.emailInput.addEventListener('input', this.handleInput.bind(this));
        this.emailInput.addEventListener('blur', this.handleBlur.bind(this));
        this.emailInput.addEventListener('focus', this.handleFocus.bind(this));
        
        // Prevent double submission
        this.submitBtn.addEventListener('click', this.preventDoubleSubmit.bind(this));
        
        // Clear messages on focus
        this.emailInput.addEventListener('focus', this.clearMessages.bind(this));
    }
    
    /**
     * Handle form submission
     */
    async handleSubmit(e) {
        e.preventDefault();
        
        if (this.isSubmitting) return;
        
        const email = this.emailInput.value.trim();
        
        // Validate email
        if (!this.validateEmail(email)) {
            this.showError('Lütfen geçerli bir e-posta adresi girin.');
            return;
        }
        
        // Start submission
        this.setLoadingState(true);
        
        try {
            const result = await this.submitNewsletter(email);
            
            if (result.success) {
                this.showSuccess('Harika! E-posta listemize başarıyla eklendiz. Teşekkürler!');
                this.resetForm();
                this.trackEvent('newsletter_signup_success', { email });
            } else {
                this.showError(result.message || 'Bir hata oluştu. Lütfen tekrar deneyin.');
                this.trackEvent('newsletter_signup_error', { email, error: result.message });
            }
        } catch (error) {
            console.error('Newsletter submission error:', error);
            this.showError('Bağlantı hatası. Lütfen internet bağlantınızı kontrol edin.');
            this.trackEvent('newsletter_signup_error', { email, error: error.message });
        } finally {
            this.setLoadingState(false);
        }
    }
    
    /**
     * Submit newsletter to backend
     */
    async submitNewsletter(email) {
        // Simulated API call - replace with actual endpoint
        return new Promise((resolve) => {
            setTimeout(() => {
                // Simulate success/failure
                const isSuccess = Math.random() > 0.1; // 90% success rate for demo
                
                if (isSuccess) {
                    resolve({
                        success: true,
                        message: 'E-posta başarıyla kaydedildi.'
                    });
                } else {
                    resolve({
                        success: false,
                        message: 'Bu e-posta adresi zaten kayıtlı.'
                    });
                }
            }, 1500);
        });
        
        /* Real implementation would be:
        const formData = new FormData();
        formData.append('email', email);
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
        
        const response = await fetch('/newsletter/subscribe/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });
        
        return await response.json();
        */
    }
    
    /**
     * Handle input events
     */
    handleInput(e) {
        const email = e.target.value.trim();
        
        // Clear previous messages
        this.clearMessages();
        
        // Real-time validation feedback
        if (email.length > 0) {
            if (this.validateEmail(email)) {
                this.emailInput.classList.remove('invalid');
                this.emailInput.classList.add('valid');
            } else {
                this.emailInput.classList.remove('valid');
                this.emailInput.classList.add('invalid');
            }
        } else {
            this.emailInput.classList.remove('valid', 'invalid');
        }
    }
    
    /**
     * Handle blur events
     */
    handleBlur(e) {
        const email = e.target.value.trim();
        
        if (email.length > 0 && !this.validateEmail(email)) {
            this.showError('Lütfen geçerli bir e-posta adresi girin.');
        }
    }
    
    /**
     * Handle focus events
     */
    handleFocus(e) {
        this.clearMessages();
    }
    
    /**
     * Prevent double submission
     */
    preventDoubleSubmit(e) {
        if (this.isSubmitting) {
            e.preventDefault();
            e.stopPropagation();
        }
    }
    
    /**
     * Validate email address
     */
    validateEmail(email) {
        return this.emailRegex.test(email) && email.length >= 5 && email.length <= 254;
    }
    
    /**
     * Set loading state
     */
    setLoadingState(loading) {
        this.isSubmitting = loading;
        this.submitBtn.classList.toggle('loading', loading);
        this.submitBtn.disabled = loading;
        this.emailInput.disabled = loading;
        
        // Update ARIA states
        this.submitBtn.setAttribute('aria-busy', loading.toString());
        
        if (loading) {
            this.clearMessages();
        }
    }
    
    /**
     * Show error message
     */
    showError(message) {
        this.clearMessages();
        this.errorMessage.textContent = message;
        this.errorMessage.classList.add('show');
        
        // Focus management
        this.errorMessage.focus();
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (this.errorMessage.classList.contains('show')) {
                this.clearMessages();
            }
        }, 5000);
    }
    
    /**
     * Show success message
     */
    showSuccess(message) {
        this.clearMessages();
        this.successMessage.textContent = message;
        this.successMessage.classList.add('show');
        
        // Focus management
        this.successMessage.focus();
        
        // Auto-hide after 8 seconds
        setTimeout(() => {
            if (this.successMessage.classList.contains('show')) {
                this.clearMessages();
            }
        }, 8000);
    }
    
    /**
     * Clear all messages
     */
    clearMessages() {
        this.errorMessage.classList.remove('show');
        this.successMessage.classList.remove('show');
        this.errorMessage.textContent = '';
        this.successMessage.textContent = '';
    }
    
    /**
     * Reset form to initial state
     */
    resetForm() {
        this.emailInput.value = '';
        this.emailInput.classList.remove('valid', 'invalid');
        this.clearMessages();
    }
    
    /**
     * Setup validation
     */
    setupValidation() {
        // HTML5 validation messages
        this.emailInput.addEventListener('invalid', (e) => {
            e.preventDefault();
            
            if (this.emailInput.validity.valueMissing) {
                this.showError('E-posta adresi gereklidir.');
            } else if (this.emailInput.validity.typeMismatch) {
                this.showError('Lütfen geçerli bir e-posta adresi girin.');
            }
        });
    }
    
    /**
     * Setup accessibility features
     */
    setupAccessibility() {
        // ARIA live regions are already in HTML
        
        // Enhanced keyboard navigation
        this.form.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.target === this.emailInput) {
                e.preventDefault();
                this.handleSubmit(e);
            }
        });
        
        // Screen reader announcements
        this.emailInput.setAttribute('aria-describedby', 'email-error newsletter-success');
    }
    
    /**
     * Track events for analytics
     */
    trackEvent(eventName, data = {}) {
        // Google Analytics 4
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, {
                event_category: 'newsletter',
                event_label: 'footer_newsletter',
                ...data
            });
        }
        
        // Custom analytics
        if (window.analytics && typeof window.analytics.track === 'function') {
            window.analytics.track(eventName, {
                source: 'footer_newsletter',
                ...data
            });
        }
        
        // Debug logging
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.log('Newsletter Event:', eventName, data);
        }
    }
    
    /**
     * Get form data for external use
     */
    getFormData() {
        return {
            email: this.emailInput.value.trim(),
            isValid: this.validateEmail(this.emailInput.value.trim()),
            isSubmitting: this.isSubmitting
        };
    }
    
    /**
     * Programmatically submit form
     */
    submitProgrammatically(email) {
        if (this.validateEmail(email)) {
            this.emailInput.value = email;
            this.handleSubmit(new Event('submit'));
        } else {
            this.showError('Geçersiz e-posta adresi.');
        }
    }
    
    /**
     * Destroy newsletter form
     */
    destroy() {
        if (this.form) {
            this.form.removeEventListener('submit', this.handleSubmit);
            this.emailInput.removeEventListener('input', this.handleInput);
            this.emailInput.removeEventListener('blur', this.handleBlur);
            this.emailInput.removeEventListener('focus', this.handleFocus);
            this.submitBtn.removeEventListener('click', this.preventDoubleSubmit);
        }
        
        // Clear any pending timeouts
        clearTimeout(this.errorTimeout);
        clearTimeout(this.successTimeout);
    }
}

/**
 * Global newsletter handler function for external use
 */
window.handleNewsletterSubmit = function(event) {
    if (window.newsletterForm) {
        window.newsletterForm.handleSubmit(event);
    }
    return false;
};

/**
 * Initialize newsletter form when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    window.newsletterForm = new NewsletterForm();
});

/**
 * Re-initialize if content is dynamically loaded
 */
document.addEventListener('contentLoaded', () => {
    if (!window.newsletterForm && document.getElementById('newsletterForm')) {
        window.newsletterForm = new NewsletterForm();
    }
});

/**
 * Cleanup on page unload
 */
window.addEventListener('beforeunload', () => {
    if (window.newsletterForm) {
        window.newsletterForm.destroy();
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NewsletterForm;
}