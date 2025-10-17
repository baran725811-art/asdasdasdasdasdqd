// Products Page JavaScript core\static\js\products\main.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize AOS
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            easing: 'ease-out-cubic',
            once: true,
            offset: 100
        });
    }
    
    // Initialize product interactions
    initProductCards();
    initSearchForm();
    initLazyLoading();
});

function handleSortChange(sortValue) {
    const url = new URL(window.location.href);
    url.searchParams.set('sort', sortValue);
    window.location.href = url.toString();
}

function initProductCards() {
    const productCards = document.querySelectorAll('.product-card, .featured-card');
    
    productCards.forEach(card => {
        // Add hover animations
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
        
        // Add click analytics (if needed)
        const productLink = card.querySelector('a[href*="urun"]');
        if (productLink) {
            productLink.addEventListener('click', function() {
                // Analytics tracking code here
                console.log('Product clicked:', this.href);
            });
        }
    });
}

function initSearchForm() {
    const searchForm = document.querySelector('.search-form');
    const searchInput = document.querySelector('.search-input');
    
    if (searchForm && searchInput) {
        // Auto-submit on enter
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchForm.submit();
            }
        });
        
        // Clear search button
        if (searchInput.value) {
            addClearButton(searchInput);
        }
    }
}

function addClearButton(input) {
    const clearBtn = document.createElement('button');
    clearBtn.type = 'button';
    clearBtn.className = 'search-clear';
    clearBtn.innerHTML = '<i class="fas fa-times"></i>';
    clearBtn.style.cssText = `
        position: absolute;
        right: 3rem;
        top: 50%;
        transform: translateY(-50%);
        background: none;
        border: none;
        color: #999;
        cursor: pointer;
        font-size: 0.9rem;
    `;
    
    clearBtn.addEventListener('click', function() {
        input.value = '';
        input.focus();
        this.remove();
    });
    
    input.parentElement.appendChild(clearBtn);
}

function initLazyLoading() {
    const images = document.querySelectorAll('img[loading="lazy"]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.src; // Trigger loading
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });
        
        images.forEach(img => {
            img.classList.add('lazy');
            imageObserver.observe(img);
        });
    }
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Filter animations
function animateFilters() {
    const filterButtons = document.querySelectorAll('.category-btn');
    
    filterButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            // Add loading state
            this.style.opacity = '0.7';
            this.style.pointerEvents = 'none';
            
            // Reset after navigation
            setTimeout(() => {
                this.style.opacity = '1';
                this.style.pointerEvents = 'auto';
            }, 1000);
        });
    });
}

// Call filter animations
animateFilters();