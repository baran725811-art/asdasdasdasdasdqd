// Storage bilgilerini periyodik olarak güncelle
class StorageMonitor {
    constructor() {
        this.updateInterval = 5 * 60 * 1000; // 5 dakika
        this.init();
    }

    init() {
        this.updateStorageInfo();
        setInterval(() => this.updateStorageInfo(), this.updateInterval);
    }

    async updateStorageInfo() {
        try {
            const response = await fetch('/dashboard/api/storage-info/');
            const data = await response.json();
            this.updateProgressBar(data);
        } catch (error) {
            console.error('Storage info update failed:', error);
        }
    }

    updateProgressBar(data) {
        const progressBar = document.querySelector('.storage-progress .progress-bar');
        const usageText = document.querySelector('.storage-info-text');
        const percentageText = document.querySelector('.storage-percentage');

        if (progressBar) {
            progressBar.style.width = `${data.usage_percentage}%`;
            progressBar.className = `progress-bar bg-${data.warning_level}`;
        }

        if (usageText && percentageText) {
            usageText.innerHTML = `
                <small class="text-muted">${data.used_gb} GB / ${data.limit_gb} GB</small>
                <small class="${data.is_critical ? 'text-danger' : data.is_warning ? 'text-warning' : 'text-success'}">
                    (${data.remaining_gb} GB kaldı)
                </small>
            `;
            percentageText.innerHTML = `
                <small class="${data.is_critical ? 'text-danger' : data.is_warning ? 'text-warning' : 'text-muted'}">
                    ${data.usage_percentage}%
                </small>
            `;
        }
    }
}

// Sayfa yüklendiğinde başlat
document.addEventListener('DOMContentLoaded', () => {
    new StorageMonitor();
});