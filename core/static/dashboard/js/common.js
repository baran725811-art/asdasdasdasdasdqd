// core\static\dashboard\js\common.js - Ortak JS fonksiyonlar
/**
 * ========================================
 * DASHBOARD COMMON JAVASCRIPT
 * Ortak JavaScript fonksiyonları ve utilities
 * ========================================
 */

// CSRF Token yönetimi
window.dashboardUtils = {
    /**
     * CSRF Token al
     */
    getCSRFToken: function() {
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        const csrfMeta = document.querySelector('[name=csrf-token]');
        
        if (csrfInput) return csrfInput.value;
        if (csrfMeta) return csrfMeta.getAttribute('content');
        
        console.warn('CSRF token bulunamadı!');
        return null;
    },

    /**
     * API Request wrapper
     */
    apiRequest: async function(url, options = {}) {
        const defaultOptions = {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': this.getCSRFToken(),
                ...options.headers
            }
        };

        const finalOptions = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, finalOptions);
            return response;
        } catch (error) {
            console.error('API Request Error:', error);
            throw error;
        }
    },

    /**
     * Form data ile POST request
     */
    submitForm: async function(form, url = null) {
        const formData = new FormData(form);
        const submitUrl = url || form.action || window.location.href;
        
        return this.apiRequest(submitUrl, {
            method: 'POST',
            body: formData
        });
    },

    /**
     * JSON POST request
     */
    postJSON: async function(url, data) {
        return this.apiRequest(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
    },

    /**
     * GET request
     */
    get: async function(url) {
        return this.apiRequest(url, {
            method: 'GET'
        });
    }
};

// Notification System
window.notificationSystem = {
    /**
     * Bildirim göster
     */
    show: function(message, type = 'info', duration = 3000) {
        // Mevcut notification'ları temizle
        this.clearAll();
        
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed notification-toast`;
        notification.style.cssText = `
            top: 20px; 
            right: 20px; 
            z-index: 9999; 
            min-width: 300px;
            max-width: 500px;
            animation: slideInRight 0.5s ease;
        `;
        
        const iconMap = {
            success: 'fas fa-check-circle',
            danger: 'fas fa-exclamation-triangle',
            warning: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle',
            error: 'fas fa-times-circle'
        };
        
        notification.innerHTML = `
            <i class="${iconMap[type] || iconMap.info} me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;

        document.body.appendChild(notification);

        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.style.animation = 'slideOutRight 0.5s ease';
                    setTimeout(() => notification.remove(), 500);
                }
            }, duration);
        }

        return notification;
    },

    /**
     * Tüm notification'ları temizle
     */
    clearAll: function() {
        const notifications = document.querySelectorAll('.notification-toast');
        notifications.forEach(n => n.remove());
    },

    /**
     * Başarı mesajı
     */
    success: function(message, duration = 3000) {
        return this.show(message, 'success', duration);
    },

    /**
     * Hata mesajı
     */
    error: function(message, duration = 5000) {
        return this.show(message, 'danger', duration);
    },

    /**
     * Uyarı mesajı
     */
    warning: function(message, duration = 4000) {
        return this.show(message, 'warning', duration);
    },

    /**
     * Bilgi mesajı
     */
    info: function(message, duration = 3000) {
        return this.show(message, 'info', duration);
    }
};

