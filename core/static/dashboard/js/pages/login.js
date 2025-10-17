//Login işlemleri
/**
 * ==========================================================================
 * LOGIN PAGE JAVASCRIPT
 * Login form functionality and security features
 * ==========================================================================
 */

class LoginManager {
    constructor() {
        this.maxAttempts = 5;
        this.lockoutDuration = 15 * 60 * 1000; // 15 minutes
        this.form = null;
        this.usernameInput = null;
        this.passwordInput = null;
        this.loginBtn = null;
        this.init();
    }
    
    init() {
        console.log('🔐 Login Manager initializing...');
        
        this.initializeElements();
        this.setupFormValidation();
        this.setupPasswordToggle();
        this.setupFormSubmission();
        this.setupKeyboardNavigation();
        this.setupSecurityFeatures();
        this.setupAnimations();
        this.checkLockoutStatus();
        
        // Focus first input
        if (this.usernameInput) {
            this.usernameInput.focus();
        }
        
        console.log('✅ Login Manager initialized successfully');
    }
    
    initializeElements() {
        this.form = document.getElementById('loginForm');
        this.usernameInput = document.getElementById('username');
        this.passwordInput = document.getElementById('password');
        this.loginBtn = document.getElementById('loginBtn');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        this.btnText = document.getElementById('btnText');
    }
    
    setupFormValidation() {
        if (!this.form) return;
        
        // Real-time validation
        [this.usernameInput, this.passwordInput].forEach(input => {
            if (!input) return;
            
            input.addEventListener('input', () => this.validateField(input));
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('focus', () => this.clearFieldError(input));
        });
        
        // Form submission validation
        this.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
    }
    
    validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        let message = '';
        
        // Required validation
        if (value === '') {
            isValid = false;
            message = field === this.usernameInput ? 'Kullanıcı adı gereklidir' : 'Parola gereklidir';
        }
        
        // Username specific validation
        if (field === this.usernameInput && value) {
            if (value.length < 3) {
                isValid = false;
                message = 'Kullanıcı adı en az 3 karakter olmalıdır';
            }
        }
        
        // Password specific validation
        if (field === this.passwordInput && value) {
            if (value.length < 6) {
                isValid = false;
                message = 'Parola en az 6 karakter olmalıdır';
            }
        }
        
        // Update field state
        if (isValid) {
            this.setFieldValid(field);
        } else {
            this.setFieldError(field, message);
        }
        
