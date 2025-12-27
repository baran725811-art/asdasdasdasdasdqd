// static/js/contact/main.js

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all contact page functionality
    initHeroAnimations();
    initFormHandling();
    initStarRating();
    initFileUpload();
    initCharacterCounters();
    initMapFunctionality();
    initScrollEffects();
});

// =====================================
// HERO ANIMATIONS
// =====================================

function initHeroAnimations() {
    // Animate statistics counters
    const contactStatNumbers = document.querySelectorAll('.contact-stats-counter');
    
    function animateCounter(element) {
        const target = parseInt(element.getAttribute('data-contact-count'));
        const duration = 2000; // 2 saniye
        const steps = 60;
        const increment = target / steps;
        let current = 0;
        let step = 0;
        
        const timer = setInterval(() => {
            step++;
            current = Math.min(current + increment, target);
            
            // Easing effect için
            const progress = step / steps;
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const displayValue = Math.floor(target * easeOut);
            
            element.textContent = displayValue;
            
            if (step >= steps) {
                element.textContent = target;
                clearInterval(timer);
                
                // Animasyon bitince hafif bir bounce efekti
                element.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    element.style.transform = 'scale(1)';
                }, 200);
            }
        }, duration / steps);
    }
    
    // Intersection Observer for counter animation
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    animateCounter(entry.target);
                }, 300);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    contactStatNumbers.forEach(stat => {
        counterObserver.observe(stat);
    });
    
    // Scroll indicator functionality
    const scrollIndicator = document.querySelector('.scroll-indicator');
    if (scrollIndicator) {
        scrollIndicator.addEventListener('click', () => {
            const nextSection = document.querySelector('.contact-form-section');
            if (nextSection) {
                nextSection.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    }
}

// =====================================
// FORM HANDLING
// =====================================

function initFormHandling() {
    const contactForm = document.getElementById('contactForm');
    const reviewForm = document.getElementById('reviewForm');
    
    if (contactForm) {
        setupFormValidation(contactForm);
        setupFormSubmission(contactForm);
    }
    
    if (reviewForm) {
        setupFormValidation(reviewForm);
        setupFormSubmission(reviewForm);
    }
}

function setupFormValidation(form) {
    const inputs = form.querySelectorAll('input, textarea');
    
    inputs.forEach(input => {
        // Real-time validation
        input.addEventListener('input', function() {
            validateField(this);
        });
        
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        // Enhanced focus effects
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
}

function validateField(field) {
    const container = field.closest('.form-group');
    const errorMessage = container.querySelector('.error-message');
    
    // Remove existing validation classes
    field.classList.remove('error', 'success');
    
    // Check field validity
    let isValid = true;
    let message = '';
    
    // Required field check
    if (field.hasAttribute('required') && !field.value.trim()) {
        isValid = false;
        message = 'Bu alan zorunludur';
    }
    
    // Email validation
    if (field.type === 'email' && field.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(field.value)) {
            isValid = false;
            message = 'Geçerli bir e-posta adresi girin';
        }
    }
    
    // Phone validation
    if (field.type === 'tel' && field.value) {
        const phoneRegex = /^[\+]?[0-9\s\-\(\)]{10,}$/;
        if (!phoneRegex.test(field.value)) {
            isValid = false;
            message = 'Geçerli bir telefon numarası girin';
        }
    }
    
    // Update field appearance
    if (isValid && field.value.trim()) {
        field.classList.add('success');
    } else if (!isValid) {
        field.classList.add('error');
        
        // Show custom error message
        if (errorMessage) {
            errorMessage.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
        }
    }
    
    return isValid;
}

function setupFormSubmission(form) {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const submitBtn = form.querySelector('.submit-btn');
        const btnText = submitBtn.querySelector('.btn-text');
        const btnIcon = submitBtn.querySelector('.btn-icon');
        
        // Validate all fields
        const inputs = form.querySelectorAll('input[required], textarea[required]');
        let allValid = true;
        
        inputs.forEach(input => {
            if (!validateField(input)) {
                allValid = false;
            }
        });
        
        if (!allValid) {
            showFormMessage('Lütfen tüm zorunlu alanları doldurun', 'error');
            return;
        }
        
        // Show loading state
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
        
        // Simulate form submission (replace with actual AJAX call)
        setTimeout(() => {
            // Reset form state
            submitBtn.classList.remove('loading');
            submitBtn.disabled = false;
            
            // Submit the form
            form.submit();
        }, 1000);
    });
}

function showFormMessage(message, type = 'info') {
    // Create message element
    const messageEl = document.createElement('div');
    messageEl.className = `form-message form-message-${type}`;
    messageEl.innerHTML = `
        <div class="message-content">
            <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'check-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(messageEl);
    
    // Animate in
    setTimeout(() => messageEl.classList.add('show'), 100);
    
    // Remove after delay
    setTimeout(() => {
        messageEl.classList.remove('show');
        setTimeout(() => messageEl.remove(), 300);
    }, 5000);
}

// =====================================
// STAR RATING SYSTEM
// =====================================

function initStarRating() {
    const starRating = document.querySelector('.star-rating');
    if (!starRating) return;
    
    const stars = starRating.querySelectorAll('label');
    const ratingText = document.querySelector('.rating-text .rating-label');
    
    const ratingLabels = {
        1: 'Kötü',
        2: 'Orta', 
        3: 'İyi',
        4: 'Çok İyi',
        5: 'Mükemmel'
    };
    
    stars.forEach((star, index) => {
        const rating = 5 - index; // Reverse order
        
        star.addEventListener('mouseenter', () => {
            updateStarDisplay(rating);
            if (ratingText) {
                ratingText.textContent = ratingLabels[rating];
            }
        });
        
        star.addEventListener('click', () => {
            const input = star.previousElementSibling;
            input.checked = true;
            updateStarDisplay(rating);
            if (ratingText) {
                ratingText.textContent = `Seçilen: ${ratingLabels[rating]}`;
            }
        });
    });
    
    starRating.addEventListener('mouseleave', () => {
        const checkedInput = starRating.querySelector('input:checked');
        if (checkedInput) {
            const rating = parseInt(checkedInput.value);
            updateStarDisplay(rating);
            if (ratingText) {
                ratingText.textContent = `Seçilen: ${ratingLabels[rating]}`;
            }
        } else {
            updateStarDisplay(0);
            if (ratingText) {
                ratingText.textContent = 'Puan seçin';
            }
        }
    });
    
    function updateStarDisplay(rating) {
        stars.forEach((star, index) => {
            const starRating = 5 - index;
            const icon = star.querySelector('i');
            
            if (starRating <= rating) {
                icon.style.color = '#ffc107';
                star.style.transform = 'scale(1.1)';
            } else {
                icon.style.color = '#ddd';
                star.style.transform = 'scale(1)';
            }
        });
    }
}

// =====================================
// FILE UPLOAD FUNCTIONALITY
// =====================================

function initFileUpload() {
    const uploadArea = document.getElementById('imageUploadArea');
    const fileInput = document.getElementById('id_image');
    const preview = document.getElementById('imagePreview');
    
    if (!uploadArea || !fileInput) return;
    
    // Drag and drop handlers
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // File input change handler
    fileInput.addEventListener('change', handleFileSelect);

    // Note: Click handler removed - the file input already covers the upload area
    // and will respond to clicks naturally due to its styling (opacity: 0, full coverage)
    
    function handleDragOver(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    }
    
    function handleDragLeave(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    }
    
    function handleDrop(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    }
    
    function handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            handleFile(file);
        }
    }
    
    function handleFile(file) {
        // Validate file type
        if (!file.type.startsWith('image/')) {
            showFormMessage('Lütfen sadece resim dosyası seçin', 'error');
            return;
        }
        
        // Validate file size (5MB)
        if (file.size > 5 * 1024 * 1024) {
            showFormMessage('Dosya boyutu 5MB\'dan küçük olmalıdır', 'error');
            return;
        }
        
        // Show preview
        const reader = new FileReader();
        reader.onload = function(e) {
            const img = preview.querySelector('.preview-image');
            img.src = e.target.result;
            
            // Hide upload content, show preview
            uploadArea.querySelector('.upload-content').style.display = 'none';
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
}

// Remove image function (called from HTML)
function removeImage() {
    const uploadArea = document.getElementById('imageUploadArea');
    const fileInput = document.getElementById('id_image');
    const preview = document.getElementById('imagePreview');
    
    if (uploadArea && fileInput && preview) {
        fileInput.value = '';
        uploadArea.querySelector('.upload-content').style.display = 'block';
        preview.style.display = 'none';
    }
}

// =====================================
// CHARACTER COUNTERS
// =====================================

function initCharacterCounters() {
    const textareas = document.querySelectorAll('textarea');
    
    textareas.forEach(textarea => {
        const counter = textarea.parentElement.querySelector('.character-counter');
        if (!counter) return;
        
        const maxLength = 1000; // Default max length
        const currentSpan = counter.querySelector('.current');
        const maxSpan = counter.querySelector('.max');
        
        if (maxSpan) {
            maxSpan.textContent = maxLength;
        }
        
        // Update counter on input
        textarea.addEventListener('input', function() {
            const currentLength = this.value.length;
            
            if (currentSpan) {
                currentSpan.textContent = currentLength;
            }
            
            // Update counter color based on length
            if (currentLength > maxLength * 0.9) {
                counter.style.color = 'var(--form-error)';
            } else if (currentLength > maxLength * 0.7) {
                counter.style.color = 'var(--contact-warning)';
            } else {
                counter.style.color = 'var(--text-muted)';
            }
        });
        
        // Initial count
        textarea.dispatchEvent(new Event('input'));
    });
}

// =====================================
// MAP FUNCTIONALITY
// =====================================

function initMapFunctionality() {
    // Get directions functionality
    window.getDirections = function() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;
                
                // Batman/Köprübaşı coordinates (approximate)
                const destination = '37.8887,41.1309';
                
                // Open Google Maps with directions
                const url = `https://www.google.com/maps/dir/${lat},${lng}/${destination}`;
                window.open(url, '_blank');
            }, function(error) {
                // Fallback: open maps without current location
                const destination = '37.8887,41.1309';
                const url = `https://www.google.com/maps/dir//${destination}`;
                window.open(url, '_blank');
                
                console.warn('Konum erişimi engellendi:', error);
            });
        } else {
            // Browser doesn't support geolocation
            const destination = '37.8887,41.1309';
            const url = `https://www.google.com/maps/dir//${destination}`;
            window.open(url, '_blank');
        }
    };
}

