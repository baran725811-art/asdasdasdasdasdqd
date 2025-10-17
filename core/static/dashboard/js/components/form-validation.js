// core\static\dashboard\js\components\form-validation.js - Form validasyon 
/**
 * ==========================================================================
 * FORM VALIDATION COMPONENT
 * Reusable form validation utilities for dashboard
 * ==========================================================================
 */

class FormValidator {
    constructor(form, options = {}) {
        this.form = typeof form === 'string' ? document.getElementById(form) : form;
        this.options = {
            validateOnInput: true,
            validateOnBlur: true,
            showSuccessState: true,
            focusFirstError: true,
            submitCallback: null,
            ...options
        };
        
        this.init();
    }
    
    init() {
        if (!this.form) return;
        
        this.setupEventListeners();
        this.setupSubmitHandler();
    }
    
    setupEventListeners() {
        const inputs = this.form.querySelectorAll('.form-control, .form-select, textarea');
        
        inputs.forEach(input => {
            if (this.options.validateOnInput) {
                input.addEventListener('input', () => this.validateField(input));
            }
            
            if (this.options.validateOnBlur) {
                input.addEventListener('blur', () => this.validateField(input));
            }
            
            // Clear validation state on focus
            input.addEventListener('focus', () => this.clearFieldState(input));
        });
    }
    
