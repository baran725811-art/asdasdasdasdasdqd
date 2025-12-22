// About sayfası JavaScript dosyası - NULL CHECK EKLENDİ
// Bu dosya core/static/dashboard/js/pages/about.js dosyasına kaydedilmelidir

// Form Status Tracker Functions
function updateFormStatus() {
    const fields = {
        title: document.querySelector('[name="title"]'),
        short_description: document.querySelector('[name="short_description"]'),
        image: document.querySelector('[name="image"]'),
        mission: document.querySelector('[name="mission"]'),
        vision: document.querySelector('[name="vision"]'),
        story: document.querySelector('[name="story"]'),
        years_experience: document.querySelector('[name="years_experience"]'),
        completed_jobs: document.querySelector('[name="completed_jobs"]'),
        happy_customers: document.querySelector('[name="happy_customers"]'),
        total_services: document.querySelector('[name="total_services"]'),
        customer_satisfaction: document.querySelector('[name="customer_satisfaction"]')
    };

    let completed = 0;
    let total = 11;
    let validationIssues = [];

    // Django config'den veri al
    const config = window.aboutConfig || {};
    const translations = config.translations || {};

    // Başlık kontrolü
    if (fields.title && fields.title.value.trim().length > 0) {
        const length = fields.title.value.length;
        if (length < 10) {
            validationIssues.push('Sayfa başlığı çok kısa (en az 10 karakter)');
            updateFieldStatus('title', 'warning', 'Kısa', `${length} karakter`);
        } else if (length > 60) {
            validationIssues.push('Sayfa başlığı çok uzun (SEO için max 60 karakter)');
            updateFieldStatus('title', 'warning', 'Uzun', `${length} karakter`);
        } else {
            updateFieldStatus('title', 'success', 'Uygun', `${length} karakter`);
        }
        completed++;
    } else {
        validationIssues.push('Sayfa başlığı zorunludur');
        updateFieldStatus('title', 'danger', 'Boş', '0 karakter');
    }

    // Açıklama kontrolü
    if (fields.short_description && fields.short_description.value.trim().length > 0) {
        const length = fields.short_description.value.length;
        if (length < 20) {
            validationIssues.push('Kısa açıklama çok kısa (en az 20 karakter)');
            updateFieldStatus('description', 'warning', 'Kısa', `${length} karakter`);
        } else if (length > 160) {
            validationIssues.push('Kısa açıklama çok uzun (SEO için max 160 karakter)');
            updateFieldStatus('description', 'warning', 'Uzun', `${length} karakter`);
        } else {
            updateFieldStatus('description', 'success', 'Uygun', `${length} karakter`);
        }
        completed++;
    } else {
        validationIssues.push('Kısa açıklama zorunludur');
        updateFieldStatus('description', 'danger', 'Boş', '0 karakter');
    }

    // Görsel kontrolü
    const existingImage = document.querySelector('.current-image img');
    const newImage = fields.image && fields.image.files && fields.image.files.length > 0;
    if (existingImage || newImage) {
        updateFieldStatus('image', 'success', 'Var', newImage ? 'Yeni görsel seçildi' : 'Mevcut görsel');
        completed++;
    } else {
        validationIssues.push('Ana görsel zorunludur');
        updateFieldStatus('image', 'danger', 'Yok', 'Görsel seçilmedi');
    }

    // İçerik alanları kontrolü
    const contentFields = [
        { name: 'mission', label: 'Misyon', status: 'mission' },
        { name: 'vision', label: 'Vizyon', status: 'vision' },
        { name: 'story', label: 'Hikaye', status: 'story' }
    ];

    contentFields.forEach(field => {
        if (fields[field.name] && fields[field.name].value.trim().length > 0) {
            const length = fields[field.name].value.length;
            if (length < 50) {
                validationIssues.push(`${field.label} çok kısa (en az 50 karakter)`);
                updateFieldStatus(field.status, 'warning', 'Kısa', `${length} karakter`);
            } else {
                updateFieldStatus(field.status, 'success', 'Uygun', `${length} karakter`);
            }
            completed++;
        } else {
            validationIssues.push(`${field.label} zorunludur`);
            updateFieldStatus(field.status, 'danger', 'Boş', '0 karakter');
        }
    });

    // İstatistikler kontrolü
    const statsFields = ['years_experience', 'completed_jobs', 'happy_customers', 'total_services', 'customer_satisfaction'];
    let statsCompleted = 0;
    let statsWithIssues = [];

    statsFields.forEach(fieldName => {
        if (fields[fieldName] && fields[fieldName].value.trim().length > 0) {
            const value = parseInt(fields[fieldName].value);
            if (isNaN(value) || value < 0) {
                statsWithIssues.push(fieldName);
            } else if (fieldName === 'customer_satisfaction' && (value < 0 || value > 100)) {
                statsWithIssues.push('customer_satisfaction (0-100 arası olmalı)');
            } else {
                statsCompleted++;
                completed++;
            }
        }
    });

    if (statsWithIssues.length > 0) {
        validationIssues.push('İstatistik alanlarında geçersiz değerler var');
    }
    if (statsCompleted < 5) {
        validationIssues.push(`İstatistik alanları eksik (${statsCompleted}/5 tamamlandı)`);
    }

    if (statsCompleted === 5 && statsWithIssues.length === 0) {
        updateFieldStatus('stats', 'success', 'Tamamlandı', '5/5 alan uygun');
    } else if (statsCompleted > 0) {
        updateFieldStatus('stats', 'warning', 'Kısmi', `${statsCompleted}/5 alan dolduruldu`);
        completed = completed - (5 - statsCompleted);
    } else {
        updateFieldStatus('stats', 'danger', 'Eksik', '0/5 alan dolduruldu');
    }

    // Validation durumunu güncelle
    updateValidationStatus(validationIssues);

    // Genel progress güncelleme
    const percentage = Math.round((completed / total) * 100);
    updateProgress(percentage);
    updateSummary(completed, total - completed, total);
}