// =====================================
// SCROLL EFFECTS
// =====================================

function initScrollEffects() {
    // Intersection Observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animatedElements = document.querySelectorAll(`
        .form-card,
        .info-card,
        .map-card,
        .review-form-card,
        .recent-reviews,
        .service-areas,
        .contact-info-item,
        .service-area-item
    `);
    
    animatedElements.forEach(el => {
        observer.observe(el);
    });
    
    // Add CSS for animations
    addScrollAnimationStyles();
}

function addScrollAnimationStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .form-card,
        .info-card,
        .map-card,
        .review-form-card,
        .recent-reviews,
        .service-areas {
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.6s ease;
        }
        
        .contact-info-item,
        .service-area-item {
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.5s ease;
        }
        
        .animate-in {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
        
        /* Stagger animation for items */
        .contact-info-item:nth-child(1) { transition-delay: 0.1s; }
        .contact-info-item:nth-child(2) { transition-delay: 0.2s; }
        .contact-info-item:nth-child(3) { transition-delay: 0.3s; }
        .contact-info-item:nth-child(4) { transition-delay: 0.4s; }
        
        .service-area-item:nth-child(1) { transition-delay: 0.1s; }
        .service-area-item:nth-child(2) { transition-delay: 0.2s; }
        .service-area-item:nth-child(3) { transition-delay: 0.3s; }
        .service-area-item:nth-child(4) { transition-delay: 0.4s; }
        
        /* Form message styles */
        .form-message {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.16);
            border-left: 4px solid var(--contact-success);
            transform: translateX(400px);
            transition: transform 0.3s ease;
            max-width: 400px;
        }
        
        .form-message.form-message-error {
            border-left-color: var(--form-error);
        }
        
        .form-message.show {
            transform: translateX(0);
        }
        
        .message-content {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 1rem 1.5rem;
            font-weight: 500;
        }
        
        .form-message-error .message-content {
            color: var(--form-error);
        }
        
        .form-message:not(.form-message-error) .message-content {
            color: var(--contact-success);
        }
    `;
    
    document.head.appendChild(style);
}

