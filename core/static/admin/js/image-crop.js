/**core\static\admin\js\image-crop.js
 * Modern Image Crop Functionality
 * Professional and minimalist cropping interface
 */

document.addEventListener('DOMContentLoaded', function() {
    initImageCropWidgets();
});

let croppers = {};
let cropperLoaded = false;

/**
 * Initialize all image crop widgets on the page
 */
function initImageCropWidgets() {
    const cropContainers = document.querySelectorAll('.image-crop-container');
    
    cropContainers.forEach(container => {
        const fieldName = container.dataset.fieldName;
        const cropType = container.dataset.cropType;
        const fileInput = container.querySelector('input[type="file"]');
        
        if (fileInput) {
            // Handle file selection
            fileInput.addEventListener('change', function(e) {
                // Skip if this is from a crop operation
                if (e.isCropEvent) return;
                
                const file = e.target.files[0];
                if (file && file.type.startsWith('image/')) {
                    openCropModal(fieldName, file);
                }
            });
            
            // Add crop button to existing images
            addCropButtonToExisting(container, fieldName);
        }
    });
}

/**
 * Add crop button to existing images
 */
function addCropButtonToExisting(container, fieldName) {
    const currentLink = container.querySelector('a[target="_blank"]');
    
    if (currentLink) {
        const cropBtn = document.createElement('button');
        cropBtn.type = 'button';
        cropBtn.className = 'crop-trigger-btn';
        cropBtn.innerHTML = '<span>✂️</span> Resmi Yeniden Kırp';
        cropBtn.onclick = () => {
            loadExistingImageForCrop(fieldName, currentLink.href);
        };
        
        currentLink.parentNode.appendChild(cropBtn);
    }
}

/**
 * Load existing image for cropping
 */
function loadExistingImageForCrop(fieldName, imageUrl) {
    // Show loading state
    showLoadingState(fieldName);
    
    fetch(imageUrl)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.blob();
        })
        .then(blob => {
            const file = new File([blob], 'existing-image', { type: blob.type });
            hideLoadingState(fieldName);
            openCropModal(fieldName, file);
        })
        .catch(error => {
            hideLoadingState(fieldName);
            console.error('Failed to load existing image:', error);
            showNotification('Mevcut resim yüklenirken hata oluştu.', 'error');
        });
}

/**
 * Show loading state
 */
function showLoadingState(fieldName) {
    const btn = document.querySelector(`[data-field-name="${fieldName}"] .crop-trigger-btn`);
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span>⏳</span> Yükleniyor...';
    }
}

/**
 * Hide loading state
 */
function hideLoadingState(fieldName) {
    const btn = document.querySelector(`[data-field-name="${fieldName}"] .crop-trigger-btn`);
    if (btn) {
        btn.disabled = false;
        btn.innerHTML = '<span>✂️</span> Resmi Yeniden Kırp';
    }
}

/**
 * Open crop modal
 */
function openCropModal(fieldName, file) {
    const modal = document.getElementById(`cropModal_${fieldName}`);
    const cropImage = document.getElementById(`cropImage_${fieldName}`);
    const config = window.cropConfigs[fieldName];
    const container = document.querySelector(`[data-field-name="${fieldName}"]`);
    
    if (!modal || !cropImage || !config || !container) {
        console.error('Crop modal components not found');
        return;
    }
    
    // Clean up any existing cropper first
    if (croppers[fieldName]) {
        croppers[fieldName].destroy();
        delete croppers[fieldName];
    }
    
    // Reset modal state
    modal.style.display = 'none';
    
    // Set crop type for preview
    const cropType = container.dataset.cropType || 'default';
    const preview = document.getElementById(`cropPreview_${fieldName}`);
    if (preview) {
        preview.setAttribute('data-crop-type', cropType);
        preview.classList.remove('has-content');
        preview.innerHTML = 'Kırpma alanını seçin';
    }
    
    // Reset buttons
    const applyBtn = document.querySelector(`#cropModal_${fieldName} .btn-crop-apply`);
    const cancelBtn = document.querySelector(`#cropModal_${fieldName} .btn-crop-cancel`);
    if (applyBtn) {
        applyBtn.disabled = false;
        applyBtn.innerHTML = 'Kırpmayı Uygula';
    }
    if (cancelBtn) {
        cancelBtn.disabled = false;
    }
    
    // Read file and open modal
    const reader = new FileReader();
    reader.onload = function(e) {
        cropImage.src = e.target.result;
        modal.style.display = 'flex';
        
        // Initialize cropper after image loads
        cropImage.onload = function() {
            initCropper(fieldName, config);
        };
    };
    
    reader.readAsDataURL(file);
}