// Form Utilities
window.formUtils = {
    /**
     * Form validation
     */
    validateForm: function(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            const fieldValue = field.value || '';
            if (!fieldValue.toString().trim()) {
                field.classList.add('is-invalid');
                field.classList.remove('is-valid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
                field.classList.add('is-valid');
            }
        });
        
        return isValid;
    },

    /**
     * Real-time validation ekle
     */
    enableRealTimeValidation: function(form) {
        const inputs = form.querySelectorAll('.form-control, .form-select, textarea');
        
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                const inputValue = this.value || '';
                if (this.hasAttribute('required') && !inputValue.toString().trim()) {                    
                    this.classList.add('is-invalid');
                    this.classList.remove('is-valid');
                } else if (inputValue.toString().trim()) {  // DÜZELTİLDİ
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                }
            });
            
            input.addEventListener('input', function() {
                const inputValue = this.value || '';  // DÜZELTİLDİ
                if (this.classList.contains('is-invalid') && inputValue.toString().trim()) {  // DÜZELTİLDİ
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                }
            });
        });
    },

    /**
     * Form submit handler
     */
    handleSubmit: function(form, onSuccess, onError) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!window.formUtils.validateForm(form)) {
                if (onError) onError('Lütfen tüm gerekli alanları doldurun.');
                return;
            }
            
            // Loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="loading-spinner me-2"></span>Kaydediliyor...';
            
            try {
                const response = await window.dashboardUtils.submitForm(form);
                const data = await response.json();
                
                if (response.ok && data.success) {
                    if (onSuccess) onSuccess(data);
                    else window.notificationSystem.success('İşlem başarıyla tamamlandı!');
                } else {
                    throw new Error(data.message || 'Bir hata oluştu');
                }
            } catch (error) {
                console.error('Form submit error:', error);
                if (onError) onError(error.message);
                else window.notificationSystem.error('Bir hata oluştu: ' + error.message);
            } finally {
                // Reset button
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    },

    /**
     * Form reset
     */
    resetForm: function(form) {
        form.reset();
        const validationClasses = form.querySelectorAll('.is-valid, .is-invalid');
        validationClasses.forEach(el => {
            el.classList.remove('is-valid', 'is-invalid');
        });
    }
};

// Image Utilities
window.imageUtils = {
    /**
     * Resim önizleme
     */
    setupPreview: function(input, previewContainer) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    if (!previewContainer) {
                        previewContainer = document.createElement('div');
                        previewContainer.className = 'image-preview mt-2';
                        input.parentNode.appendChild(previewContainer);
                    }
                    
                    previewContainer.innerHTML = `
                        <img src="${e.target.result}" class="image-modern" style="max-width: 200px; max-height: 150px;">
                        <p class="small text-muted mt-1">${file.name}</p>
                    `;
                    previewContainer.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    },

    /**
     * Tüm image input'lara preview ekle
     */
    initializeAllPreviews: function() {
        const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
        imageInputs.forEach(input => {
            this.setupPreview(input);
        });
    }
};

// Search and Filter Utilities
window.searchUtils = {
    /**
     * Tablo arama
     */
    setupTableSearch: function(searchInput, table, columns = []) {
        if (!searchInput || !table) return;
        
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                if (row.querySelector('.empty-state')) return;
                
                let shouldShow = false;
                
                if (columns.length > 0) {
                    // Belirli sütunlarda ara
                    columns.forEach(columnIndex => {
                        const cell = row.querySelector(`td:nth-child(${columnIndex})`);
                        if (cell && cell.textContent.toLowerCase().includes(searchTerm)) {
                            shouldShow = true;
                        }
                    });
                } else {
                    // Tüm sütunlarda ara
                    const cells = row.querySelectorAll('td');
                    cells.forEach(cell => {
                        if (cell.textContent.toLowerCase().includes(searchTerm)) {
                            shouldShow = true;
                        }
                    });
                }
                
                row.style.display = shouldShow ? '' : 'none';
            });
        });
    },

    /**
     * Kart listesi arama
     */
    setupCardSearch: function(searchInput, cardSelector, searchFields = []) {
        if (!searchInput) return;
        
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const cards = document.querySelectorAll(cardSelector);
            
            cards.forEach(card => {
                let shouldShow = false;
                
                searchFields.forEach(field => {
                    const element = card.querySelector(field);
                    if (element && element.textContent.toLowerCase().includes(searchTerm)) {
                        shouldShow = true;
                    }
                });
                
                card.style.display = shouldShow ? '' : 'none';
            });
        });
    }
};

