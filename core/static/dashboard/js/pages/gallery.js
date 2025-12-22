// core\static\dashboard\js\pages\gallery.js - Galeri yönetimi
/**
 * ==========================================================================
 * GALLERY PAGE JAVASCRIPT
 * Gallery management page functionality
 * ==========================================================================
 */

class GalleryManager {
    constructor() {
        this.currentView = 'grid';
        this.currentFilter = {};
        this.lazyLoadObserver = null;
        this.init();
    }
    
    init() {
        console.log('🖼️ Gallery Manager initializing...');
        
        this.setupViewToggle();
        this.setupFilterForm();
        this.setupMediaTypeToggle();
        this.setupEditModal();
        this.setupViewer();
        this.setupLazyLoading();
        this.loadSavedPreferences();
        
        console.log('✅ Gallery Manager initialized successfully');
    }
    
    setupViewToggle() {
        const viewToggleInputs = document.querySelectorAll('input[name="view-type"]');
        
        viewToggleInputs.forEach(input => {
            input.addEventListener('change', () => {
                if (input.checked) {
                    this.toggleView(input.value);
                }
            });
        });
        
        // Setup view toggle buttons (alternative implementation)
        const gridViewBtn = document.getElementById('gridView');
        const listViewBtn = document.getElementById('listView');
        
        if (gridViewBtn) {
            gridViewBtn.addEventListener('change', () => {
                if (gridViewBtn.checked) {
                    this.toggleView('grid');
                }
            });
        }
        
        if (listViewBtn) {
            listViewBtn.addEventListener('change', () => {
                if (listViewBtn.checked) {
                    this.toggleView('list');
                }
            });
        }
    }
    
    toggleView(viewType) {
        const container = document.getElementById('galleryContainer');
        if (!container) return;
        
        console.log(`🔄 Switching to ${viewType} view`);
        
        // Remove existing view classes
        container.classList.remove('gallery-grid', 'gallery-list', 'gallery-masonry');
        
        // Add new view class
        switch (viewType) {
            case 'list':
                container.classList.add('gallery-list');
                break;
            case 'masonry':
                container.classList.add('gallery-masonry');
                this.setupMasonry();
                break;
            default:
                container.classList.add('gallery-grid');
        }
        
        this.currentView = viewType;
        
        // Save preference
        localStorage.setItem('galleryViewType', viewType);
        
        // Trigger lazy loading check
        this.checkLazyLoading();
    }
    
    setupFilterForm() {
        const filterForm = document.getElementById('filterForm');
        const filterInputs = filterForm?.querySelectorAll('select, input');
        
        if (!filterForm) return;
        
        filterInputs.forEach(input => {
            if (input.type !== 'submit') {
                input.addEventListener('change', () => {
                    if (input.name === 'search') {
                        clearTimeout(this.searchTimeout);
                        this.searchTimeout = setTimeout(() => this.applyFilters(), 500);
                    } else {
                        setTimeout(() => this.applyFilters(), 300);
                    }
                });
            }
        });
        
        // Reset filters button
        const resetBtn = document.getElementById('resetFiltersBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetFilters());
        }
        
        // Advanced filters toggle
        const advancedToggle = document.getElementById('advancedFiltersToggle');
        if (advancedToggle) {
            advancedToggle.addEventListener('click', () => this.toggleAdvancedFilters());
        }
    }
    
    applyFilters() {
        const filterForm = document.getElementById('filterForm');
        if (!filterForm) return;
        
        console.log('🔍 Applying filters...');
        
        // Show loading state
        this.showFilteringState(true);
        
        // Get filter values
        const formData = new FormData(filterForm);
        const filters = {};
        
        for (let [key, value] of formData.entries()) {
            if (value.trim()) {
                filters[key] = value;
            }
        }
        
        this.currentFilter = filters;
        
        // Apply filters to gallery items
        this.filterGalleryItems(filters);
        
        // Update URL without page reload
        this.updateFilterURL(filters);
        
        setTimeout(() => {
            this.showFilteringState(false);
        }, 500);
    }
    