/**
 * Initialize Cropper.js
 */
function initCropper(fieldName, config) {
    const cropImage = document.getElementById(`cropImage_${fieldName}`);
    
    if (!cropperLoaded) {
        loadCropperJS(() => {
            createCropper(fieldName, cropImage, config);
        });
    } else {
        createCropper(fieldName, cropImage, config);
    }
}

/**
 * Load Cropper.js library
 */
function loadCropperJS(callback) {
    if (window.Cropper) {
        cropperLoaded = true;
        callback();
        return;
    }
    
    // Load CSS
    const cropperCSS = document.createElement('link');
    cropperCSS.rel = 'stylesheet';
    cropperCSS.href = 'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.12/cropper.min.css';
    document.head.appendChild(cropperCSS);
    
    // Load JS
    const cropperScript = document.createElement('script');
    cropperScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.12/cropper.min.js';
    cropperScript.onload = () => {
        cropperLoaded = true;
        callback();
    };
    cropperScript.onerror = () => {
        showNotification('Cropper kütüphanesi yüklenemedi.', 'error');
    };
    document.head.appendChild(cropperScript);
}

/**
 * Create cropper instance (optimized)
 */
function createCropper(fieldName, cropImage, config) {
    const container = document.querySelector(`[data-field-name="${fieldName}"]`);
    const cropType = container?.dataset.cropType || 'default';
    
    // Clean up any existing timeout
    if (window.cropUpdateTimeouts && window.cropUpdateTimeouts[fieldName]) {
        clearTimeout(window.cropUpdateTimeouts[fieldName]);
    }
    
    // Initialize timeout storage
    window.cropUpdateTimeouts = window.cropUpdateTimeouts || {};
    
    croppers[fieldName] = new Cropper(cropImage, {
        aspectRatio: config.ratio,
        viewMode: 1,
        dragMode: 'move',
        autoCropArea: 0.8,
        restore: false,
        guides: true,
        center: true,
        highlight: false,
        cropBoxMovable: true,
        cropBoxResizable: true,
        toggleDragModeOnDblclick: false,
        minContainerWidth: 200,
        minContainerHeight: 200,
        responsive: true,
        checkCrossOrigin: false,
        
        ready: function() {
            // Initial preview update
            updateCropPreview(fieldName, this.cropper.getData());
        },
        
        crop: function(event) {
            // Debounce preview updates for smooth performance
            clearTimeout(window.cropUpdateTimeouts[fieldName]);
            window.cropUpdateTimeouts[fieldName] = setTimeout(() => {
                updateCropPreview(fieldName, event.detail);
            }, 100); // 100ms delay
        }
    });
}

/**
 * Update crop preview (optimized)
 */
