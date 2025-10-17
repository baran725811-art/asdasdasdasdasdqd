from django.core.management.base import BaseCommand
from core.models import LegalPage

class Command(BaseCommand):
    help = 'Varsayılan yasal sayfaları oluşturur'
    
    def handle(self, *args, **options):
        legal_pages = [
            {
                'page_type': 'privacy',
                'title': 'Gizlilik Politikası',
                'content': '''
                <h2>Kişisel Verilerin Korunması</h2>
                <p>Bu gizlilik politikası, web sitemizi ziyaret ettiğinizde kişisel verilerinizin nasıl toplandığını, kullanıldığını ve korunduğunu açıklar.</p>
                
                <h3>Toplanan Bilgiler</h3>
                <p>Web sitemizi ziyaret ettiğinizde aşağıdaki bilgiler otomatik olarak toplanabilir:</p>
                <ul>
                    <li>IP adresiniz</li>
                    <li>Tarayıcı türü ve sürümü</li>
                    <li>Ziyaret edilen sayfalar</li>
                    <li>Ziyaret tarihi ve süresi</li>
                </ul>
                
                <h3>Çerezler</h3>
                <p>Web sitemiz deneyiminizi geliştirmek için çerezler kullanır. Çerez tercihlerinizi <a href="#cookie-settings">buradan</a> yönetebilirsiniz.</p>
                '''
            },
            {
                'page_type': 'terms',
                'title': 'Kullanım Şartları',
                'content': '''
                <h2>Web Sitesi Kullanım Şartları</h2>
                <p>Bu web sitesini kullanarak aşağıdaki şartları kabul etmiş sayılırsınız.</p>
                
                <h3>Genel Kullanım</h3>
                <p>Web sitemiz yalnızca yasal amaçlarla kullanılabilir. Site içeriğini izinsiz kopyalamanız, dağıtmanız veya ticari amaçlarla kullanmanız yasaktır.</p>
                '''
            },
            {
                'page_type': 'cookies',
                'title': 'Çerez Politikası',
                'content': '''
                <h2>Çerez Kullanımı Hakkında</h2>
                <p>Bu sayfa web sitemizde kullanılan çerezler hakkında detaylı bilgi sağlar.</p>
                
                <h3>Çerez Nedir?</h3>
                <p>Çerezler, web sitelerinin kullanıcı deneyimini geliştirmek amacıyla tarayıcınızda sakladığı küçük metin dosyalarıdır.</p>
                
                <h3>Çerez Türlerimiz</h3>
                <ul>
                    <li><strong>Zorunlu Çerezler:</strong> Site işlevselliği için gerekli</li>
                    <li><strong>Fonksiyonel Çerezler:</strong> Tercihlerinizi hatırlar</li>
                    <li><strong>Analitik Çerezler:</strong> Site performansını ölçer</li>
                    <li><strong>Pazarlama Çerezleri:</strong> Kişiselleştirilmiş reklam için</li>
                </ul>
                '''
            }
        ]
        
        for page_data in legal_pages:
            page, created = LegalPage.objects.get_or_create(
                page_type=page_data['page_type'],
                defaults=page_data
            )
            if created:
                self.stdout.write(f"✅ {page.title} oluşturuldu")
            else:
                self.stdout.write(f"ℹ️ {page.title} zaten mevcut")