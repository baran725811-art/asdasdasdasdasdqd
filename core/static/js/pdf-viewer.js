/**
 * PDF.js Entegreli PDF Viewer
 * Sayfa sayfa navigation ile PDF görüntüleme
 */

class PDFViewer {
    constructor(pdfUrl, containerId) {
        this.pdfUrl = pdfUrl;
        this.container = document.getElementById(containerId);
        this.currentPage = 1;
        this.totalPages = 0;
        this.scale = 1.0;
        this.pdfDoc = null;
        
        this.init();
    }

    async init() {
        try {
            // PDF.js worker'ını ayarla
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
            
            // Loading göster
            this.showLoading();
            
            // PDF'i yükle
            this.pdfDoc = await pdfjsLib.getDocument(this.pdfUrl).promise;
            this.totalPages = this.pdfDoc.numPages;
            
            // UI'ı oluştur
            this.createViewer();
            
            // İlk sayfayı göster
            await this.renderPage(this.currentPage);
            
            // Loading'i gizle
            this.hideLoading();
            
        } catch (error) {
            console.error('PDF yükleme hatası:', error);
            this.showError();
        }
    }

    createViewer() {
        this.container.innerHTML = `
            <!-- PDF Viewer Container -->
            <div class="pdf-viewer-wrapper">
                <!-- Toolbar -->
                <div class="pdf-toolbar">
                    <div class="pdf-toolbar-left">
                        <button id="prevPage" class="pdf-btn pdf-btn-icon" title="Önceki Sayfa">
                            <i class="fas fa-chevron-left"></i>
                        </button>
                        <button id="nextPage" class="pdf-btn pdf-btn-icon" title="Sonraki Sayfa">
                            <i class="fas fa-chevron-right"></i>
                        </button>
                        <span class="pdf-page-info">
                            <input type="number" id="pageInput" class="pdf-page-input" min="1" max="${this.totalPages}" value="${this.currentPage}">
                            <span>/ ${this.totalPages}</span>
                        </span>
                    </div>
                    
                    <div class="pdf-toolbar-center">
                        <button id="zoomOut" class="pdf-btn pdf-btn-icon" title="Uzaklaştır">
                            <i class="fas fa-search-minus"></i>
                        </button>
                        <span class="pdf-zoom-info" id="zoomInfo">${Math.round(this.scale * 100)}%</span>
                        <button id="zoomIn" class="pdf-btn pdf-btn-icon" title="Yakınlaştır">
                            <i class="fas fa-search-plus"></i>
                        </button>
                        <button id="zoomFit" class="pdf-btn pdf-btn-text" title="Sayfaya Sığdır">
                            <i class="fas fa-expand-arrows-alt"></i>
                        </button>
                    </div>
                    
                    <div class="pdf-toolbar-right">
                        <button id="fullscreen" class="pdf-btn pdf-btn-icon" title="Tam Ekran">
                            <i class="fas fa-expand"></i>
                        </button>
                        <button id="downloadPdf" class="pdf-btn pdf-btn-text" title="İndir">
                            <i class="fas fa-download"></i> İndir
                        </button>
                    </div>
                </div>

                <!-- PDF Canvas Container -->
                <div class="pdf-canvas-container" id="pdfCanvasContainer">
                    <div class="pdf-loading" id="pageLoading">
                        <div class="loading-spinner">
                            <i class="fas fa-spinner fa-spin"></i>
                        </div>
                        <p>Sayfa yükleniyor...</p>
                    </div>
                    <canvas id="pdfCanvas" class="pdf-canvas"></canvas>
                </div>

                <!-- Thumbnail Navigator (isteğe bağlı) -->
                <div class="pdf-thumbnails" id="pdfThumbnails" style="display: none;">
                    <!-- Thumbnail'lar buraya gelecek -->
                </div>
            </div>
        `;

        this.bindEvents();
    }

    bindEvents() {
        // Navigation butonları
        document.getElementById('prevPage').addEventListener('click', () => this.prevPage());
        document.getElementById('nextPage').addEventListener('click', () => this.nextPage());
        
        // Sayfa input
        document.getElementById('pageInput').addEventListener('change', (e) => {
            const page = parseInt(e.target.value);
            if (page >= 1 && page <= this.totalPages) {
                this.goToPage(page);
            }
        });

        // Zoom butonları
        document.getElementById('zoomIn').addEventListener('click', () => this.zoomIn());
        document.getElementById('zoomOut').addEventListener('click', () => this.zoomOut());
        document.getElementById('zoomFit').addEventListener('click', () => this.fitToWidth());

        // Tam ekran
        document.getElementById('fullscreen').addEventListener('click', () => this.toggleFullscreen());

        // İndirme
        document.getElementById('downloadPdf').addEventListener('click', () => this.downloadPdf());

        // Klavye kısayolları
        document.addEventListener('keydown', (e) => this.handleKeydown(e));

        // Mouse wheel zoom (Ctrl + wheel)
        document.getElementById('pdfCanvasContainer').addEventListener('wheel', (e) => {
            if (e.ctrlKey) {
                e.preventDefault();
                if (e.deltaY < 0) {
                    this.zoomIn();
                } else {
                    this.zoomOut();
                }
            }
        });
    }