function updateCropPreview(fieldName, cropData) {
    const preview = document.getElementById(`cropPreview_${fieldName}`);
    const container = document.querySelector(`[data-field-name="${fieldName}"]`);
    
    if (!preview || !container || !croppers[fieldName]) return;
    
    const cropType = container.dataset.cropType || 'default';
    
    // Preview sizes for different crop types (smaller for performance)
    const previewSizes = {
        'carousel': { width: 200, height: 112 },
        'gallery': { width: 200, height: 150 },
        'products': { width: 200, height: 133 },
        'categories': { width: 200, height: 125 },
        'about': { width: 200, height: 150 },
        'services': { width: 200, height: 125 },
        'team': { width: 150, height: 150 },
        'reviews': { width: 80, height: 80 },
        'media': { width: 200, height: 125 },
        'default': { width: 200, height: 150 }
    };
    
    const previewSize = previewSizes[cropType] || previewSizes['default'];
    
    try {
        // Create small preview canvas for better performance
        const canvas = croppers[fieldName].getCroppedCanvas({
            width: previewSize.width,
            height: previewSize.height,
            imageSmoothingEnabled: false // Faster for preview
        });
        
        preview.innerHTML = '';
        preview.appendChild(canvas);
        preview.classList.add('has-content');
        
        // Store crop data
        const cropDataInput = document.getElementById(`cropData_${fieldName}`);
        if (cropDataInput) {
            cropDataInput.value = JSON.stringify({
                x: Math.round(cropData.x),
                y: Math.round(cropData.y),
                width: Math.round(cropData.width),
                height: Math.round(cropData.height),
                rotate: cropData.rotate || 0,
                scaleX: cropData.scaleX || 1,
                scaleY: cropData.scaleY || 1
            });
        }
    } catch (error) {
        console.error('Preview update failed:', error);
        preview.innerHTML = 'Önizleme hazırlanıyor...';
        preview.classList.remove('has-content');
    }
}

/**
 * Apply crop and save
 */
function applyCrop(fieldName) {
    const cropper = croppers[fieldName];
    const config = window.cropConfigs[fieldName];
    
    if (!cropper) {
        showNotification('Kırpma işlemi başlatılmamış', 'error');
        return;
    }
    
    // Show processing state
    const applyBtn = document.querySelector(`#cropModal_${fieldName} .btn-crop-apply`);
    const cancelBtn = document.querySelector(`#cropModal_${fieldName} .btn-crop-cancel`);
    const originalText = applyBtn.innerHTML;
    
    applyBtn.disabled = true;
    cancelBtn.disabled = true;
    applyBtn.innerHTML = 'Kırpılıyor...';
    
    // Use setTimeout to allow UI update before heavy operation
    setTimeout(() => {
        try {
            // Optimize canvas size for faster processing
            const maxDimension = Math.max(config.width, config.height);
            let outputWidth = config.width;
            let outputHeight = config.height;
            
            // For very large images, create in steps
            if (maxDimension > 2000) {
                const scale = 2000 / maxDimension;
                outputWidth = Math.round(config.width * scale);
                outputHeight = Math.round(config.height * scale);
            }
            
            // Create canvas with optimized settings
            const canvas = cropper.getCroppedCanvas({
                width: outputWidth,
                height: outputHeight,
                imageSmoothingEnabled: false, // Disable for speed
                fillColor: '#fff'
            });
            
            // If we scaled down, create final canvas at target size
            let finalCanvas = canvas;
            if (outputWidth !== config.width || outputHeight !== config.height) {
                finalCanvas = document.createElement('canvas');
                finalCanvas.width = config.width;
                finalCanvas.height = config.height;
                const ctx = finalCanvas.getContext('2d');
                ctx.imageSmoothingEnabled = true;
                ctx.imageSmoothingQuality = 'high';
                ctx.drawImage(canvas, 0, 0, config.width, config.height);
            }
            
            // Convert to blob with lower quality for speed
            finalCanvas.toBlob(function(blob) {
                if (!blob) {
                    showNotification('Resim işlenirken hata oluştu', 'error');
                    applyBtn.disabled = false;
                    cancelBtn.disabled = false;
                    applyBtn.innerHTML = originalText;
                    return;
                }
                
                // Create file
                const timestamp = Date.now();
                const croppedFile = new File([blob], `cropped_${timestamp}.jpg`, {
                    type: 'image/jpeg',
                    lastModified: timestamp
                });
                
                // Close modal FIRST to prevent state conflicts
                closeCropModal(fieldName);
                
                // THEN update file input
                const fileInput = document.querySelector(`[data-field-name="${fieldName}"] input[type="file"]`);
                if (fileInput) {
                    const dt = new DataTransfer();
                    dt.items.add(croppedFile);
                    fileInput.files = dt.files;
                    
                    // Trigger change event with crop flag to prevent modal reopening
                    const changeEvent = new Event('change', { bubbles: true });
                    changeEvent.isCropEvent = true; // Custom flag to prevent reopening modal
                    fileInput.dispatchEvent(changeEvent);
                }
                
                // Show success message
                showCropSuccess(fieldName);
                
            }, 'image/jpeg', 0.85); // Lower quality for speed
            
        } catch (error) {
            console.error('Crop apply failed:', error);
            showNotification('Kırpma işlemi başarısız oldu', 'error');
            applyBtn.disabled = false;
            cancelBtn.disabled = false;
            applyBtn.innerHTML = originalText;
        }
    }, 50); // Small delay to allow UI update
}

