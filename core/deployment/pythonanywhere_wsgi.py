"""
PythonAnywhere WSGI Configuration
==================================

Bu dosyayı PythonAnywhere'deki WSGI configuration file'ına kopyalayın.

Adımlar:
1. PythonAnywhere Dashboard > Web sekmesi
2. "WSGI configuration file" linkine tıklayın
3. Bu dosyanın içeriğini oraya kopyalayın
4. KULLANICI_ADI yerine kendi kullanıcı adınızı yazın
5. Kaydedin ve Reload butonuna tıklayın
"""

import os
import sys

# ============================================================================
# PATH CONFIGURATION
# ============================================================================

# Proje yolunu sys.path'e ekle
# KULLANICI_ADI yerine kendi PythonAnywhere kullanıcı adınızı yazın!
path = '/home/KULLANICI_ADI/asdasdasdasdasdqd/core'
if path not in sys.path:
    sys.path.insert(0, path)

# ============================================================================
# ENVIRONMENT VARIABLES
# ============================================================================

# Django environment ayarı - PRODUCTION modda çalışacak
os.environ['DJANGO_ENV'] = 'production'
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

# ============================================================================
# DJANGO APPLICATION
# ============================================================================

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# ============================================================================
# LOGGING (Optional - Debugging için)
# ============================================================================

# Eğer sorun yaşarsanız, aşağıdaki satırları uncomment edin:
# import logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
# logger.info('WSGI application loaded successfully')
