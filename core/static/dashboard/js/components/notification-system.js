// NOTIFICATION SYSTEM - ACTIVE VERSION
console.log('🔔 Notification system başlatılıyor...');

class NotificationSystem {
    constructor() {
        this.isInitialized = false;
        console.log('NotificationSystem constructor çağrıldı');
    }
    
    init() {
        if (this.isInitialized) {
            console.log('NotificationSystem zaten başlatılmış');
            return;
        }
        
        console.log('NotificationSystem init() çağrıldı');
        
        // NotificationDropdownSystem varsa kullan
        if (window.NotificationDropdownSystem) {
            console.log('NotificationDropdownSystem bulundu, başlatılıyor...');
            window.NotificationDropdownSystem.init();
        } else {
            console.log('NotificationDropdownSystem bulunamadı');
        }
        
        this.isInitialized = true;
    }
    
    destroy() {
        console.log('NotificationSystem destroy() çağrıldı');
        this.isInitialized = false;
    }
}

// Global instance oluştur
window.notificationSystem = new NotificationSystem();

// DOM ready olduğunda başlat
document.addEventListener('DOMContentLoaded', function() {
    console.log('NotificationSystem DOM ready - başlatılıyor');
    
    // Biraz bekle ki diğer sistemler yüklensin
    setTimeout(() => {
        window.notificationSystem.init();
    }, 100);
});