    setupSubmitHandler() {
        this.form.addEventListener('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
                
                if (this.options.focusFirstError) {
                    this.focusFirstError();
                }
                
                this.showFormError('Lütfen tüm gerekli alanları doğru şekilde doldurun.');
                return false;
            }
            
            if (this.options.submitCallback) {
                this.options.submitCallback(e);
            }
        });
    }
    
    validateField(field) {
        const rules = this.getFieldRules(field);
        // GÜVENLİK: field.value undefined olabilir
        const value = (field.value || '').trim();
        
        for (const rule of rules) {
            const result = this.applyRule(rule, value, field);
            if (!result.valid) {
                this.setFieldError(field, result.message);
                return false;
            }
        }
        
        if (this.options.showSuccessState) {
            this.setFieldSuccess(field);
        } else {
            this.clearFieldState(field);
        }
        
        return true;
    }
    
    validateForm() {
        const fields = this.form.querySelectorAll('.form-control, .form-select, textarea');
        let isValid = true;
        
        fields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    getFieldRules(field) {
        const rules = [];
        
        // Required rule
        if (field.hasAttribute('required') || field.classList.contains('required')) {
            rules.push({ type: 'required' });
        }
        
        // Email rule
        if (field.type === 'email') {
            rules.push({ type: 'email' });
        }
        
        // URL rule
        if (field.type === 'url') {
            rules.push({ type: 'url' });
        }
        
        // Min length
        if (field.hasAttribute('minlength')) {
            rules.push({ 
                type: 'minlength', 
                value: parseInt(field.getAttribute('minlength')) 
            });
        }
        
        // Max length
        if (field.hasAttribute('maxlength')) {
            rules.push({ 
                type: 'maxlength', 
                value: parseInt(field.getAttribute('maxlength')) 
            });
        }
        
        // Pattern
        if (field.hasAttribute('pattern')) {
            rules.push({ 
                type: 'pattern', 
                value: field.getAttribute('pattern') 
            });
        }
        
        // Custom validation
        if (field.hasAttribute('data-validate')) {
            rules.push({ 
                type: 'custom', 
                value: field.getAttribute('data-validate') 
            });
        }
        
        return rules;
    }
    
    applyRule(rule, value, field) {
        // GÜVENLİK: value her zaman string olsun
        const safeValue = String(value || '');
        
        switch (rule.type) {
            case 'required':
                return {
                    valid: safeValue.length > 0,
                    message: 'Bu alan zorunludur.'
                };
                
            case 'email':
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                return {
                    valid: !safeValue || emailRegex.test(safeValue),
                    message: 'Geçerli bir e-posta adresi girin.'
                };
            
            case 'url':
                if (!safeValue) return { valid: true };
                try {
                    new URL(safeValue);
                    return { valid: true };
                } catch {
                    return {
                        valid: false,
                        message: 'Geçerli bir URL girin.'
                    };
                }

            case 'minlength':
                return {
                    valid: !safeValue || safeValue.length >= rule.value,
                    message: `En az ${rule.value} karakter olmalıdır.`
                };

            case 'maxlength':
                return {
                    valid: safeValue.length <= rule.value,
                    message: `En fazla ${rule.value} karakter olmalıdır.`
                };

            case 'pattern':
                const regex = new RegExp(rule.value);
                return {
                    valid: !safeValue || regex.test(safeValue),
                    message: 'Geçerli format değil.'
                };

            case 'custom':
                return this.customValidation(rule.value, safeValue, field);

            default:
                return { valid: true };
        }
    }
    
    customValidation(type, value, field) {
        switch (type) {
            case 'phone':
                const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
                return {
                    valid: !value || phoneRegex.test(value),
                    message: 'Geçerli bir telefon numarası girin.'
                };
                
            case 'password':
                return {
                    valid: !value || (value.length >= 6 && /(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value)),
                    message: 'En az 6 karakter, büyük harf, küçük harf ve rakam içermelidir.'
                };
                
            case 'confirm-password':
                const passwordField = this.form.querySelector('input[type="password"]:not([data-validate="confirm-password"])');
                return {
                    valid: !value || value === passwordField.value,
                    message: 'Parolalar eşleşmiyor.'
                };
                
            case 'turkish-id':
                return {
                    valid: !value || this.validateTurkishId(value),
                    message: 'Geçerli bir TC kimlik numarası girin.'
                };
                
            default:
                return { valid: true };
        }
    }
    
    validateTurkishId(id) {
        if (!/^\d{11}$/.test(id)) return false;
        
        const digits = id.split('').map(Number);
        const checksum = digits[10];
        
        const sum1 = digits[0] + digits[2] + digits[4] + digits[6] + digits[8];
        const sum2 = digits[1] + digits[3] + digits[5] + digits[7];
        
        return ((sum1 * 7 - sum2) % 10) === digits[9] &&
               ((sum1 + sum2 + digits[9]) % 10) === checksum;
    }
    
    setFieldError(field, message) {
        this.clearFieldState(field);
        field.classList.add('is-invalid');
        
        // Create or update error message
        let errorElement = field.parentNode.querySelector('.invalid-feedback');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            field.parentNode.appendChild(errorElement);
        }
        errorElement.textContent = message;
        errorElement.style.display = 'block';
    }
    
    setFieldSuccess(field) {
        this.clearFieldState(field);
        field.classList.add('is-valid');
    }
    
    clearFieldState(field) {
        field.classList.remove('is-invalid', 'is-valid');
        const errorElement = field.parentNode.querySelector('.invalid-feedback');
        if (errorElement) {
            errorElement.style.display = 'none';
        }
    }
    
    focusFirstError() {
        const firstError = this.form.querySelector('.is-invalid');
        if (firstError) {
            firstError.focus();
            firstError.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
        }
    }
    
    showFormError(message) {
        // Remove existing alerts
        const existingAlerts = this.form.querySelectorAll('.form-alert');
        existingAlerts.forEach(alert => alert.remove());
        
        // Create new alert
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger form-alert';
        alert.innerHTML = `
            <i class="fas fa-exclamation-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        
        this.form.insertBefore(alert, this.form.firstChild);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
    
    showFormSuccess(message) {
        // Remove existing alerts
        const existingAlerts = this.form.querySelectorAll('.form-alert');
        existingAlerts.forEach(alert => alert.remove());
        
        // Create success alert
        const alert = document.createElement('div');
        alert.className = 'alert alert-success form-alert';
        alert.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        
        this.form.insertBefore(alert, this.form.firstChild);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 3000);
    }
    
    reset() {
        const fields = this.form.querySelectorAll('.form-control, .form-select, textarea');
        fields.forEach(field => {
            this.clearFieldState(field);
            if (field.type !== 'hidden') {
                field.value = '';
            }
        });
        
        // Remove alerts
        const alerts = this.form.querySelectorAll('.form-alert');
        alerts.forEach(alert => alert.remove());
    }
}

// Character counter utility
class CharacterCounter {
    constructor(input, options = {}) {
        this.input = typeof input === 'string' ? document.getElementById(input) : input;
        this.options = {
            maxLength: this.input.getAttribute('maxlength') || 255,
            warningThreshold: 0.8,
            dangerThreshold: 0.95,
            showRemaining: false,
            ...options
        };
        
        this.init();
    }
    
    init() {
        if (!this.input) return;
        
        this.createCounter();
        this.updateCounter();
        
        this.input.addEventListener('input', () => this.updateCounter());
    }
    
    createCounter() {
        this.counter = document.createElement('div');
        this.counter.className = 'character-counter';
        this.counter.style.cssText = `
            font-size: 0.75rem;
            color: #6c757d;
            margin-top: 0.25rem;
            text-align: right;
        `;
        
        this.input.parentNode.appendChild(this.counter);
    }
    
    updateCounter() {
        const length = this.input.value.length;
        const maxLength = this.options.maxLength;
        const percentage = length / maxLength;
        
        const text = this.options.showRemaining 
            ? `${maxLength - length} karakter kaldı`
            : `${length}/${maxLength}`;
            
        this.counter.textContent = text;
        
        // Update color based on threshold
        if (percentage >= this.options.dangerThreshold) {
            this.counter.style.color = '#dc3545';
            this.counter.classList.add('text-danger');
            this.counter.classList.remove('text-warning');
        } else if (percentage >= this.options.warningThreshold) {
            this.counter.style.color = '#ffc107';
            this.counter.classList.add('text-warning');
            this.counter.classList.remove('text-danger');
        } else {
            this.counter.style.color = '#6c757d';
            this.counter.classList.remove('text-danger', 'text-warning');
        }
    }
}

// Auto-setup for forms with validation
document.addEventListener('DOMContentLoaded', function() {
    // Auto-initialize forms with data-validate attribute
    const formsToValidate = document.querySelectorAll('form[data-validate="true"]');
    formsToValidate.forEach(form => {
        new FormValidator(form);
    });
    
    // Auto-initialize character counters
    const inputsWithMaxLength = document.querySelectorAll('input[maxlength], textarea[maxlength]');
    inputsWithMaxLength.forEach(input => {
        if (input.getAttribute('data-counter') !== 'false') {
            new CharacterCounter(input);
        }
    });
});

// Export for use in other modules
window.FormValidator = FormValidator;
window.CharacterCounter = CharacterCounter;