    filterGalleryItems(filters) {
        const galleryItems = document.querySelectorAll('.gallery-item');
        let visibleCount = 0;
        
        galleryItems.forEach(item => {
            let show = true;
            
            // Search filter
            if (filters.search) {
                const title = item.querySelector('.gallery-title')?.textContent.toLowerCase() || '';
                const description = item.querySelector('.gallery-description')?.textContent.toLowerCase() || '';
                const searchTerm = filters.search.toLowerCase();
                
                if (!title.includes(searchTerm) && !description.includes(searchTerm)) {
                    show = false;
                }
            }
            
            // Media type filter
            if (filters.media_type && filters.media_type !== 'all') {
                const mediaType = item.dataset.mediaType;
                if (mediaType !== filters.media_type) {
                    show = false;
                }
            }
            
            // Category filter
            if (filters.category && filters.category !== 'all') {
                const category = item.dataset.category;
                if (category !== filters.category) {
                    show = false;
                }
            }
            
            // Date filter
            if (filters.date_from || filters.date_to) {
                const itemDate = new Date(item.dataset.date);
                
                if (filters.date_from) {
                    const fromDate = new Date(filters.date_from);
                    if (itemDate < fromDate) {
                        show = false;
                    }
                }
                
                if (filters.date_to) {
                    const toDate = new Date(filters.date_to);
                    if (itemDate > toDate) {
                        show = false;
                    }
                }
            }
            
            // Status filter
            if (filters.status && filters.status !== 'all') {
                const status = item.dataset.status;
                if (status !== filters.status) {
                    show = false;
                }
            }
            
            // Show/hide item
            item.style.display = show ? '' : 'none';
            if (show) visibleCount++;
        });
        
        // Update results count
        this.updateResultsCount(visibleCount);
        
        // Show empty state if no results
        this.toggleEmptyState(visibleCount === 0);
    }
    
    updateResultsCount(count) {
        const countElement = document.getElementById('resultsCount');
        if (countElement) {
            countElement.textContent = `${count} öğe gösteriliyor`;
        }
    }
    
    toggleEmptyState(show) {
        const container = document.getElementById('galleryContainer');
        const emptyState = document.getElementById('galleryEmptyState');
        
        if (show) {
            if (!emptyState) {
                this.createEmptyState();
            } else {
                emptyState.style.display = 'block';
            }
            container.style.display = 'none';
        } else {
            if (emptyState) {
                emptyState.style.display = 'none';
            }
            container.style.display = '';
        }
    }
    
    createEmptyState() {
        const emptyDiv = document.createElement('div');
        emptyDiv.id = 'galleryEmptyState';
        emptyDiv.className = 'gallery-empty';
        emptyDiv.innerHTML = `
            <div class="gallery-empty-icon">
                <i class="fas fa-search"></i>
            </div>
            <h4>Sonuç bulunamadı</h4>
            <p>Arama kriterlerinize uygun medya bulunamadı.</p>
            <button class="btn btn-primary" onclick="galleryManager.resetFilters()">
                <i class="fas fa-refresh me-1"></i>Filtreleri Temizle
            </button>
        `;
        
        const container = document.getElementById('galleryContainer');
        container.parentNode.insertBefore(emptyDiv, container.nextSibling);
    }
    
    resetFilters() {
        const filterForm = document.getElementById('filterForm');
        if (!filterForm) return;
        
        console.log('🧹 Resetting filters...');
        
        // Reset form inputs
        filterForm.querySelectorAll('select, input[type="text"], input[type="date"]').forEach(input => {
            if (input.type === 'select-one') {
                input.selectedIndex = 0;
            } else {
                input.value = '';
            }
        });
        
        // Clear current filter
        this.currentFilter = {};
        
        // Show all items
        document.querySelectorAll('.gallery-item').forEach(item => {
            item.style.display = '';
        });
        
        // Update results count
        const totalCount = document.querySelectorAll('.gallery-item').length;
        this.updateResultsCount(totalCount);
        
        // Hide empty state
        this.toggleEmptyState(false);
        
        // Update URL
        this.updateFilterURL({});
    }
    
