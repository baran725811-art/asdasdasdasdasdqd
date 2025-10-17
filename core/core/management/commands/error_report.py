# core/management/commands/error_report.py - YENİ DOSYA OLUŞTUR

from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from collections import Counter
import json

class Command(BaseCommand):
    help = '404 hata raporunu görüntüler ve analiz eder'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='404 hata cache\'ini temizle',
        )
        parser.add_argument(
            '--export',
            type=str,
            help='Raporu JSON dosyasına aktar',
        )
        parser.add_argument(
            '--top',
            type=int,
            default=10,
            help='En çok görülen hataların sayısı (varsayılan: 10)',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self._clear_error_cache()
            return

        self.stdout.write(self.style.SUCCESS('📊 404 Hata Raporu Analizi'))
        self.stdout.write('=' * 50)
        
        # Cache'den 404 hatalarını al
        errors = cache.get('404_errors_list', [])
        
        if not errors:
            self.stdout.write(self.style.WARNING('Hiç 404 hatası kaydı bulunamadı.'))
            return
        
        # Analiz yap
        analysis = self._analyze_errors(errors)
        
        # Raporu göster
        self._display_report(analysis, options['top'])
        
        # Export işlemi
        if options['export']:
            self._export_report(analysis, options['export'])

    def _analyze_errors(self, errors):
        """404 hatalarını analiz et"""
        analysis = {
            'total_errors': len(errors),
            'unique_paths': len(set(error['path'] for error in errors)),
            'unique_ips': len(set(error['ip'] for error in errors)),
            'path_counts': Counter(error['path'] for error in errors),
            'ip_counts': Counter(error['ip'] for error in errors),
            'referrer_counts': Counter(error.get('referrer', 'Direct') for error in errors if error.get('referrer')),
            'hourly_distribution': {},
            'critical_errors': [],
            'recent_errors': sorted(errors, key=lambda x: x['timestamp'], reverse=True)[:20]
        }
        
        # Saatlik dağılım
        for error in errors:
            try:
                hour = timezone.datetime.fromisoformat(error['timestamp']).hour
                analysis['hourly_distribution'][hour] = analysis['hourly_distribution'].get(hour, 0) + 1
            except:
                pass
        
        # Kritik hatalar
        for path, count in analysis['path_counts'].items():
            if self._is_critical_path(path) or count > 5:
                analysis['critical_errors'].append({
                    'path': path,
                    'count': count,
                    'is_critical': self._is_critical_path(path)
                })
        
        return analysis

    def _is_critical_path(self, path):
        """Kritik path olup olmadığını kontrol et"""
        critical_patterns = [
            '/sitemap.xml',
            '/robots.txt',
            '/favicon.ico',
            '.xml',
            '.json',
        ]
        
        for pattern in critical_patterns:
            if pattern in path:
                return True
        
        return path.count('/') > 3

    def _display_report(self, analysis, top_count):
        """Raporu konsola yazdır"""
        self.stdout.write(f"\n📈 Genel İstatistikler:")
        self.stdout.write(f"  • Toplam 404 hatası: {analysis['total_errors']}")
        self.stdout.write(f"  • Benzersiz path sayısı: {analysis['unique_paths']}")
        self.stdout.write(f"  • Benzersiz IP sayısı: {analysis['unique_ips']}")
        
        # En çok 404 alan path'ler
        self.stdout.write(f"\n🔥 En Çok 404 Alan Sayfalar (Top {top_count}):")
        for path, count in analysis['path_counts'].most_common(top_count):
            status = "🔴 KRİTİK" if self._is_critical_path(path) else "ℹ️  Normal"
            self.stdout.write(f"  {status} {path}: {count} kez")
        
        # En aktif IP'ler
        self.stdout.write(f"\n🌐 En Aktif IP Adresleri (Top {min(top_count, 5)}):")
        for ip, count in analysis['ip_counts'].most_common(min(top_count, 5)):
            self.stdout.write(f"  • {ip}: {count} hata")
        
        # Referrer analizi
        if analysis['referrer_counts']:
            self.stdout.write(f"\n🔗 Referrer Analizi (Top 5):")
            for referrer, count in analysis['referrer_counts'].most_common(5):
                referrer_display = referrer if referrer != 'Direct' else 'Doğrudan Erişim'
                self.stdout.write(f"  • {referrer_display}: {count} kez")
        
        # Kritik hatalar
        if analysis['critical_errors']:
            self.stdout.write(f"\n⚠️  Kritik Hatalar:")
            for error in sorted(analysis['critical_errors'], key=lambda x: x['count'], reverse=True):
                self.stdout.write(f"  🔴 {error['path']}: {error['count']} kez")
        
        # Saatlik dağılım
        if analysis['hourly_distribution']:
            self.stdout.write(f"\n⏰ Saatlik Dağılım:")
            for hour in sorted(analysis['hourly_distribution'].keys()):
                count = analysis['hourly_distribution'][hour]
                bar = '█' * min(count // 2, 20)  # Basit bar chart
                self.stdout.write(f"  {hour:02d}:00 {bar} ({count})")
        
        # Son hatalar
        self.stdout.write(f"\n🕒 Son 5 Hata:")
        for error in analysis['recent_errors'][:5]:
            timestamp = error['timestamp'][:19].replace('T', ' ')
            self.stdout.write(f"  • {timestamp} | {error['path']} | {error['ip']}")

    def _export_report(self, analysis, filename):
        """Raporu JSON dosyasına aktar"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
            self.stdout.write(self.style.SUCCESS(f"✅ Rapor {filename} dosyasına aktarıldı."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Export hatası: {e}"))

    def _clear_error_cache(self):
        """404 hata cache'ini temizle"""
        cache.delete('404_errors_list')
        self.stdout.write(self.style.SUCCESS("✅ 404 hata cache'i temizlendi."))