function updateValidationStatus(issues) {
    const alertElement = document.getElementById('validationAlert');
    const successElement = document.getElementById('validationSuccess');
    const listElement = document.getElementById('validationList');

    // ✅ NULL CHECK EKLENDI
    if (!alertElement || !successElement || !listElement) {
        console.log('Validation elements not found - sidebar may be disabled');
        return;
    }

    if (issues.length > 0) {
        listElement.innerHTML = '';
        issues.forEach(issue => {
            const li = document.createElement('li');
            li.textContent = issue;
            listElement.appendChild(li);
        });
        alertElement.style.display = 'block';
        successElement.style.display = 'none';
    } else {
        alertElement.style.display = 'none';
        successElement.style.display = 'block';
    }
}

function updateFieldStatus(fieldId, badgeColor, badgeText, infoText) {
    const statusElement = document.getElementById(`${fieldId}Status`);
    const infoElement = document.getElementById(`${fieldId}Info`);
    const statusItem = statusElement ? statusElement.closest('.status-item') : null;
    
    // ✅ NULL CHECK EKLENDI
    if (!statusElement) {
        console.log(`Status element not found: ${fieldId}Status`);
        return;
    }
    
    statusElement.style.transform = 'scale(0.8)';
    statusElement.style.opacity = '0';
    
    setTimeout(() => {
        statusElement.className = `badge bg-${badgeColor}`;
        statusElement.textContent = badgeText;
        statusElement.style.transform = 'scale(1)';
        statusElement.style.opacity = '1';
    }, 150);
    
    if (statusItem) {
        statusItem.classList.remove('status-completed', 'status-warning', 'status-danger', 'status-secondary');
        statusItem.classList.add(`status-${badgeColor}`, 'field-status-updating');
        
        setTimeout(() => {
            statusItem.classList.remove('field-status-updating');
        }, 600);
    }
    
    if (infoElement) {
        infoElement.style.opacity = '0.6';
        setTimeout(() => {
            infoElement.textContent = infoText;
            infoElement.style.opacity = '1';
        }, 100);
    }
}

