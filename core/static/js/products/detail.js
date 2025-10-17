// core\static\js\products\detail.js Product Detail JavaScript
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
    
    // Initialize product detail features
    initImageZoom();
    initSocialShare();
    initScrollToDescription();
});

function initImageZoom() {
    initImageModal();

}

function initImageModal() {
    const productImage = document.getElementById('mainProductImage');
    
    if (productImage) {
        // Eski click handler'ı kaldır
        productImage.removeEventListener('click', handleImageClick);
        
        // Eğer universal modal varsa onu kullan
        if (window.universalModal) {
            console.log('Universal modal kullanılıyor');
            return; // Universal modal zaten otomatik olarak çalışacak
        }
        
        // Fallback: Manuel modal
        productImage.addEventListener('click', handleImageClick);
    }
}

function handleImageClick() {
    const img = this;
    const imageData = {
        src: img.src,
        title: img.alt,
        description: ''
    };
    
    if (window.openImageModal) {
        window.openImageModal(imageData);
    }
}

// ESC tuş sorunu için güncellenmiş kod
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        // Sadece eski modal varsa kapat
        const oldModal = document.querySelector('.image-modal');
        if (oldModal) {
            closeImageModal();
        }
        // Universal modal kendisi halleder
    }
});

function shareProduct() {
    if (navigator.share) {
        navigator.share({
            title: document.title,
            url: window.location.href
        });
    } else {
        // Fallback: copy to clipboard
        navigator.clipboard.writeText(window.location.href).then(() => {
            showNotification('Ürün linki panoya kopyalandı!');
        });
    }
}

function showNotification(message) {
    const notification = document.createElement('div');
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 2rem;
        right: 2rem;
        background: var(--primary-color);
        color: white;
        padding: 1rem 2rem;
        border-radius: 8px;
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function initSocialShare() {
    // Social share buttons (if added)
    const shareButtons = document.querySelectorAll('.social-share-btn');
    shareButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const platform = this.dataset.platform;
            const url = encodeURIComponent(window.location.href);
            const title = encodeURIComponent(document.title);
            
            let shareUrl = '';
            switch(platform) {
                case 'facebook':
                    shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
                    break;
                case 'twitter':
                    shareUrl = `https://twitter.com/intent/tweet?url=${url}&text=${title}`;
                    break;
                case 'whatsapp':
                    shareUrl = `https://wa.me/?text=${title}%20${url}`;
                    break;
            }
            
            if (shareUrl) {
                window.open(shareUrl, '_blank', 'width=600,height=400');
            }
        });
    });
}

function initScrollToDescription() {
    // Smooth scroll to description section
    const descriptionLinks = document.querySelectorAll('a[href="#description"]');
    descriptionLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector('.product-description-section');
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
}

// Product modal fonksiyonu ekle
function openProductModal() {
    const modalData = document.getElementById('product-modal-data');
    if (modalData) {
        try {
            const data = JSON.parse(modalData.textContent);
            
            if (window.openImageModal) {
                window.openImageModal({
                    src: data.originalImageUrl,
                    title: data.title,
                    description: data.description
                });
            } else {
                // Fallback basit modal
                createSimpleModal(data.originalImageUrl, data.title);
            }
        } catch (e) {
            console.error('Modal data parse error:', e);
        }
    }
}

function createSimpleModal(imageSrc, title) {
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.9); z-index: 9999; display: flex;
        align-items: center; justify-content: center; cursor: pointer;
    `;
    
    modal.innerHTML = `
        <img src="${imageSrc}" alt="${title}" style="max-width: 90%; max-height: 90%; object-fit: contain;">
        <div style="position: absolute; top: 20px; right: 30px; color: white; font-size: 30px; cursor: pointer;" onclick="this.parentElement.remove()">×</div>
    `;
    
    modal.onclick = () => modal.remove();
    document.body.appendChild(modal);
}

// Keyboard navigation for image modal
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeImageModal();
    }
});