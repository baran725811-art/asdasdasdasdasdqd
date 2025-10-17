// static/dashboard/js/components/translation-tab-fix.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔧 Translation Tab Fix Loading...');
    
    // 1 saniye bekle, sonra tab'ları bul
    setTimeout(function() {
        const tabs = document.querySelectorAll('.translation-tab');
        console.log('🔍 Found translation tabs:', tabs.length);
        
        if (tabs.length > 0) {
            tabs.forEach(function(tab, index) {
                console.log('🏷️ Setting up tab', index, ':', tab.textContent.trim());
                
                // Tıklama eventi ekle
                tab.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log('🌍 Tab clicked:', this.textContent.trim());
                    
                    // Tüm tab'ları deaktif et
                    tabs.forEach(t => {
                        t.classList.remove('active');
                    });
                    
                    // Bu tab'ı aktif et
                    this.classList.add('active');
                    
                    // Dil kodunu al (data-lang varsa)
                    const langCode = this.dataset.lang;
                    if (langCode) {
                        console.log('🔄 Language switched to:', langCode);
                        
                        // Translation content'leri bul ve göster/gizle
                        const contents = document.querySelectorAll('.translation-content');
                        contents.forEach(content => {
                            if (content.dataset.lang === langCode) {
                                content.classList.add('active');
                                content.style.display = 'block';
                            } else {
                                content.classList.remove('active');
                                content.style.display = 'none';
                            }
                        });
                    }
                });
                
                // İmleci pointer yap
                tab.style.cursor = 'pointer';
            });
            
            console.log('✅ Translation tabs initialized successfully');
        } else {
            console.log('❌ No translation tabs found');
        }
    }, 1000);
});