    updateFilterURL(filters) {
        const url = new URL(window.location);
        
        // Clear existing filter params
        ['search', 'media_type', 'category', 'date_from', 'date_to', 'status'].forEach(param => {
            url.searchParams.delete(param);
        });
        
        // Add new filter params
        Object.keys(filters).forEach(key => {
            if (filters[key]) {
                url.searchParams.set(key, filters[key]);
            }
        });
        
        // Update URL without page reload
        window.history.replaceState({}, '', url);
    }
    
    showFilteringState(show) {
        const container = document.getElementById('galleryContainer');
        if (show) {
            container.classList.add('filtering');
        } else {
            container.classList.remove('filtering');
        }
    }
    
    setupMediaTypeToggle() {
        // Add modal media type toggle
        const addMediaType = document.getElementById('add_media_type');
        if (addMediaType) {
            addMediaType.addEventListener('change', () => {
                this.toggleMediaFields('add', addMediaType.value);
            });
        }
    }
    
    toggleMediaFields(prefix, mediaType, itemId = '') {
        const suffix = itemId ? '_' + itemId : '';
        const imageField = document.getElementById(prefix + '_image_field' + suffix);
        const videoField = document.getElementById(prefix + '_video_field' + suffix);
        
        if (!imageField || !videoField) return;
        
        if (mediaType === 'video') {
            imageField.style.display = 'none';
            videoField.style.display = 'block';
            const imageInput = document.getElementById(prefix + '_image' + suffix);
            if (imageInput) imageInput.removeAttribute('required');
        } else {
            imageField.style.display = 'block';
            videoField.style.display = 'none';
            if (prefix === 'add') {
                const imageInput = document.getElementById(prefix + '_image');
                if (imageInput) imageInput.setAttribute('required', 'required');
            }
        }
    }
    
    setupEditModal() {
        // Setup edit gallery functionality
        window.editGallery = (galleryId) => this.editGallery(galleryId);
        window.viewGalleryItem = (itemId, mediaType, mediaUrl) => this.viewGalleryItem(itemId, mediaType, mediaUrl);
    }
    
