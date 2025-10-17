/**core\static\js\home\statistics.js
 * Statistics Animation & Counter Functions
 * Animates counters and progress bars when they come into view
 */

class StatisticsAnimator {
    constructor() {
        this.section = document.getElementById('statisticsSection');
        this.statCards = document.querySelectorAll('.stat-card');
        this.hasAnimated = false;
        this.animationDuration = 2000; // 2 saniye
        this.observers = [];
        
        this.init();
    }
    
    init() {
        if (!this.section) return;
        
        this.setupIntersectionObserver();
        this.setupCounters();
    }
    
    /**
     * Intersection Observer setup - görünürde olduğunda animasyon başlat
     */
    setupIntersectionObserver() {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && !this.hasAnimated) {
                        this.animateStatistics();
                        this.hasAnimated = true;
                    }
                });
            },
            {
                threshold: 0.3, // %30'u görünür olduğunda tetikle
                rootMargin: '0px 0px -10% 0px'
            }
        );
        
        observer.observe(this.section);
        this.observers.push(observer);
    }
    
    /**
     * Setup individual counter animations
     */
    setupCounters() {
        this.statCards.forEach((card, index) => {
            const numberElement = card.querySelector('.stat-number');
            const progressBar = card.querySelector('.progress-bar');
            
            if (numberElement) {
                const targetValue = parseInt(numberElement.dataset.count) || 0;
                numberElement.dataset.target = targetValue;
                numberElement.textContent = '0'; // Başlangıç değeri
            }
            
            // Card'a animasyon delay'i ekle
            card.style.animationDelay = `${index * 100}ms`;
        });
    }
    
    /**
     * Ana animasyon fonksiyonu
     */
    animateStatistics() {
        // Card'lara animate sınıfı ekle
        this.statCards.forEach((card, index) => {
            setTimeout(() => {
                card.classList.add('animate');
                this.animateCounter(card);
                this.animateProgressBar(card);
            }, index * 150); // Her card için 150ms gecikme
        });
        
        // Floating numbers animation
        this.animateFloatingNumbers();
    }
    
    /**
     * Sayac animasyonu
     */
    animateCounter(card) {
        const numberElement = card.querySelector('.stat-number');
        if (!numberElement) return;
        
        const targetValue = parseInt(numberElement.dataset.target) || 0;
        const startValue = 0;
        const startTime = performance.now();
        
        const updateCounter = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / this.animationDuration, 1);
            
            // Easing function (ease-out)
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const currentValue = Math.floor(startValue + (targetValue - startValue) * easeOut);
            
            numberElement.textContent = this.formatNumber(currentValue);
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            } else {
                numberElement.textContent = this.formatNumber(targetValue);
            }
        };
        
        requestAnimationFrame(updateCounter);
    }
    
    /**
     * Progress bar animasyonu
     */
    animateProgressBar(card) {
        const progressBar = card.querySelector('.progress-bar');
        if (!progressBar) return;
        
        // Progress bar animasyonu için CSS transition kullan
        setTimeout(() => {
            progressBar.style.width = '100%';
        }, 200);
    }
    
    /**
     * Floating numbers animasyonu
     */
    animateFloatingNumbers() {
        const floatingNumbers = document.querySelectorAll('.floating-number');
        
        floatingNumbers.forEach((num, index) => {
            setTimeout(() => {
                num.style.opacity = '0.06';
                num.style.animation = `floatNumbers 10s ease-in-out infinite ${index * 2}s`;
            }, index * 500);
        });
    }
    
    /**
     * Sayı formatlamaları
     */
    formatNumber(num) {
        // 1000'den büyükse binlik ayracı ekle
        if (num >= 1000) {
            return num.toLocaleString('tr-TR');
        }
        return num.toString();
    }
    
    /**
     * Animasyonu sıfırla (gerekirse)
     */
    reset() {
        this.hasAnimated = false;
        
        this.statCards.forEach(card => {
            card.classList.remove('animate');
            
            const numberElement = card.querySelector('.stat-number');
            const progressBar = card.querySelector('.progress-bar');
            
            if (numberElement) {
                numberElement.textContent = '0';
            }
            
            if (progressBar) {
                progressBar.style.width = '0';
            }
        });
        
        // Floating numbers reset
        const floatingNumbers = document.querySelectorAll('.floating-number');
        floatingNumbers.forEach(num => {
            num.style.opacity = '0.03';
            num.style.animation = 'none';
        });
    }
    
    /**
     * Manuel tetikleme fonksiyonu
     */
    trigger() {
        if (!this.hasAnimated) {
            this.animateStatistics();
            this.hasAnimated = true;
        }
    }
    
    /**
     * Temizlik
     */
    destroy() {
        this.observers.forEach(observer => {
            observer.disconnect();
        });
        this.observers = [];
    }
}

/**
 * Scroll-based paralax effect for statistics section
 */
class StatisticsParallax {
    constructor() {
        this.section = document.getElementById('statisticsSection');
        this.decorations = document.querySelector('.stats-decorations');
        this.isEnabled = window.innerWidth > 768; // Mobilde devre dışı
        
        if (this.isEnabled) {
            this.init();
        }
    }
    
    init() {
        if (!this.section) return;
        
        window.addEventListener('scroll', this.handleScroll.bind(this), { passive: true });
        window.addEventListener('resize', this.handleResize.bind(this));
    }
    
    handleScroll() {
        const rect = this.section.getBoundingClientRect();
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.1;
        
        if (this.decorations && rect.top < window.innerHeight && rect.bottom > 0) {
            this.decorations.style.transform = `translateY(${rate}px)`;
        }
    }
    
    handleResize() {
        this.isEnabled = window.innerWidth > 768;
        
        if (!this.isEnabled && this.decorations) {
            this.decorations.style.transform = 'none';
        }
    }
}

/**
 * Global functions for external access
 */
window.triggerStatsAnimation = function() {
    if (window.statisticsAnimator) {
        window.statisticsAnimator.trigger();
    }
};

window.resetStatsAnimation = function() {
    if (window.statisticsAnimator) {
        window.statisticsAnimator.reset();
    }
};

/**
 * Initialize on DOM ready
 */
document.addEventListener('DOMContentLoaded', () => {
    window.statisticsAnimator = new StatisticsAnimator();
    window.statisticsParallax = new StatisticsParallax();
});

/**
 * Cleanup on page unload
 */
window.addEventListener('beforeunload', () => {
    if (window.statisticsAnimator) {
        window.statisticsAnimator.destroy();
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { StatisticsAnimator, StatisticsParallax };
}