        return isValid;
    }
    
    setFieldValid(field) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        this.clearFieldError(field);
    }
    
    setFieldError(field, message) {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');
        
        // Create or update error message
        let errorElement = field.parentNode.querySelector('.field-error');
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'field-error';
            errorElement.style.cssText = `
                color: #dc3545;
                font-size: 0.875rem;
                margin-top: 0.25rem;
                display: flex;
                align-items: center;
                gap: 0.25rem;
            `;
            field.parentNode.appendChild(errorElement);
        }
        errorElement.innerHTML = `<i class="fas fa-exclamation-circle"></i>${message}`;
    }
    
    clearFieldError(field) {
        const errorElement = field.parentNode.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }
    }
    
    setupPasswordToggle() {
        // Create password toggle button if it doesn't exist
        let toggleBtn = document.getElementById('passwordToggle');
        
        if (!toggleBtn && this.passwordInput) {
            toggleBtn = document.createElement('button');
            toggleBtn.type = 'button';
            toggleBtn.className = 'password-toggle';
            toggleBtn.innerHTML = '<i class="fas fa-eye" id="passwordToggleIcon"></i>';
            toggleBtn.setAttribute('aria-label', 'Parolayı göster/gizle');
            
            this.passwordInput.parentNode.appendChild(toggleBtn);
        }
        
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.togglePassword());
        }
    }
    
    togglePassword() {
        const toggleIcon = document.getElementById('passwordToggleIcon');
        
        if (this.passwordInput.type === 'password') {
            this.passwordInput.type = 'text';
            if (toggleIcon) {
                toggleIcon.classList.remove('fa-eye');
                toggleIcon.classList.add('fa-eye-slash');
            }
        } else {
            this.passwordInput.type = 'password';
            if (toggleIcon) {
                toggleIcon.classList.remove('fa-eye-slash');
                toggleIcon.classList.add('fa-eye');
            }
        }
    }
    
    setupFormSubmission() {
        if (!this.form) return;
        
        this.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
    }
    
    handleFormSubmit(e) {
        // Check if user is locked out
        if (this.isLockedOut()) {
            e.preventDefault();
            this.showLockoutMessage();
            return false;
        }
        
        // Validate all fields
        const isUsernameValid = this.validateField(this.usernameInput);
        const isPasswordValid = this.validateField(this.passwordInput);
        
        if (!isUsernameValid || !isPasswordValid) {
            e.preventDefault();
            
            // Focus first invalid field
            const firstInvalid = this.form.querySelector('.is-invalid');
            if (firstInvalid) {
                firstInvalid.focus();
            }
            
            this.showFormError('Lütfen tüm alanları doğru şekilde doldurun.');
            return false;
        }
        
        // Show loading state
        this.setLoadingState(true);
        
        // Track login attempt
        this.trackLoginAttempt();
        
        // Form will be submitted normally
        // Server-side will handle the actual authentication
        
        return true;
    }
    
    setLoadingState(isLoading) {
        if (!this.loginBtn) return;
        
        if (isLoading) {
            this.loginBtn.disabled = true;
            if (this.loadingSpinner) {
                this.loadingSpinner.style.display = 'inline-block';
            }
            if (this.btnText) {
                this.btnText.textContent = 'Giriş yapılıyor...';
            }
        } else {
            this.loginBtn.disabled = false;
            if (this.loadingSpinner) {
                this.loadingSpinner.style.display = 'none';
            }
            if (this.btnText) {
                this.btnText.textContent = 'Giriş Yap';
            }
        }
    }
    
    setupKeyboardNavigation() {
        // Enter key support
        document.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && this.form) {
                e.preventDefault();
                this.form.dispatchEvent(new Event('submit', { bubbles: true }));
            }
        });
        
        // Tab navigation improvement
        [this.usernameInput, this.passwordInput, this.loginBtn].forEach((element, index, arr) => {
            if (!element) return;
            
            element.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    // Custom tab handling if needed
                }
            });
        });
    }
    
    setupSecurityFeatures() {
        // Login attempt tracking
        this.initializeAttemptTracking();
        
        // Basic security measures (optional - can be enabled/disabled)
        this.setupBasicSecurity();
        
        // Form tampering detection
        this.setupFormProtection();
    }
    
    initializeAttemptTracking() {
        // Get current attempts from localStorage
        const attempts = this.getLoginAttempts();
        const lastAttempt = this.getLastAttemptTime();
        
        // Reset attempts if enough time has passed
        if (lastAttempt && (Date.now() - lastAttempt) > this.lockoutDuration) {
            this.clearLoginAttempts();
        }
        
        // Show warning if close to lockout
        if (attempts >= this.maxAttempts - 2) {
            this.showAttemptWarning(attempts);
        }
    }
    
    trackLoginAttempt() {
        const attempts = this.getLoginAttempts() + 1;
        localStorage.setItem('loginAttempts', attempts.toString());
        localStorage.setItem('lastAttemptTime', Date.now().toString());
        
        console.log(`Login attempt ${attempts} tracked`);
    }
    
    getLoginAttempts() {
        return parseInt(localStorage.getItem('loginAttempts') || '0');
    }
    
    getLastAttemptTime() {
        return parseInt(localStorage.getItem('lastAttemptTime') || '0');
    }
    
    clearLoginAttempts() {
        localStorage.removeItem('loginAttempts');
        localStorage.removeItem('lastAttemptTime');
    }
    
    isLockedOut() {
        const attempts = this.getLoginAttempts();
        const lastAttempt = this.getLastAttemptTime();
        
        if (attempts >= this.maxAttempts && lastAttempt) {
            const timePassed = Date.now() - lastAttempt;
            return timePassed < this.lockoutDuration;
        }
        
        return false;
    }
    
    checkLockoutStatus() {
        if (this.isLockedOut()) {
            this.showLockoutMessage();
            this.disableForm();
        }
    }
    
    showLockoutMessage() {
        const lastAttempt = this.getLastAttemptTime();
        const timeRemaining = this.lockoutDuration - (Date.now() - lastAttempt);
        const minutesRemaining = Math.ceil(timeRemaining / (60 * 1000));
        
        this.showFormError(
            `Çok fazla başarısız giriş denemesi yaptınız. ${minutesRemaining} dakika sonra tekrar deneyebilirsiniz.`,
            'warning'
        );
    }
    
    showAttemptWarning(attempts) {
        const remaining = this.maxAttempts - attempts;
        this.showFormError(
            `Dikkat: ${remaining} başarısız deneme hakkınız kaldı.`,
            'warning'
        );
    }
    
    disableForm() {
        if (this.usernameInput) this.usernameInput.disabled = true;
        if (this.passwordInput) this.passwordInput.disabled = true;
        if (this.loginBtn) this.loginBtn.disabled = true;
    }
    
    enableForm() {
        if (this.usernameInput) this.usernameInput.disabled = false;
        if (this.passwordInput) this.passwordInput.disabled = false;
        if (this.loginBtn) this.loginBtn.disabled = false;
    }
    
    setupBasicSecurity() {
        // Disable context menu (optional)
        // document.addEventListener('contextmenu', (e) => e.preventDefault());
        
        // Disable certain key combinations (optional)
        document.addEventListener('keydown', (e) => {
            // Disable F12, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+U
            if (e.keyCode === 123 || 
                (e.ctrlKey && e.shiftKey && e.keyCode === 73) || 
                (e.ctrlKey && e.shiftKey && e.keyCode === 74) || 
                (e.ctrlKey && e.keyCode === 85)) {
                // e.preventDefault(); // Uncomment if needed
            }
        });
    }
    
    setupFormProtection() {
        // Detect form tampering
        if (this.form) {
            const originalAction = this.form.action;
            const originalMethod = this.form.method;
            
            // Check for form modifications
            setInterval(() => {
                if (this.form.action !== originalAction || this.form.method !== originalMethod) {
                    console.warn('Form tampering detected');
                    this.showFormError('Güvenlik hatası: Form değiştirildi.', 'danger');
                    this.disableForm();
                }
            }, 1000);
        }
    }
    
    setupAnimations() {
        // Auto-hide error messages
        const alerts = document.querySelectorAll('.alert-modern');
        alerts.forEach(alert => {
            setTimeout(() => {
                alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-20px)';
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 500);
            }, 5000);
        });
        
        // Add floating label effect
        const inputs = document.querySelectorAll('.form-control-modern');
        inputs.forEach(input => {
            input.addEventListener('focus', () => {
                input.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', () => {
                if (input.value === '') {
                    input.parentElement.classList.remove('focused');
                }
            });
            
            // Check if input has value on load
            if (input.value !== '') {
                input.parentElement.classList.add('focused');
            }
        });
        
        // Add ripple effect to login button
        if (this.loginBtn) {
            this.loginBtn.addEventListener('click', (e) => this.addRippleEffect(e));
        }
    }
    
    addRippleEffect(e) {
        const button = e.currentTarget;
        const ripple = document.createElement('span');
        const rect = button.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');
        
        button.appendChild(ripple);
        
        setTimeout(() => {
            if (ripple.parentNode) {
                ripple.remove();
            }
        }, 600);
    }
    
    showFormError(message, type = 'danger') {
        // Remove existing error alerts
        const existingAlerts = this.form.querySelectorAll('.form-alert');
        existingAlerts.forEach(alert => alert.remove());
        
        // Create new alert
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} form-alert`;
        alert.style.marginBottom = '1.5rem';
        
        const icon = type === 'danger' ? 'exclamation-circle' : 
                    type === 'warning' ? 'exclamation-triangle' : 'info-circle';
        
        alert.innerHTML = `
            <i class="fas fa-${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        
        this.form.insertBefore(alert, this.form.firstChild);
        
        // Auto-remove after 10 seconds for warnings/errors
        if (type !== 'success') {
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 10000);
        }
    }
    
    showFormSuccess(message) {
        this.showFormError(message, 'success');
    }
    
    // Public methods
    resetForm() {
        if (this.usernameInput) this.usernameInput.value = '';
        if (this.passwordInput) this.passwordInput.value = '';
        
        // Clear validation states
        [this.usernameInput, this.passwordInput].forEach(input => {
            if (input) {
                input.classList.remove('is-valid', 'is-invalid');
                this.clearFieldError(input);
            }
        });
        
        // Clear loading state
        this.setLoadingState(false);
        
        // Focus username
        if (this.usernameInput) {
            this.usernameInput.focus();
        }
    }
    
    unlockForm() {
        this.clearLoginAttempts();
        this.enableForm();
        
        // Remove any lockout messages
        const alerts = this.form.querySelectorAll('.alert');
        alerts.forEach(alert => alert.remove());
        
        this.showFormSuccess('Giriş formu sıfırlandı. Tekrar deneyebilirsiniz.');
    }
}