    editGallery(galleryId) {
        const editButton = document.querySelector(`button[onclick="editGallery(${galleryId})"]`);
        const editUrl = editButton?.getAttribute('data-edit-url') || `/dashboard/gallery/edit/${galleryId}/`;
        
        console.log('🔧 Editing gallery:', galleryId, 'URL:', editUrl);
        
        fetch(editUrl, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': this.getCSRFToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('editModalContent').innerHTML = data.modal_content;
            const editModal = new bootstrap.Modal(document.getElementById('editGalleryModal'));
            editModal.show();
            
            // Setup form submit handler
            const editForm = document.getElementById('editGalleryForm');
            if (editForm) {
                editForm.addEventListener('submit', (e) => {
                    e.preventDefault();
                    this.submitEditForm(galleryId);
                });
            }
            
            // Setup media type toggle for edit modal
            const editMediaType = document.getElementById(`edit_media_type_${galleryId}`);
            if (editMediaType) {
                editMediaType.addEventListener('change', () => {
                    this.toggleMediaFields('edit', editMediaType.value, galleryId);
                });
                
                // Initialize with current value
                this.toggleMediaFields('edit', editMediaType.value, galleryId);
            }
            
            console.log('✅ Edit modal loaded successfully');
        })
        .catch(error => {
            console.error('❌ Edit error:', error);
            this.showNotification('Bir hata oluştu!', 'error');
        });
    }
    
    submitEditForm(galleryId) {
        const form = document.getElementById('editGalleryForm');
        const formData = new FormData(form);
        const editButton = document.querySelector(`button[onclick="editGallery(${galleryId})"]`);
        const editUrl = editButton?.getAttribute('data-edit-url') || `/dashboard/gallery/edit/${galleryId}/`;
        
        fetch(editUrl, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': this.getCSRFToken()
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const editModal = bootstrap.Modal.getInstance(document.getElementById('editGalleryModal'));
                editModal.hide();
                this.showNotification('Medya başarıyla güncellendi.', 'success');
                setTimeout(() => location.reload(), 1000);
            } else {
                this.showNotification('Form hatası! Lütfen alanları kontrol edin.', 'error');
                console.error(data.errors);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            this.showNotification('Bir hata oluştu!', 'error');
        });
    }
    
    setupViewer() {
        // Setup gallery viewer modal
        window.viewGalleryItem = (itemId, mediaType, mediaUrl) => this.viewGalleryItem(itemId, mediaType, mediaUrl);
    }
    
    viewGalleryItem(itemId, mediaType, mediaUrl) {
        const modal = document.getElementById('viewerModal');
        const content = document.getElementById('viewerContent');
        
        if (!modal || !content) {
            console.error('Viewer modal elements not found');
            return;
        }
        
        console.log(`👁️ Viewing ${mediaType}: ${mediaUrl}`);
        
        if (mediaType === 'image') {
            content.innerHTML = `
                <img src="${mediaUrl}" 
                     class="img-fluid" 
                     style="max-height: 80vh; max-width: 100%; object-fit: contain;"
                     alt="Gallery Image">
            `;
        } else if (mediaType === 'video') {
            let embedUrl = mediaUrl;
            
            // Handle YouTube URLs
            if (mediaUrl.includes('youtube.com/watch?v=')) {
                const videoId = mediaUrl.split('v=')[1].split('&')[0];
                embedUrl = `https://www.youtube.com/embed/${videoId}`;
            } else if (mediaUrl.includes('youtu.be/')) {
                const videoId = mediaUrl.split('/').pop();
                embedUrl = `https://www.youtube.com/embed/${videoId}`;
            }
            // Handle Vimeo URLs
            else if (mediaUrl.includes('vimeo.com/')) {
                const videoId = mediaUrl.split('/').pop();
                embedUrl = `https://player.vimeo.com/video/${videoId}`;
            }
            
            content.innerHTML = `
                <div class="ratio ratio-16x9">
                    <iframe src="${embedUrl}" 
                            allowfullscreen 
                            frameborder="0"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture">
                    </iframe>
                </div>
            `;
        }
        
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    }
    
    setupLazyLoading() {
        if ('IntersectionObserver' in window) {
            this.lazyLoadObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.loadGalleryItem(entry.target);
                        this.lazyLoadObserver.unobserve(entry.target);
                    }
                });
            }, {
                rootMargin: '50px 0px'
            });
            
            this.checkLazyLoading();
        }
    }
    
    checkLazyLoading() {
        const lazyItems = document.querySelectorAll('.gallery-item[data-loaded="false"]');
        lazyItems.forEach(item => {
            if (this.lazyLoadObserver) {
                this.lazyLoadObserver.observe(item);
            } else {
                this.loadGalleryItem(item);
            }
        });
    }
    
    loadGalleryItem(item) {
        const img = item.querySelector('img[data-src]');
        if (img) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
            
            img.addEventListener('load', () => {
                item.setAttribute('data-loaded', 'true');
                item.classList.add('loaded');
            });
            
            img.addEventListener('error', () => {
                item.classList.add('error');
                img.src = '/static/images/placeholder.jpg'; // Fallback image
            });
        } else {
            item.setAttribute('data-loaded', 'true');
        }
    }
    
    setupMasonry() {
        // Simple masonry layout implementation
        if (this.currentView === 'masonry') {
            const container = document.getElementById('galleryContainer');
            if (container && CSS.supports('column-count', '1')) {
                container.style.columnCount = 'auto';
                container.style.columnWidth = '280px';
                container.style.columnGap = '1.5rem';
                
                // Prevent breaking inside items
                const items = container.querySelectorAll('.gallery-item');
                items.forEach(item => {
                    item.style.breakInside = 'avoid';
                    item.style.marginBottom = '1.5rem';
                });
            }
        }
    }
    
    loadSavedPreferences() {
        // Load saved view type
        const savedViewType = localStorage.getItem('galleryViewType');
        if (savedViewType && ['grid', 'list', 'masonry'].includes(savedViewType)) {
            const viewInput = document.querySelector(`input[value="${savedViewType}"]`);
            if (viewInput) {
                viewInput.checked = true;
                this.toggleView(savedViewType);
            }
        }
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        const icon = type === 'success' ? 'check-circle' : 
                    type === 'error' ? 'exclamation-circle' : 
                    type === 'warning' ? 'exclamation-triangle' : 'info-circle';
        
        notification.innerHTML = `
            <i class="fas fa-${icon} me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }
    
    // Public methods
    refreshGallery() {
        console.log('🔄 Refreshing gallery...');
        this.applyFilters();
        this.checkLazyLoading();
        this.showNotification('Galeri güncellendi.', 'success');
    }
    
    exportGalleryData() {
        const visibleItems = Array.from(document.querySelectorAll('.gallery-item')).filter(item => 
            item.style.display !== 'none'
        );
        
        const data = visibleItems.map(item => ({
            title: item.querySelector('.gallery-title')?.textContent || '',
            description: item.querySelector('.gallery-description')?.textContent || '',
            mediaType: item.dataset.mediaType || '',
            category: item.dataset.category || '',
            date: item.dataset.date || ''
        }));
        
        const csv = 'Başlık,Açıklama,Medya Tipi,Kategori,Tarih\n' + 
                   data.map(row => `"${row.title}","${row.description}","${row.mediaType}","${row.category}","${row.date}"`).join('\n');
        
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = 'galeri-verileri-' + new Date().toISOString().split('T')[0] + '.csv';
        link.click();
        
        this.showNotification('Veriler başarıyla indirildi.', 'success');
    }
}

// Gallery utilities
const GalleryUtils = {
    // Generate thumbnail from video URL
    generateVideoThumbnail(videoUrl) {
        if (videoUrl.includes('youtube.com') || videoUrl.includes('youtu.be')) {
            const videoId = videoUrl.includes('watch?v=') 
                ? videoUrl.split('v=')[1].split('&')[0]
                : videoUrl.split('/').pop();
            return `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`;
        }
        return '/static/images/video-placeholder.jpg';
    },
    
    // Validate video URL
    isValidVideoUrl(url) {
        const patterns = [
            /^https?:\/\/(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)/,
            /^https?:\/\/(www\.)?vimeo\.com\/\d+/,
            /^https?:\/\/.+\.(mp4|avi|mov|wmv|flv|webm)$/i
        ];
        
        return patterns.some(pattern => pattern.test(url));
    },
    
    // Get media type from URL
    getMediaTypeFromUrl(url) {
        if (/\.(jpg|jpeg|png|gif|webp)$/i.test(url)) {
            return 'image';
        } else if (/\.(mp4|avi|mov|wmv|flv|webm)$/i.test(url) || 
                   url.includes('youtube.com') || 
                   url.includes('youtu.be') || 
                   url.includes('vimeo.com')) {
            return 'video';
        }
        return 'unknown';
    }
};

// Initialize gallery manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize on gallery pages
    if (document.querySelector('.gallery-page, .gallery-management')) {
        window.galleryManager = new GalleryManager();
    }
});

// Export for global use
window.GalleryManager = GalleryManager;
window.GalleryUtils = GalleryUtils;


// Gallery form submit handler - Modal kapatma eklendi
document.addEventListener('submit', function(e) {
    const form = e.target;
    
    // Sadece gallery modal formlarını dinle
    if (form.closest('#addGalleryModal') || form.closest('#editGalleryModal')) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        // Loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Kaydediliyor...';
        
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // ✅ MODAL KAPAT
                const modalElement = form.closest('.modal');
                if (modalElement) {
                    const modalInstance = bootstrap.Modal.getInstance(modalElement);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                }
                
                // Notification
                if (window.notificationSystem) {
                    window.notificationSystem.success(data.message || 'Başarıyla kaydedildi!');
                }
                
                // Sayfa yenile
                setTimeout(() => location.reload(), 1000);
            } else {
                // Hata
                if (window.notificationSystem) {
                    window.notificationSystem.error(data.message || 'Bir hata oluştu!');
                }
                
                // Restore button
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        })
        .catch(error => {
            console.error('Submit error:', error);
            alert('Bir hata oluştu: ' + error.message);
            
            // Restore button
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        });
    }
});