// =====================================
// CAPTCHA REFRESH FUNCTIONS
// =====================================

function refreshContactCaptcha() {
    const captcha = document.querySelector('#contactForm .captcha');
    if (captcha) {
        const img = captcha.querySelector('img');
        if (img) {
            img.src = img.src.split('?')[0] + '?' + Math.random();
        }
    }
}

function refreshReviewCaptcha() {
    const captcha = document.querySelector('#reviewForm .captcha');
    if (captcha) {
        const img = captcha.querySelector('img');
        if (img) {
            img.src = img.src.split('?')[0] + '?' + Math.random();
        }
    }
}

// Make functions globally available
window.refreshContactCaptcha = refreshContactCaptcha;
window.refreshReviewCaptcha = refreshReviewCaptcha;

// =====================================
// UTILITY FUNCTIONS
// =====================================

// Phone number formatting
function formatPhoneNumber(input) {
    // Remove all non-digits
    let value = input.value.replace(/\D/g, '');
    
    // Add country code if missing
    if (value.length > 0 && !value.startsWith('90')) {
        if (value.startsWith('0')) {
            value = '90' + value.substring(1);
        } else if (value.length === 10) {
            value = '90' + value;
        }
    }
    
    // Format as +90 5XX XXX XX XX
    if (value.length >= 12) {
        value = value.substring(0, 12);
        const formatted = `+${value.substring(0, 2)} ${value.substring(2, 5)} ${value.substring(5, 8)} ${value.substring(8, 10)} ${value.substring(10)}`;
        input.value = formatted;
    }
}

