/**ccore\static\dashboard\js\components\image-crop.js
 * Modern Image Crop Functionality
 * Professional and minimalist cropping interface
 */

/**
 * Dashboard Image Crop - Inline Version
 */

document.addEventListener('DOMContentLoaded', function() {
    initImageCropWidgets();
});

let croppers = {};
let cropperLoaded = false;

function initImageCropWidgets() {
    const cropContainers = document.querySelectorAll('.image-crop-container');

    cropContainers.forEach(container => {
        const fieldName = container.dataset.fieldName;
        const fileInput = container.querySelector('input[type="file"]');

        if (fileInput) {
            fileInput.addEventListener('change', function(e) {
                if (e.isCropEvent) return;

                const file = e.target.files[0];
                if (file && file.type.startsWith('image/')) {
                    openCropInline(fieldName, file);
                }
            });

            addCropButtonToExisting(container, fieldName);
        }

        // ★ EDIT MODE: Handle recrop button clicks
        const recropBtn = container.querySelector('.recrop-btn');
        if (recropBtn) {
            recropBtn.addEventListener('click', function(e) {
                e.preventDefault();
                const imageUrl = this.dataset.imageUrl;
                if (imageUrl) {
                    fetch(imageUrl)
                        .then(response => response.blob())
                        .then(blob => {
                            const file = new File([blob], 'existing-image.jpg', { type: blob.type });
                            openCropInline(fieldName, file);
                        })
                        .catch(error => {
                            console.error('Failed to load existing image:', error);
                            alert('Görsel yüklenemedi. Lütfen tekrar deneyin.');
                        });
                }
            });
        }
    });
}

function addCropButtonToExisting(container, fieldName) {
    const currentLink = container.querySelector('a[target="_blank"]');
    
    if (currentLink) {
        const cropBtn = document.createElement('button');
        cropBtn.type = 'button';
        cropBtn.className = 'crop-trigger-btn';
        cropBtn.innerHTML = '<span>✂️</span> Resmi Yeniden Kırp';
        cropBtn.onclick = () => {
            fetch(currentLink.href)
                .then(response => response.blob())
                .then(blob => {
                    const file = new File([blob], 'existing-image', { type: blob.type });
                    openCropInline(fieldName, file);
                })
                .catch(error => console.error('Failed to load existing image:', error));
        };
        
        currentLink.parentNode.appendChild(cropBtn);
    }
}