function updateProgress(percentage) {
    const progressBar = document.getElementById('formProgress');
    const progressText = document.getElementById('formProgressText');
    
    // ✅ NULL CHECK EKLENDI
    if (!progressBar) {
        console.log('Progress bar not found');
        return;
    }
    
    progressBar.style.transition = 'width 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
    progressBar.style.width = `${percentage}%`;
    progressBar.setAttribute('aria-valuenow', percentage);
    
    progressBar.className = 'progress-bar';
    if (percentage < 30) {
        progressBar.classList.add('bg-danger');
    } else if (percentage < 70) {
        progressBar.classList.add('bg-warning');
    } else {
        progressBar.classList.add('bg-success');
    }
    
    if (percentage >= 90) {
        progressBar.style.animation = 'pulse 1s ease-in-out infinite';
    } else {
        progressBar.style.animation = 'none';
    }
    
    if (progressText) {
        const currentText = parseInt(progressText.textContent) || 0;
        animateCounter(progressText, currentText, percentage);
    }
}

function animateCounter(element, start, end) {
    const duration = 500;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const current = Math.round(start + (end - start) * progress);
        element.textContent = `${current}%`;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

function updateSummary(completed, pending, total) {
    const completedEl = document.getElementById('completedFields');
    const pendingEl = document.getElementById('pendingFields');
    const totalEl = document.getElementById('totalFields');
    
    // ✅ NULL CHECK EKLENDI
    if (completedEl) completedEl.textContent = completed;
    if (pendingEl) pendingEl.textContent = pending;
    if (totalEl) totalEl.textContent = total;
}

function showSaveStatus(message, type) {
    const statusDiv = document.getElementById('saveStatus');
    const statusText = document.getElementById('saveStatusText');
    
    // ✅ NULL CHECK EKLENDI
    if (!statusDiv || !statusText) {
        console.log('Save status elements not found');
        return;
    }
    
    const alertDiv = statusDiv.querySelector('.alert');
    if (!alertDiv) return;
    
    alertDiv.className = `alert alert-${type} mb-0`;
    
    const icon = alertDiv.querySelector('i');
    if (icon) {
        if (type === 'info') {
            icon.className = 'fas fa-spinner fa-spin me-2';
        } else if (type === 'success') {
            icon.className = 'fas fa-check-circle me-2';
        } else if (type === 'danger') {
            icon.className = 'fas fa-exclamation-circle me-2';
        }
    }
    
    statusText.textContent = message;
    statusDiv.style.display = 'block';
    
    if (type !== 'info') {
        setTimeout(() => {
            statusDiv.style.display = 'none';
        }, 5000);
    }
}

function saveDraft() {
    const form = document.getElementById('aboutForm');
    if (!form) {
        console.error('Form bulunamadı!');
        return;
    }
    
    const config = window.aboutConfig || {};
    const translations = config.translations || {};
    
    showSaveStatus(translations.saving || 'Taslak kaydediliyor...', 'info');
    
    const formData = new FormData(form);
    formData.append('is_draft', 'true');
    
    fetch(window.location.href, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSaveStatus(translations.saved || 'Taslak kaydedildi!', 'success');
        } else {
            showSaveStatus(translations.error || 'Taslak kayıt hatası!', 'danger');
        }
    })
    .catch(error => {
        console.error('Taslak kayıt hatası:', error);
        showSaveStatus(translations.error || 'Taslak kayıt hatası!', 'danger');
    });
}

function resetForm() {
    if (confirm('Tüm değişiklikler kaybolacak. Emin misiniz?')) {
        const form = document.getElementById('aboutForm');
        if (form) {
            form.reset();
            updateFormStatus();
            showSaveStatus('Form sıfırlandı!', 'info');
        }
    }
}