// Utility functions
const LoginUtils = {
    // Check password strength
    checkPasswordStrength(password) {
        let strength = 0;
        let feedback = [];
        
        if (password.length >= 8) strength++;
        else feedback.push('En az 8 karakter');
        
        if (/[a-z]/.test(password)) strength++;
        else feedback.push('Küçük harf');
        
        if (/[A-Z]/.test(password)) strength++;
        else feedback.push('Büyük harf');
        
        if (/[0-9]/.test(password)) strength++;
        else feedback.push('Rakam');
        
        if (/[^A-Za-z0-9]/.test(password)) strength++;
        else feedback.push('Özel karakter');
        
        const levels = ['Çok Zayıf', 'Zayıf', 'Orta', 'İyi', 'Güçlü'];
        
        return {
            score: strength,
            level: levels[strength] || 'Çok Zayıf',
            feedback: feedback
        };
    },
    
    // Generate secure password
    generateSecurePassword(length = 12) {
        const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*';
        let password = '';
        
        for (let i = 0; i < length; i++) {
            password += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        
        return password;
    },
    
    // Validate email format
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
};

// Initialize login manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize on login page
    if (document.querySelector('.login-page, .login-form, #loginForm')) {
        window.loginManager = new LoginManager();
    }
});

// Handle successful login (if needed)
window.addEventListener('beforeunload', function() {
    // Clear login attempts on successful navigation
    if (window.loginManager && document.querySelector('.dashboard-page')) {
        window.loginManager.clearLoginAttempts();
    }
});

// Export for global use
window.LoginManager = LoginManager;
window.LoginUtils = LoginUtils;