// Initialize phone formatting for phone inputs
document.addEventListener('DOMContentLoaded', function() {
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function() {
            formatPhoneNumber(this);
        });
    });
});

// =====================================
// ACCESSIBILITY ENHANCEMENTS
// =====================================

function initAccessibilityFeatures() {
    // Skip to content functionality
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'İçeriğe Geç';
    skipLink.className = 'skip-link';
    skipLink.style.cssText = `
        position: absolute;
        top: -40px;
        left: 6px;
        background: var(--contact-primary);
        color: white;
        padding: 8px;
        text-decoration: none;
        border-radius: 4px;
        z-index: 1000;
        transition: top 0.3s;
    `;
    
    skipLink.addEventListener('focus', function() {
        this.style.top = '6px';
    });
    
    skipLink.addEventListener('blur', function() {
        this.style.top = '-40px';
    });
    
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Enhanced keyboard navigation for star rating
    const starInputs = document.querySelectorAll('.star-rating input');
    starInputs.forEach((input, index) => {
        input.addEventListener('keydown', function(e) {
            const parent = this.closest('.star-rating');
            const inputs = parent.querySelectorAll('input');
            
            if (e.key === 'ArrowLeft' && index < inputs.length - 1) {
                inputs[index + 1].focus();
                e.preventDefault();
            } else if (e.key === 'ArrowRight' && index > 0) {
                inputs[index - 1].focus();
                e.preventDefault();
            }
        });
    });
    
    // ARIA labels for dynamic content
    const uploadArea = document.getElementById('imageUploadArea');
    if (uploadArea) {
        uploadArea.setAttribute('role', 'button');
        uploadArea.setAttribute('aria-label', 'Dosya yüklemek için tıklayın veya sürükleyip bırakın');
        uploadArea.setAttribute('tabindex', '0');
        
        uploadArea.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                document.getElementById('id_image').click();
            }
        });
    }
}

// Initialize accessibility features
document.addEventListener('DOMContentLoaded', initAccessibilityFeatures);

// =====================================
// PERFORMANCE OPTIMIZATIONS
// =====================================

// Debounce function for input validation
function debounce(func, wait) {
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

// Lazy load map iframe
function initLazyMapLoading() {
    const mapIframe = document.querySelector('.map-wrapper iframe');
    if (!mapIframe) return;
    
    const mapObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const iframe = entry.target;
                if (iframe.dataset.src) {
                    iframe.src = iframe.dataset.src;
                    iframe.removeAttribute('data-src');
                }
                mapObserver.unobserve(iframe);
            }
        });
    });
    
    // Move src to data-src for lazy loading
    mapIframe.dataset.src = mapIframe.src;
    mapIframe.src = '';
    mapObserver.observe(mapIframe);
}

// Initialize performance optimizations
document.addEventListener('DOMContentLoaded', initLazyMapLoading);