    async renderPage(pageNum) {
        try {
            // Sayfa loading göster
            this.showPageLoading();

            const page = await this.pdfDoc.getPage(pageNum);
            const canvas = document.getElementById('pdfCanvas');
            const ctx = canvas.getContext('2d');

            // Viewport hesapla
            const viewport = page.getViewport({ scale: this.scale });
            
            // Canvas boyutlarını ayarla
            canvas.height = viewport.height;
            canvas.width = viewport.width;

            // Render işlemi
            const renderContext = {
                canvasContext: ctx,
                viewport: viewport
            };

            await page.render(renderContext).promise;

            // UI güncelle
            this.updateUI();
            this.hidePageLoading();

        } catch (error) {
            console.error('Sayfa render hatası:', error);
            this.showError();
        }
    }

    updateUI() {
        // Sayfa numarasını güncelle
        document.getElementById('pageInput').value = this.currentPage;
        
        // Zoom bilgisini güncelle
        document.getElementById('zoomInfo').textContent = `${Math.round(this.scale * 100)}%`;
        
        // Buton durumlarını güncelle
        document.getElementById('prevPage').disabled = this.currentPage <= 1;
        document.getElementById('nextPage').disabled = this.currentPage >= this.totalPages;
    }

    async prevPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            await this.renderPage(this.currentPage);
        }
    }

    async nextPage() {
        if (this.currentPage < this.totalPages) {
            this.currentPage++;
            await this.renderPage(this.currentPage);
        }
    }

    async goToPage(pageNum) {
        if (pageNum >= 1 && pageNum <= this.totalPages && pageNum !== this.currentPage) {
            this.currentPage = pageNum;
            await this.renderPage(this.currentPage);
        }
    }

    async zoomIn() {
        this.scale = Math.min(this.scale * 1.2, 3.0);
        await this.renderPage(this.currentPage);
    }

    async zoomOut() {
        this.scale = Math.max(this.scale / 1.2, 0.3);
        await this.renderPage(this.currentPage);
    }

    async fitToWidth() {
        const container = document.getElementById('pdfCanvasContainer');
        const containerWidth = container.clientWidth - 40; // Padding için margin
        
        if (this.pdfDoc) {
            const page = await this.pdfDoc.getPage(this.currentPage);
            const viewport = page.getViewport({ scale: 1.0 });
            this.scale = containerWidth / viewport.width;
            await this.renderPage(this.currentPage);
        }
    }

    toggleFullscreen() {
        const element = this.container;
        
        if (!document.fullscreenElement) {
            element.requestFullscreen().then(() => {
                element.classList.add('pdf-fullscreen');
                document.getElementById('fullscreen').innerHTML = '<i class="fas fa-compress"></i>';
            });
        } else {
            document.exitFullscreen().then(() => {
                element.classList.remove('pdf-fullscreen');
                document.getElementById('fullscreen').innerHTML = '<i class="fas fa-expand"></i>';
            });
        }
    }

    downloadPdf() {
        const link = document.createElement('a');
        link.href = this.pdfUrl;
        link.download = 'katalog.pdf';
        link.click();
    }

    handleKeydown(e) {
        switch(e.key) {
            case 'ArrowLeft':
                if (!e.target.matches('input')) {
                    e.preventDefault();
                    this.prevPage();
                }
                break;
            case 'ArrowRight':
                if (!e.target.matches('input')) {
                    e.preventDefault();
                    this.nextPage();
                }
                break;
            case 'Home':
                e.preventDefault();
                this.goToPage(1);
                break;
            case 'End':
                e.preventDefault();
                this.goToPage(this.totalPages);
                break;
            case '+':
            case '=':
                if (e.ctrlKey) {
                    e.preventDefault();
                    this.zoomIn();
                }
                break;
            case '-':
                if (e.ctrlKey) {
                    e.preventDefault();
                    this.zoomOut();
                }
                break;
            case '0':
                if (e.ctrlKey) {
                    e.preventDefault();
                    this.fitToWidth();
                }
                break;
        }
    }

    showLoading() {
        const loading = document.getElementById('loadingOverlay');
        if (loading) {
            loading.style.display = 'flex';
        }
    }

    hideLoading() {
        const loading = document.getElementById('loadingOverlay');
        if (loading) {
            loading.style.display = 'none';
        }
    }

    showPageLoading() {
        const pageLoading = document.getElementById('pageLoading');
        if (pageLoading) {
            pageLoading.style.display = 'flex';
        }
    }

    hidePageLoading() {
        const pageLoading = document.getElementById('pageLoading');
        if (pageLoading) {
            pageLoading.style.display = 'none';
        }
    }

    showError() {
        this.container.innerHTML = `
            <div class="pdf-error">
                <div class="error-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h4>PDF Yüklenemedi</h4>
                <p>PDF dosyası görüntülenemiyor. Lütfen sayfayı yenileyin veya farklı bir tarayıcı deneyin.</p>
                <div class="error-actions">
                    <button onclick="location.reload()" class="pdf-btn pdf-btn-primary">
                        <i class="fas fa-refresh"></i> Sayfayı Yenile
                    </button>
                    <a href="${this.pdfUrl}" download class="pdf-btn pdf-btn-outline">
                        <i class="fas fa-download"></i> PDF'i İndir
                    </a>
                </div>
            </div>
        `;
    }
}

// Global fonksiyon - Template'ten çağrılacak
window.initPDFViewer = function(pdfUrl, containerId) {
    return new PDFViewer(pdfUrl, containerId);
};