/**
 * Close crop modal
 */
function closeCropModal(fieldName) {
    const modal = document.getElementById(`cropModal_${fieldName}`);
    if (modal) {
        modal.style.display = 'none';
    }
    
    // Clean up cropper completely
    if (croppers[fieldName]) {
        croppers[fieldName].destroy();
        delete croppers[fieldName];
    }
    
    // Reset modal elements
    const preview = document.getElementById(`cropPreview_${fieldName}`);
    if (preview) {
        preview.classList.remove('has-content');
        preview.innerHTML = 'Kırpma alanını seçin';
    }
    
    // Reset buttons
    const applyBtn = document.querySelector(`#cropModal_${fieldName} .btn-crop-apply`);
    const cancelBtn = document.querySelector(`#cropModal_${fieldName} .btn-crop-cancel`);
    if (applyBtn) {
        applyBtn.disabled = false;
        applyBtn.innerHTML = 'Kırpmayı Uygula';
    }
    if (cancelBtn) {
        cancelBtn.disabled = false;
    }
    
    // Clear image source
    const cropImage = document.getElementById(`cropImage_${fieldName}`);
    if (cropImage) {
        cropImage.src = '';
        cropImage.onload = null;
    }
}

/**
 * Show crop success message
 */
function showCropSuccess(fieldName) {
    const container = document.querySelector(`[data-field-name="${fieldName}"]`);
    if (container) {
        // Remove existing success message
        const existingMsg = container.querySelector('.crop-success-message');
        if (existingMsg) {
            existingMsg.remove();
        }
        
        const successMsg = document.createElement('div');
        successMsg.className = 'crop-success-message';
        successMsg.innerHTML = '<span>✅</span> Resim başarıyla kırpıldı!';
        
        container.appendChild(successMsg);
        
        // Auto remove after 4 seconds
        setTimeout(() => {
            if (successMsg.parentNode) {
                successMsg.style.animation = 'slideOutDown 0.3s ease-in forwards';
                setTimeout(() => successMsg.remove(), 300);
            }
        }, 4000);
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    // Create notification if doesn't exist
    let notification = document.querySelector('.crop-notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.className = 'crop-notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        document.body.appendChild(notification);
    }
    
    // Set notification style based on type
    const styles = {
        success: { background: '#ecfdf5', color: '#065f46', border: '1px solid #a7f3d0' },
        error: { background: '#fef2f2', color: '#991b1b', border: '1px solid #fca5a5' },
        info: { background: '#eff6ff', color: '#1e40af', border: '1px solid #93c5fd' }
    };
    
    const style = styles[type] || styles.info;
    Object.assign(notification.style, style);
    
    notification.textContent = message;
    
    // Show notification
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Hide after 3 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 3000);
}

// Event Listeners

// Close modal when clicking outside
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('crop-modal')) {
        const fieldName = e.target.id.replace('cropModal_', '');
        closeCropModal(fieldName);
    }
});

// Close modal with ESC key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        Object.keys(croppers).forEach(fieldName => {
            closeCropModal(fieldName);
        });
    }
});

// Prevent modal content clicks from closing modal
document.addEventListener('click', function(e) {
    if (e.target.closest('.crop-modal-content')) {
        e.stopPropagation();
    }
});

// Add CSS animations for slide effects
const slideAnimations = `
@keyframes slideOutDown {
    from {
        opacity: 1;
        transform: translateY(0);
    }
    to {
        opacity: 0;
        transform: translateY(20px);
    }
}
`;

// Inject animations if not already present
if (!document.querySelector('#crop-animations')) {
    const style = document.createElement('style');
    style.id = 'crop-animations';
    style.textContent = slideAnimations;
    document.head.appendChild(style);
}