// Ana Event Listener
document.addEventListener('DOMContentLoaded', function() {
    console.log('About.js yüklendi');
    
    const aboutForm = document.getElementById('aboutForm');
    if (!aboutForm) {
        console.error('Form bulunamadı!');
        return;
    }
    
    const config = window.aboutConfig || {};
    console.log('Config:', config);
    
    // Form durumu takibini başlat (sidebar varsa)
    const sidebarExists = document.getElementById('formProgress');
    if (sidebarExists) {
        updateFormStatus();
        
        // Form alanlarındaki değişiklikleri dinle
        const formFields = aboutForm.querySelectorAll('input, textarea, select');
        formFields.forEach(field => {
            field.addEventListener('input', updateFormStatus);
            field.addEventListener('change', updateFormStatus);
        });
    } else {
        console.log('Sidebar elements not found - status tracking disabled');
    }
    
    // ✅ ÇEVIRI TAB'LARINI KONTROL ET
    const translationTabs = document.querySelectorAll('.translation-tab');
    const translationContents = document.querySelectorAll('.translation-content');
    
    if (translationTabs.length === 0 || translationContents.length === 0) {
        console.log('Translation system not found - single language mode');
        // Çeviri sistemi yoksa sadece form handler'ı çalıştır
    } else {
        console.log(`Found ${translationTabs.length} translation tabs`);
        
        // Translation tabs handler
        translationTabs.forEach(tab => {
            tab.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                const targetLang = this.getAttribute('data-lang');
                console.log('Switching to language:', targetLang);
                
                // Immediate UI update
                translationTabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');

                requestAnimationFrame(() => {
                    // Hide all contents first
                    translationContents.forEach(content => {
                        content.style.display = 'none';
                        content.classList.remove('active');
                    });

                    // Show target content
                    translationContents.forEach(content => {
                        const contentLang = content.getAttribute('data-lang');
                        if (contentLang === targetLang) {
                            content.style.display = 'block';
                            content.classList.add('active');

                            const inputs = content.querySelectorAll('input, textarea');
                            inputs.forEach(input => {
                                input.dispatchEvent(new Event('focus', { bubbles: false }));
                                input.blur();
                            });
                        }
                    });
                });
            });
        });
    }
    
    // Form submit handler
    aboutForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const submitBtn = this.querySelector('button[type="submit"]');
        if (!submitBtn) {
            console.error('Submit button not found!');
            return;
        }
        
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Kaydediliyor...';
        submitBtn.disabled = true;
        
        const config = window.aboutConfig || {};
        const translations = config.translations || {};
        
        showSaveStatus(translations.saving || 'Kaydediliyor...', 'info');
        
        const formData = new FormData(this);
        
        fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => response.json())
        .then(data => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            
            if (data.success) {
                showSaveStatus(translations.saved || 'Başarıyla kaydedildi!', 'success');
                
                const modal = document.getElementById('saveSuccessModal');
                if (modal && typeof bootstrap !== 'undefined') {
                    const bsModal = new bootstrap.Modal(modal);
                    bsModal.show();
                }
                
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showSaveStatus((translations.error || 'Kayıt hatası: ') + (data.error || 'Bilinmeyen hata'), 'danger');
            }
        })
        .catch(error => {
            console.error('Network error:', error);
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            showSaveStatus(translations.error || 'Bağlantı hatası!', 'danger');
        });
    });
});

// ===============================================
// SERVICE FORM SUBMIT HANDLER
// ===============================================
const serviceAddForm = document.getElementById('serviceForm');
const serviceEditForms = document.querySelectorAll('[id^="editServiceForm"]');

if (serviceAddForm) {
    serviceAddForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        // Loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Kaydediliyor...';
        
        try {
            const formData = new FormData(this);
            const response = await fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                showToast('Başarılı', result.message || 'Hizmet başarıyla eklendi.', 'success');
                
                // Modal'ı kapat
                const modal = bootstrap.Modal.getInstance(document.getElementById('addServiceModal'));
                if (modal) modal.hide();
                
                // Sayfayı yenile
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showToast('Hata', result.message || 'Kaydetme başarısız.', 'error');
            }
            
        } catch (error) {
            console.error('Service save error:', error);
            showToast('Hata', 'Bir hata oluştu. Lütfen tekrar deneyin.', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    });
}

// Service Edit Forms
serviceEditForms.forEach(form => {
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        // Loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Güncelleniyor...';
        
        try {
            const formData = new FormData(this);
            const response = await fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                showToast('Başarılı', result.message || 'Hizmet başarıyla güncellendi.', 'success');
                
                // Modal'ı kapat
                const modalId = this.closest('.modal').id;
                const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
                if (modal) modal.hide();
                
                // Sayfayı yenile
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showToast('Hata', result.message || 'Güncelleme başarısız.', 'error');
            }
            
        } catch (error) {
            console.error('Service update error:', error);
            showToast('Hata', 'Bir hata oluştu. Lütfen tekrar deneyin.', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    });
});

// Hizmetler kısmı için initialize
function initServices() {
    console.log('🔧 Services section initializing...');
