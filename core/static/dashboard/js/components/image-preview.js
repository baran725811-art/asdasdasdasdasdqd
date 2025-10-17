// core\static\dashboard\js\components\image-preview.js - Resim önizleme
/**
 * ==========================================================================
 * IMAGE PREVIEW COMPONENT
 * Reusable image preview utilities for file uploads
 * ==========================================================================
 */

class ImagePreview {
    constructor(input, options = {}) {
        this.input = typeof input === 'string' ? document.getElementById(input) : input;
        this.options = {
            maxWidth: 200,
            maxHeight: 200,
            quality: 0.8,
            allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
            maxSize: 5 * 1024 * 1024, // 5MB
            showFileName: true,
            showFileSize: true,
            enableCrop: false,
            previewContainer: null,
            onSelect: null,
            onError: null,
            onRemove: null,
            ...options
        };
        
        this.init();
    }
    
    init() {
        if (!this.input || this.input.type !== 'file') return;
        
        this.createPreviewContainer();
        this.setupEventListeners();
    }
    
    createPreviewContainer() {
        // Use existing container or create new one
        if (this.options.previewContainer) {
            this.previewContainer = typeof this.options.previewContainer === 'string' 
                ? document.getElementById(this.options.previewContainer)
                : this.options.previewContainer;
        } else {
            this.previewContainer = document.createElement('div');
            this.previewContainer.className = 'image-preview-container';
            this.previewContainer.style.cssText = `
                margin-top: 1rem;
                padding: 1rem;
                background: #f8f9fa;
                border-radius: 8px;
                border: 2px dashed #dee2e6;
                text-align: center;
                display: none;
            `;
            
            this.input.parentNode.appendChild(this.previewContainer);
        }
    }
    
    setupEventListeners() {
        this.input.addEventListener('change', (e) => this.handleFileSelect(e));
    }
    
    handleFileSelect(event) {
        const file = event.target.files[0];
        
        if (!file) {
            this.clearPreview();
            return;
        }
        
        // Validate file
        const validation = this.validateFile(file);
        if (!validation.valid) {
            this.showError(validation.message);
            this.input.value = '';
            return;
        }
        
        this.displayPreview(file);
        
        if (this.options.onSelect) {
            this.options.onSelect(file, this);
        }
    }
    
    validateFile(file) {
        // Check file type
        if (!this.options.allowedTypes.includes(file.type)) {
            return {
                valid: false,
                message: `Desteklenen formatlar: ${this.options.allowedTypes.map(type => type.split('/')[1]).join(', ')}`
            };
        }
        
        // Check file size
        if (file.size > this.options.maxSize) {
            const maxSizeMB = (this.options.maxSize / (1024 * 1024)).toFixed(1);
            return {
                valid: false,
                message: `Dosya boyutu ${maxSizeMB}MB'dan küçük olmalıdır.`
            };
        }
        
        return { valid: true };
    }
    