function openCropInline(fieldName, file) {
    const container = document.querySelector(`[data-field-name="${fieldName}"]`);
    let cropContainer = container.querySelector('.crop-inline-container');
    
    if (!cropContainer) {
        const cropHTML = `
            <div class="crop-inline-container" style="display:none; border: 1px solid #e0e0e0; border-radius: 8px; margin-top: 15px; overflow: hidden;">
                <div class="crop-inline-header" style="background: #5e72e4; color: white; padding: 12px 20px; display: flex; justify-content: space-between; align-items: center;">
                    <h6 style="margin: 0; font-size: 14px; font-weight: 600;"><i class="fas fa-crop me-2"></i>Resmi Kırp</h6>
                    <button type="button" class="btn-close-crop" style="background: none; border: none; color: white; font-size: 24px; cursor: pointer; line-height: 1; transition: opacity 0.2s;">&times;</button>
                </div>
                <div class="crop-inline-body" style="padding: 20px; max-height: 400px; overflow: auto;">
                    <img id="cropImage_${fieldName}" style="max-width: 100%; display: block;">
                </div>
                <div class="crop-inline-footer" style="padding: 15px 20px; background: #f8f9fa; display: flex; justify-content: flex-end; gap: 10px;">
                    <button type="button" class="btn btn-secondary btn-sm btn-cancel-crop">İptal</button>
                    <button type="button" class="btn btn-primary btn-sm btn-apply-crop">Kırpmayı Uygula</button>
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', cropHTML);
        cropContainer = container.querySelector('.crop-inline-container');
        
        // Event listeners
        cropContainer.querySelector('.btn-close-crop').addEventListener('click', () => closeCropInline(fieldName));
        cropContainer.querySelector('.btn-cancel-crop').addEventListener('click', () => closeCropInline(fieldName));
        cropContainer.querySelector('.btn-apply-crop').addEventListener('click', () => applyCrop(fieldName));
        
        // Hover effect
        cropContainer.querySelector('.btn-close-crop').addEventListener('mouseenter', (e) => {
            e.target.style.opacity = '0.7';
        });
        cropContainer.querySelector('.btn-close-crop').addEventListener('mouseleave', (e) => {
            e.target.style.opacity = '1';
        });
    }
    
    const cropImage = document.getElementById(`cropImage_${fieldName}`);
    const reader = new FileReader();
    reader.onload = function(e) {
        cropImage.src = e.target.result;
        cropContainer.style.display = 'block';
        
        cropImage.onload = function() {
            initCropper(fieldName);
        };
    };
    reader.readAsDataURL(file);
}

function closeCropInline(fieldName) {
    const container = document.querySelector(`[data-field-name="${fieldName}"]`);
    const cropContainer = container.querySelector('.crop-inline-container');
    if (cropContainer) {
        cropContainer.style.display = 'none';
    }
    if (croppers[fieldName]) {
        croppers[fieldName].destroy();
        delete croppers[fieldName];
    }
}

function initCropper(fieldName) {
    const cropImage = document.getElementById(`cropImage_${fieldName}`);
    const container = document.querySelector(`[data-field-name="${fieldName}"]`);
    
    // Default config
    let config = { ratio: 16/9, width: 1920, height: 1080 };
    
    // Override if window.cropConfigs exists
    if (window.cropConfigs && window.cropConfigs[fieldName]) {
        config = window.cropConfigs[fieldName];
    }
    
    if (!cropperLoaded) {
        loadCropperJS(() => {
            createCropper(fieldName, cropImage, config);
        });
    } else {
        createCropper(fieldName, cropImage, config);
    }
}

function loadCropperJS(callback) {
    if (window.Cropper) {
        cropperLoaded = true;
        callback();
        return;
    }
    
    const cropperCSS = document.createElement('link');
    cropperCSS.rel = 'stylesheet';
    cropperCSS.href = 'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.12/cropper.min.css';
    document.head.appendChild(cropperCSS);
    
    const cropperScript = document.createElement('script');
    cropperScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.12/cropper.min.js';
    cropperScript.onload = () => {
        cropperLoaded = true;
        callback();
    };
    cropperScript.onerror = () => {
        console.error('Cropper library failed to load');
    };
    document.head.appendChild(cropperScript);
}

function createCropper(fieldName, cropImage, config) {
    if (croppers[fieldName]) {
        croppers[fieldName].destroy();
    }
    
    // Daire kırpma için özel ayarlar
    const cropperOptions = {
        aspectRatio: config.ratio,
        viewMode: 1,
        dragMode: 'move',
        autoCropArea: 0.8,
        guides: true,
        center: true,
        cropBoxMovable: true,
        cropBoxResizable: true,
        responsive: true
    };
    
    // Eğer rounded flag varsa, daire şeklinde kırp (overlay olmadan)
    if (config.rounded) {
        cropperOptions.cropBoxResizable = false;
        cropperOptions.aspectRatio = 1;
    }
    
    croppers[fieldName] = new Cropper(cropImage, cropperOptions);
}

function applyCrop(fieldName) {
    const cropper = croppers[fieldName];
    
    if (!cropper) {
        console.error('Cropper not initialized');
        return;
    }
    
    const container = document.querySelector(`[data-field-name="${fieldName}"]`);
    const applyBtn = container.querySelector('.btn-apply-crop');
    const cancelBtn = container.querySelector('.btn-cancel-crop');
    
    applyBtn.disabled = true;
    cancelBtn.disabled = true;
    applyBtn.textContent = 'Kırpılıyor...';
    
    // Default config
    let config = { width: 1920, height: 1080 };
    if (window.cropConfigs && window.cropConfigs[fieldName]) {
        config = window.cropConfigs[fieldName];
    }
    
    // ✅ ORİJİNAL DOSYAYI SAKLA (Products & Gallery için)
    const originalFile = container.querySelector('input[type="file"]').files[0];
    
    setTimeout(() => {
        const canvas = cropper.getCroppedCanvas({
            width: config.width,
            height: config.height
        });
        
        // ✅ DAİRE KIRPMA EKLE
        let finalCanvas = canvas;
        
        if (config.rounded) {
            // Daire şeklinde kırp
            finalCanvas = document.createElement('canvas');
            finalCanvas.width = config.width;
            finalCanvas.height = config.height;
            
            const ctx = finalCanvas.getContext('2d');
            
            // Daire maskeleme
            ctx.beginPath();
            ctx.arc(config.width / 2, config.height / 2, config.width / 2, 0, Math.PI * 2);
            ctx.closePath();
            ctx.clip();
            
            // Kırpılmış görseli çiz
            ctx.drawImage(canvas, 0, 0, config.width, config.height);
        }
        
        finalCanvas.toBlob(function(blob) {
            if (!blob) {
                console.error('Failed to create blob');
                applyBtn.disabled = false;
                cancelBtn.disabled = false;
                applyBtn.textContent = 'Kırpmayı Uygula';
                return;
            }
            
            const timestamp = Date.now();
            const croppedFile = new File([blob], `cropped_${timestamp}.jpg`, {
                type: 'image/jpeg',
                lastModified: timestamp
            });
            
            closeCropInline(fieldName);
            
            // ✅ SADECE KIRPILMIŞ DOSYAYI `image` FIELD'INA EKLE
                        // ✅ KIRPILMIŞ DOSYAYI `cropped_image` FIELD'INA, ORİJİNALİ `image` FIELD'INDA BIRAK
            const form = container.closest('form');
            if (form) {
                // 1. Kırpılmış dosyayı cropped_image field'ına yaz
                let croppedImageInput = form.querySelector('input[name="cropped_image"]');
                
                if (!croppedImageInput) {
                    // cropped_image field'ı yoksa oluştur (hidden file input)
                    croppedImageInput = document.createElement('input');
                    croppedImageInput.type = 'file';
                    croppedImageInput.name = 'cropped_image';
                    croppedImageInput.style.display = 'none';
                    form.appendChild(croppedImageInput);
                }
                
                const dtCropped = new DataTransfer();
                dtCropped.items.add(croppedFile);
                croppedImageInput.files = dtCropped.files;
                
                // 2. Orijinal dosyayı image field'ında tut
                const imageInput = document.querySelector(`[data-field-name="${fieldName}"] input[type="file"]`);
                if (imageInput && originalFile) {
                    const dtOriginal = new DataTransfer();
                    dtOriginal.items.add(originalFile);
                    imageInput.files = dtOriginal.files;
                    
                    const changeEvent = new Event('change', { bubbles: true });
                    changeEvent.isCropEvent = true;
                    imageInput.dispatchEvent(changeEvent);
                }
                
                console.log('✅ Kırpılmış dosya: cropped_image field\'ına yazıldı');
                console.log('✅ Orijinal dosya: image field\'ında korundu');
            }

            
            // Success message
            showSuccess(fieldName);
            
        }, 'image/jpeg', 0.9);
    }, 100);
}

function showSuccess(fieldName) {
    const container = document.querySelector(`[data-field-name="${fieldName}"]`);
    if (container) {
        const existingMsg = container.querySelector('.crop-success-message');
        if (existingMsg) existingMsg.remove();
        
        const successMsg = document.createElement('div');
        successMsg.className = 'crop-success-message';
        successMsg.style.cssText = `
            margin-top: 10px;
            padding: 10px 15px;
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            border-radius: 6px;
            font-size: 14px;
            animation: fadeIn 0.3s ease;
        `;
        successMsg.innerHTML = '<span>✅</span> Resim başarıyla kırpıldı!';
        
        container.appendChild(successMsg);
        
        setTimeout(() => {
            if (successMsg.parentNode) {
                successMsg.style.animation = 'fadeOut 0.3s ease';
                setTimeout(() => successMsg.remove(), 300);
            }
        }, 3000);
    }
}

// CSS animations
const style = document.createElement('style');
style.textContent = `
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeOut {
    from { opacity: 1; transform: translateY(0); }
    to { opacity: 0; transform: translateY(-10px); }
}
`;
document.head.appendChild(style);