// Animation Utilities
window.animationUtils = {
    /**
     * Fade in animasyonu
     */
    fadeIn: function(element, duration = 300) {
        element.style.opacity = '0';
        element.style.display = 'block';
        
        let start = null;
        function animate(timestamp) {
            if (!start) start = timestamp;
            const progress = timestamp - start;
            const opacity = Math.min(progress / duration, 1);
            
            element.style.opacity = opacity;
            
            if (progress < duration) {
                requestAnimationFrame(animate);
            }
        }
        
        requestAnimationFrame(animate);
    },

    /**
     * Slide up animasyonu
     */
    slideUp: function(element, duration = 300) {
        element.style.maxHeight = element.scrollHeight + 'px';
        element.style.overflow = 'hidden';
        element.style.transition = `max-height ${duration}ms ease-out`;
        
        requestAnimationFrame(() => {
            element.style.maxHeight = '0';
        });
        
        setTimeout(() => {
            element.style.display = 'none';
            element.style.removeProperty('max-height');
            element.style.removeProperty('overflow');
            element.style.removeProperty('transition');
        }, duration);
    },

    /**
     * Slide down animasyonu
     */
    slideDown: function(element, duration = 300) {
        element.style.display = 'block';
        element.style.maxHeight = '0';
        element.style.overflow = 'hidden';
        element.style.transition = `max-height ${duration}ms ease-out`;
        
        requestAnimationFrame(() => {
            element.style.maxHeight = element.scrollHeight + 'px';
        });
        
        setTimeout(() => {
            element.style.removeProperty('max-height');
            element.style.removeProperty('overflow');
            element.style.removeProperty('transition');
        }, duration);
    }
};

// URL Utilities
window.urlUtils = {
    /**
     * URL parametresi al
     */
    getParam: function(name) {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get(name);
    },

    /**
     * URL parametresi set et
     */
    setParam: function(name, value) {
        const url = new URL(window.location);
        url.searchParams.set(name, value);
        window.history.pushState({}, '', url);
    },

    /**
     * URL parametresi sil
     */
    removeParam: function(name) {
        const url = new URL(window.location);
        url.searchParams.delete(name);
        window.history.pushState({}, '', url);
    }
};

// Storage Utilities
window.storageUtils = {
    /**
     * Local storage'a kaydet
     */
    set: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn('LocalStorage yazılamadı:', e);
        }
    },

    /**
     * Local storage'dan oku
     */
    get: function(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.warn('LocalStorage okunamadı:', e);
            return defaultValue;
        }
    },

    /**
     * Local storage'dan sil
     */
    remove: function(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.warn('LocalStorage silinemedi:', e);
        }
    }
};

// Global Error Handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    // Geliştirme ortamında detaylı hata göster
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        window.notificationSystem.error('JavaScript Hatası: ' + e.error.message);
    }
});

// Page Load Complete
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Dashboard Common JS loaded');
    
    // Auto-initialize image previews
    window.imageUtils.initializeAllPreviews();
    
    // Auto-enable real-time validation for all forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        window.formUtils.enableRealTimeValidation(form);
    });
});

// Notification animations CSS (inject edilecek)
const notificationCSS = `
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
    
    .notification-toast {
        border-radius: 12px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border: none;
    }
`;

// CSS'i head'e ekle
const notificationStyle = document.createElement('style');
notificationStyle.textContent = notificationCSS;
document.head.appendChild(notificationStyle);