    displayPreview(file) {
        const reader = new FileReader();
        
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                const preview = this.createPreviewElement(img, file);
                this.previewContainer.innerHTML = '';
                this.previewContainer.appendChild(preview);
                this.previewContainer.style.display = 'block';
            };
            img.src = e.target.result;
        };
        
        reader.readAsDataURL(file);
    }
    
    createPreviewElement(img, file) {
        const previewDiv = document.createElement('div');
        previewDiv.className = 'image-preview-item';
        
        // Create canvas for resized image
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Calculate dimensions
        const { width, height } = this.calculateDimensions(img.width, img.height);
        canvas.width = width;
        canvas.height = height;
        
        // Draw resized image
        ctx.drawImage(img, 0, 0, width, height);
        
        // Create preview HTML
        previewDiv.innerHTML = `
            <div class="preview-image-wrapper" style="position: relative; display: inline-block;">
                <img src="${canvas.toDataURL('image/jpeg', this.options.quality)}" 
                     style="max-width: ${this.options.maxWidth}px; max-height: ${this.options.maxHeight}px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);"
                     alt="Preview">
                <button type="button" class="btn-remove-preview" 
                        style="position: absolute; top: -8px; right: -8px; width: 24px; height: 24px; border-radius: 50%; background: #dc3545; border: none; color: white; font-size: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center;"
                        title="Kaldır">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            ${this.options.showFileName ? `<p class="preview-filename" style="margin: 0.5rem 0 0 0; font-size: 0.875rem; color: #6c757d;">${file.name}</p>` : ''}
            ${this.options.showFileSize ? `<p class="preview-filesize" style="margin: 0.25rem 0 0 0; font-size: 0.75rem; color: #6c757d;">${this.formatFileSize(file.size)}</p>` : ''}
        `;
        
        // Add remove functionality
        const removeBtn = previewDiv.querySelector('.btn-remove-preview');
        removeBtn.addEventListener('click', () => this.removePreview());
        
        return previewDiv;
    }
    
    calculateDimensions(originalWidth, originalHeight) {
        const maxWidth = this.options.maxWidth;
        const maxHeight = this.options.maxHeight;
        
        let width = originalWidth;
        let height = originalHeight;
        
        // Scale down if necessary
        if (width > maxWidth) {
            height = (height * maxWidth) / width;
            width = maxWidth;
        }
        
        if (height > maxHeight) {
            width = (width * maxHeight) / height;
            height = maxHeight;
        }
        
        return { width, height };
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    removePreview() {
        this.clearPreview();
        this.input.value = '';
        
        if (this.options.onRemove) {
            this.options.onRemove(this);
        }
    }
    
    clearPreview() {
        if (this.previewContainer) {
            this.previewContainer.innerHTML = '';
            this.previewContainer.style.display = 'none';
        }
    }
    
    showError(message) {
        // Remove existing error
        const existingError = this.input.parentNode.querySelector('.image-preview-error');
        if (existingError) {
            existingError.remove();
        }
        
        // Create error element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'image-preview-error alert alert-danger';
        errorDiv.style.cssText = 'margin-top: 0.5rem; font-size: 0.875rem;';
        errorDiv.innerHTML = `
            <i class="fas fa-exclamation-triangle me-2"></i>
            ${message}
        `;
        
        this.input.parentNode.appendChild(errorDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
        
        if (this.options.onError) {
            this.options.onError(message, this);
        }
    }
    
    // Public methods
    getFile() {
        return this.input.files[0] || null;
    }
    
    reset() {
        this.input.value = '';
        this.clearPreview();
    }
    
    setFile(file) {
        // Create a new FileList with the provided file
        const dt = new DataTransfer();
        dt.items.add(file);
        this.input.files = dt.files;
        this.displayPreview(file);
    }
}

// Drag and Drop Enhancement
class ImageDropZone {
    constructor(element, options = {}) {
        this.element = typeof element === 'string' ? document.getElementById(element) : element;
        this.options = {
            allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
            maxSize: 5 * 1024 * 1024,
            multiple: false,
            onDrop: null,
            onDragEnter: null,
            onDragLeave: null,
            ...options
        };
        
        this.init();
    }
    
    init() {
        if (!this.element) return;
        
        this.setupDropZone();
        this.setupEventListeners();
    }
    
    setupDropZone() {
        this.element.style.cursor = 'pointer';
        this.element.setAttribute('tabindex', '0');
        
        // Add visual feedback styles
        this.element.style.transition = 'all 0.3s ease';
    }
    
    setupEventListeners() {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.element.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });
        
        // Highlight drop area when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            this.element.addEventListener(eventName, () => this.highlight(), false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            this.element.addEventListener(eventName, () => this.unhighlight(), false);
        });
        
        // Handle dropped files
        this.element.addEventListener('drop', (e) => this.handleDrop(e), false);
        
        // Click to select files
        this.element.addEventListener('click', () => this.openFileSelector());
        
        // Keyboard accessibility
        this.element.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.openFileSelector();
            }
        });
    }
    
    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    highlight() {
        this.element.style.backgroundColor = 'rgba(102, 126, 234, 0.1)';
        this.element.style.borderColor = 'var(--primary-color)';
        this.element.style.transform = 'scale(1.02)';
        
        if (this.options.onDragEnter) {
            this.options.onDragEnter(this);
        }
    }
    
    unhighlight() {
        this.element.style.backgroundColor = '';
        this.element.style.borderColor = '';
        this.element.style.transform = '';
        
        if (this.options.onDragLeave) {
            this.options.onDragLeave(this);
        }
    }
    
    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        this.handleFiles(files);
    }
    
    handleFiles(files) {
        const fileList = Array.from(files);
        
        if (!this.options.multiple && fileList.length > 1) {
            this.showError('Tek seferde sadece bir dosya seçebilirsiniz.');
            return;
        }
        
        const validFiles = fileList.filter(file => this.validateFile(file));
        
        if (validFiles.length > 0 && this.options.onDrop) {
            this.options.onDrop(validFiles, this);
        }
    }
    
    validateFile(file) {
        // Check file type
        if (!this.options.allowedTypes.includes(file.type)) {
            this.showError(`Desteklenen formatlar: ${this.options.allowedTypes.map(type => type.split('/')[1]).join(', ')}`);
            return false;
        }
        
        // Check file size
        if (file.size > this.options.maxSize) {
            const maxSizeMB = (this.options.maxSize / (1024 * 1024)).toFixed(1);
            this.showError(`Dosya boyutu ${maxSizeMB}MB'dan küçük olmalıdır.`);
            return false;
        }
        
        return true;
    }
    
    openFileSelector() {
        // Create hidden file input
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = this.options.allowedTypes.join(',');
        input.multiple = this.options.multiple;
        
        input.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFiles(e.target.files);
            }
        });
        
        input.click();
    }
    
    showError(message) {
        // Create temporary error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'drop-zone-error';
        errorDiv.style.cssText = `
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #dc3545;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 0.875rem;
            z-index: 1000;
            box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
        `;
        errorDiv.textContent = message;
        
        document.body.appendChild(errorDiv);
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 3000);
    }
}

// Auto-initialize image previews
document.addEventListener('DOMContentLoaded', function() {
    // Auto-initialize file inputs with data-preview attribute
    const imageInputs = document.querySelectorAll('input[type="file"][data-preview="true"]');
    imageInputs.forEach(input => {
        new ImagePreview(input);
    });
    
    // Auto-initialize drop zones
    const dropZones = document.querySelectorAll('[data-drop-zone="true"]');
    dropZones.forEach(zone => {
        const fileInput = zone.querySelector('input[type="file"]');
        if (fileInput) {
            new ImageDropZone(zone, {
                onDrop: (files) => {
                    // Set files to the input
                    const dt = new DataTransfer();
                    files.forEach(file => dt.items.add(file));
                    fileInput.files = dt.files;
                    
                    // Trigger change event
                    fileInput.dispatchEvent(new Event('change', { bubbles: true }));
                }
            });
        }
    });
});

// Export for use in other modules
window.ImagePreview = ImagePreview;
window.ImageDropZone = ImageDropZone;