// Empty State Button Modal Triggers - Otomatik modal bağlama
// Modal ID Fix: Case-insensitive modal bulma
document.addEventListener('DOMContentLoaded', function() {
    
    document.addEventListener('click', function(e) {
        const button = e.target.closest('button[data-bs-toggle="modal"]');
        
        if (button) {
            let targetModalId = button.getAttribute('data-bs-target');
            
            if (targetModalId) {
                // # işaretini kaldır
                const modalId = targetModalId.replace('#', '');
                
                // Önce tam eşleşmeyi dene
                let modalElement = document.getElementById(modalId);
                
                // Bulamazsa case-insensitive ara
                if (!modalElement) {
                    const allModals = document.querySelectorAll('.modal');
                    for (let modal of allModals) {
                        if (modal.id.toLowerCase() === modalId.toLowerCase()) {
                            modalElement = modal;
                            console.log(`🔧 Case-insensitive match: ${modalId} -> ${modal.id}`);
                            break;
                        }
                    }
                }
                
                if (modalElement) {
                    // Bootstrap Modal aç
                    if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                        const modal = new bootstrap.Modal(modalElement);
                        modal.show();
                        console.log('✅ Modal açıldı:', modalElement.id);
                    } else {
                        console.error('❌ Bootstrap bulunamadı!');
                    }
                } else {
                    console.error('❌ Modal bulunamadı:', targetModalId);
                    
                    // Mevcut modalleri listele
                    const existingModals = Array.from(document.querySelectorAll('.modal')).map(m => m.id);
                    console.log('📋 Mevcut modaller:', existingModals);
                }
            }
        }
    });
    
    console.log('🔧 Case-insensitive Modal Fix uygulandı');
});

// Bootstrap Modal Fix - common.js dosyasının sonuna ekle (mevcut olanı değiştir)
(function() {
    'use strict';
    
    let modalFixApplied = false;
    
    function applyModalFix() {
        if (modalFixApplied) return;
        
        // Bootstrap'in tam yüklendiğini kontrol et
        if (typeof bootstrap === 'undefined' || !bootstrap.Modal) {
            console.warn('Bootstrap henüz yüklenmedi, tekrar denenecek...');
            setTimeout(applyModalFix, 200);
            return;
        }
        
        modalFixApplied = true;
        console.log('Bootstrap Modal Fix applying...');
        
        // Tüm modal butonları için event listener ekle
        document.addEventListener('click', function(e) {
            const button = e.target.closest('[data-bs-toggle="modal"]');
            if (!button) return;
            
            e.preventDefault();
            e.stopPropagation();
            
            const targetSelector = button.getAttribute('data-bs-target');
            if (!targetSelector) return;
            
            const modalElement = document.querySelector(targetSelector);
            if (!modalElement) {
                console.error('Modal bulunamadı:', targetSelector);
                return;
            }
            
            try {
                // Modal'ı güvenli bir şekilde başlat ve aç
                let modalInstance = bootstrap.Modal.getInstance(modalElement);
                
                if (!modalInstance) {
                    modalInstance = new bootstrap.Modal(modalElement, {
                        backdrop: 'static',
                        keyboard: true,
                        focus: true
                    });
                }
                
                modalInstance.show();
                console.log('Modal açıldı:', targetSelector);
                
            } catch (error) {
                console.warn('Modal açma hatası:', error.message);
                // Fallback: Manuel modal açma
                modalElement.style.display = 'block';
                modalElement.classList.add('show');
                document.body.classList.add('modal-open');
                
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
            }
        });
        
        // Backdrop hatalarını yakala
        window.addEventListener('error', function(e) {
            if (e.message && e.message.includes('backdrop')) {
                console.warn('Backdrop hatası yakalandı:', e.message);
                e.preventDefault();
                return false;
            }
        });
        
        console.log('Bootstrap Modal Fix uygulandı');
    }
    
    // Sayfa yüklendiğinde çalıştır
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(applyModalFix, 500); // Bootstrap'in yüklenmesi için bekle
        });
    } else {
        setTimeout(applyModalFix, 500);
    }
})();

// Uzun işletme adları için otomatik class atama - NAVBAR
document.addEventListener('DOMContentLoaded', function() {
    const brandElement = document.querySelector('.navbar-brand');
    
    if (brandElement) {
        const text = brandElement.textContent.trim();
        
        // 25 karakterden uzun veya 3 kelimeden fazla ise 'long-name' class'ı ekle
        if (text.length > 25 || text.split(' ').length > 3) {
            brandElement.classList.add('long-name');
            console.log('Uzun işletme adı tespit edildi:', text);
        }
    }
});