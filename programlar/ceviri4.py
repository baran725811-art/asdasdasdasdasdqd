import sys
import os
import re
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog, 
    QProgressBar, QComboBox, QGroupBox, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget,
    QScrollArea, QFrame, QSpinBox, QSlider, QRadioButton,
    QButtonGroup, QSplitter, QPlainTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt6.QtGui import QFont, QColor, QPalette, QTextCharFormat, QSyntaxHighlighter

try:
    import deepl
except ImportError:
    print("HATA: deepl kütüphanesi yüklü değil. 'pip install deepl' komutunu çalıştırın.")
    sys.exit(1)

try:
    import google.generativeai as genai
except ImportError:
    print("HATA: google-generativeai kütüphanesi yüklü değil. 'pip install google-generativeai' komutunu çalıştırın.")
    sys.exit(1)

# =====================================================
# API KEYS
# =====================================================
DEEPL_API_KEY = "64605b99-7c0c-481b-a28a-5dbd1b72377d:fx"
GEMINI_API_KEY = "AIzaSyDb3LY05ahVBctyVPlvFVmmzLzv-XrO_9Q"

# =====================================================
# Sabitler ve Konfigürasyonlar
# =====================================================
LANGUAGES = {
    "TR": {"name": "Türkçe", "flag": "🇹🇷", "code": "TR"},
    "EN-US": {"name": "İngilizce (Amerikan)", "flag": "🇺🇸", "code": "EN-US"},
    "EN-GB": {"name": "İngilizce (İngiliz)", "flag": "🇬🇧", "code": "EN-GB"},
    "AR": {"name": "Arapça", "flag": "🇸🇦", "code": "AR"},
    "DE": {"name": "Almanca", "flag": "🇩🇪", "code": "DE"},
    "ES": {"name": "İspanyolca", "flag": "🇪🇸", "code": "ES"},
    "FR": {"name": "Fransızca", "flag": "🇫🇷", "code": "FR"},
    "RU": {"name": "Rusça", "flag": "🇷🇺", "code": "RU"}
}

class QualityStatus(Enum):
    PERFECT = (90, 100, "Mükemmel", "🟢", "#d4edda")
    GOOD = (80, 89, "İyi", "🟢", "#d1ecf1")
    MODERATE = (70, 79, "Orta", "🟡", "#fff3cd")
    WEAK = (60, 69, "Zayıf", "🟠", "#ffe5cc")
    POOR = (0, 59, "Hatalı", "🔴", "#f8d7da")
    
    def __init__(self, min_score, max_score, label, icon, color):
        self.min_score = min_score
        self.max_score = max_score
        self.label = label
        self.icon = icon
        self.color = color
    
    @staticmethod
    def get_status(score: int):
        for status in QualityStatus:
            if status.min_score <= score <= status.max_score:
                return status
        return QualityStatus.POOR

# =====================================================
# Data Classes
# =====================================================
@dataclass
class TranslationItem:
    line_number: int
    msgid: str
    msgstr: str
    translated: bool = False
    
@dataclass
class GeminiResult:
    overall_score: int
    scores: Dict[str, int]
    issues: List[str]
    suggestion: Optional[str]
    comment: str
    status: QualityStatus

# =====================================================
# Gemini Kalite Kontrol Sınıfı (İYİLEŞTİRİLMİŞ)
# =====================================================
class GeminiQualityChecker:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            'gemini-2.0-flash-exp',
            generation_config={
                "temperature": 0.3,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
        )
    
    def get_language_name(self, lang_code: str) -> str:
        """Dil kodundan tam dil adını al"""
        lang_map = {
            "TR": "Türkçe",
            "EN-US": "İngilizce (Amerikan)",
            "EN-GB": "İngilizce (İngiliz)",
            "AR": "Arapça",
            "DE": "Almanca",
            "ES": "İspanyolca",
            "FR": "Fransızca",
            "RU": "Rusça"
        }
        return lang_map.get(lang_code, "Bilinmeyen")
        
    def check_translation(self, msgid: str, msgstr: str, 
                         source_lang: str = "TR", 
                         target_lang: str = "EN") -> GeminiResult:
        """Tek bir çeviriyi kontrol et - OPTİMİZE EDİLMİŞ"""
        
        target_lang_name = self.get_language_name(target_lang)
        source_lang_name = self.get_language_name(source_lang)
        
        # Boş msgstr durumu - HIZLI ÇEVİRİ ÖNERİSİ
        if not msgstr.strip():
            prompt = f"""Sen profesyonel bir {target_lang_name} çevirmensin.

Kaynak ({source_lang_name}): "{msgid}"
Hedef Dil: {target_lang_name}

GÖREV: Bu metni {target_lang_name} diline profesyonelce çevir.

KURALLAR:
- Doğal ve akıcı {target_lang_name}
- Teknik terimleri koru (API, Database vb)
- Placeholder'ları aynen koru (%s, {{{{x}}}}, %d vb)
- HTML tag'leri koru
- {target_lang_name} dilbilgisi kurallarına uy

SADECE JSON:
{{
    "suggestion": "SADECE {target_lang_name} ÇEVİRİSİ BURAYA",
    "comment": "Kısa açıklama"
}}"""
            
            try:
                response = self.model.generate_content(prompt)
                response_text = self._clean_json(response.text)
                data = json.loads(response_text)
                
                return GeminiResult(
                    overall_score=0,
                    scores={"meaning": 0, "grammar": 0, "naturalness": 0, "technical": 0, "format": 0},
                    issues=["Çeviri yapılmamış"],
                    suggestion=data.get("suggestion", "Çeviri oluşturulamadı"),
                    comment=f"🤖 {target_lang_name} çevirisi önerildi",
                    status=QualityStatus.POOR
                )
                
            except Exception as e:
                print(f"Gemini çeviri hatası: {e}")
                return GeminiResult(
                    overall_score=0,
                    scores={"meaning": 0, "grammar": 0, "naturalness": 0, "technical": 0, "format": 0},
                    issues=["Çeviri boş - API hatası"],
                    suggestion=None,
                    comment="Çeviri oluşturulamadı",
                    status=QualityStatus.POOR
                )
        
        # Dolu msgstr durumu - HIZLI KALİTE KONTROLÜ
        prompt = f"""Sen {target_lang_name} uzmanısın.

Kaynak ({source_lang_name}): "{msgid}"
Çeviri ({target_lang_name}): "{msgstr}"

ÖNEMLİ: SADECE msgstr'i değerlendir ve öner, msgid'e DOKUNMA!

Değerlendirme kriterleri (0-100):
1. Anlam bütünlüğü
2. {target_lang_name} dilbilgisi
3. Doğallık ({target_lang_name} için)
4. Teknik doğruluk (placeholder'lar, terimler)
5. Format (HTML, noktalama)

SADECE JSON:
{{
    "scores": {{
        "meaning": 0-100,
        "grammar": 0-100,
        "naturalness": 0-100,
        "technical": 0-100,
        "format": 0-100
    }},
    "overall_score": 0-100,
    "issues": ["sorun1", "sorun2"],
    "suggestion": "SADECE msgstr için iyileştirilmiş {target_lang_name} çeviri veya null",
    "comment": "Kısa yorum"
}}

NOT: Eğer msgstr mükemmelse suggestion: null döndür."""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = self._clean_json(response.text)
            data = json.loads(response_text)
            
            overall_score = data.get("overall_score", 0)
            status = QualityStatus.get_status(overall_score)
            
            return GeminiResult(
                overall_score=overall_score,
                scores=data.get("scores", {}),
                issues=data.get("issues", []),
                suggestion=data.get("suggestion"),
                comment=data.get("comment", ""),
                status=status
            )
            
        except Exception as e:
            print(f"Gemini API hatası: {e}")
            return GeminiResult(
                overall_score=50,
                scores={"meaning": 50, "grammar": 50, "naturalness": 50, "technical": 50, "format": 50},
                issues=[f"API hatası: {str(e)}"],
                suggestion=None,
                comment="Kontrol yapılamadı",
                status=QualityStatus.MODERATE
            )
    
    def _clean_json(self, text: str) -> str:
        """JSON yanıtını temizle"""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

# =====================================================
# PO Dosya Parser
# =====================================================
class POFileParser:
    @staticmethod
    def parse(content: str) -> List[TranslationItem]:
        """PO dosyasını parse et"""
        items = []
        
        # Çok satırlı msgid/msgstr desteği ile regex
        pattern = r'(?:^|\n)msgid\s+"([^"]*)"(?:\s*\n"([^"]*)")*\s*\nmsgstr\s+"([^"]*)"(?:\s*\n"([^"]*)")*'
        
        for i, match in enumerate(re.finditer(pattern, content, re.MULTILINE), start=1):
            msgid_parts = [match.group(1)]
            msgstr_parts = [match.group(3)]
            
            # Çok satırlı kısımları ekle
            if match.group(2):
                msgid_parts.append(match.group(2))
            if match.group(4):
                msgstr_parts.append(match.group(4))
            
            msgid = ''.join(msgid_parts)
            msgstr = ''.join(msgstr_parts)
            
            if msgid.strip():  # Boş msgid'leri atla
                items.append(TranslationItem(
                    line_number=i,
                    msgid=msgid,
                    msgstr=msgstr,
                    translated=bool(msgstr.strip())
                ))
        
        return items
    
    @staticmethod
    def escape_po_string(text: str) -> str:
        """PO formatı için escape"""
        if not text:
            return '""'
        text = text.replace('\\', '\\\\')
        text = text.replace('"', '\\"')
        text = text.replace('\n', '\\n')
        text = text.replace('\t', '\\t')
        text = text.replace('\r', '\\r')
        return f'"{text}"'
    
    @staticmethod
    def update_po_file(content: str, items: List[TranslationItem]) -> str:
        """PO dosyasını güncelle"""
        new_content = content
        
        for item in items:
            if not item.translated:
                continue
            
            # Eski msgstr'i bul ve değiştir
            old_pattern = rf'(msgid\s+{re.escape(POFileParser.escape_po_string(item.msgid))}\s*\n)msgstr\s+"[^"]*"'
            new_msgstr = f'msgstr {POFileParser.escape_po_string(item.msgstr)}'
            replacement = r'\1' + new_msgstr
            
            new_content = re.sub(old_pattern, replacement, new_content, count=1)
        
        return new_content

# =====================================================
# Çeviri Worker Thread
# =====================================================
class TranslationWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, input_path: str, output_dir: str, 
                 target_langs: List[str], force_retranslate: bool):
        super().__init__()
        self.input_path = input_path
        self.output_dir = output_dir
        self.target_langs = target_langs
        self.force_retranslate = force_retranslate
        self.translator = deepl.Translator(DEEPL_API_KEY)
        self._is_running = True
        
    def stop(self):
        self._is_running = False
        
    def is_turkish_text(self, text: str) -> bool:
        """Türkçe metin kontrolü"""
        if not text.strip():
            return False
        turkish_chars = set('çğıöşüÇĞIİÖŞÜ')
        turkish_words = {'için', 'olan', 'bir', 'bu', 'şu', 've', 'ile', 'gibi', 'var', 'yok'}
        
        has_turkish_chars = any(char in turkish_chars for char in text)
        words = re.findall(r'\b\w+\b', text.lower())
        
        if not words:
            return False
            
        turkish_word_count = sum(1 for w in words if w in turkish_words)
        
        return has_turkish_chars or (turkish_word_count / len(words) > 0.2)
    
    def translate_text(self, text: str, target_lang: str) -> str:
        """Metni çevir"""
        if not text.strip():
            return ""
        
        # Türkçe'ye çeviriyorsak ve zaten Türkçe ise
        if target_lang == "TR" and self.is_turkish_text(text):
            return text
            
        try:
            time.sleep(1.2)  # API rate limit
            result = self.translator.translate_text(text, target_lang=target_lang)
            return result.text
        except deepl.TooManyRequestsException:
            time.sleep(10)
            return self.translate_text(text, target_lang)
        except Exception as e:
            print(f"Çeviri hatası: {e}")
            return text
    
    def run(self):
        try:
            # Dosyayı oku
            with open(self.input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse et
            items = POFileParser.parse(content)
            
            if not items:
                self.error.emit("PO dosyasında çevrilebilir içerik bulunamadı!")
                return
            
            results = {}
            
            for lang_code in self.target_langs:
                if not self._is_running:
                    break
                    
                lang_name = LANGUAGES[lang_code]["name"]
                self.progress.emit(0, f"🌍 {lang_name} çevirisi başlıyor...")
                
                translated_items = []
                translated = 0
                skipped = 0
                errors = 0
                
                for i, item in enumerate(items):
                    if not self._is_running:
                        break
                        
                    progress_pct = int((i + 1) / len(items) * 100)
                    
                    # Zaten çevrilmiş mi?
                    if item.msgstr and not self.force_retranslate:
                        skipped += 1
                        continue
                    
                    self.progress.emit(
                        progress_pct, 
                        f"🔄 {lang_name}: '{item.msgid[:50]}...' çeviriliyor"
                    )
                    
                    # Çeviri yap
                    translated_text = self.translate_text(item.msgid, lang_code)
                    
                    if translated_text and translated_text != item.msgid:
                        item.msgstr = translated_text
                        item.translated = True
                        translated_items.append(item)
                        translated += 1
                    else:
                        errors += 1
                
                # Dosyayı güncelle ve kaydet
                new_content = POFileParser.update_po_file(content, translated_items)
                
                output_path = os.path.join(
                    self.output_dir, 
                    f"django_{lang_code.lower().replace('-', '_')}.po"
                )
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                results[lang_code] = {
                    'name': lang_name,
                    'translated': translated,
                    'skipped': skipped,
                    'errors': errors,
                    'output': output_path,
                    'total': len(items)
                }
                
                self.progress.emit(100, f"✅ {lang_name} tamamlandı!")
            
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(f"Hata: {str(e)}")

# =====================================================
# Gemini Kontrol Worker Thread (OPTİMİZE EDİLMİŞ)
# =====================================================
class GeminiWorker(QThread):
    progress = pyqtSignal(int, str)
    item_checked = pyqtSignal(int, dict)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, items: List[TranslationItem], 
                 check_meaning: bool, check_technical: bool,
                 check_format: bool, check_grammar: bool,
                 check_alternatives: bool, min_score: int,
                 check_mode: str, target_lang: str, source_lang: str = "TR"):
        super().__init__()
        self.items = items
        self.check_meaning = check_meaning
        self.check_technical = check_technical
        self.check_format = check_format
        self.check_grammar = check_grammar
        self.check_alternatives = check_alternatives
        self.min_score = min_score
        self.check_mode = check_mode
        self.target_lang = target_lang
        self.source_lang = source_lang
        self._is_running = True
        self.checker = GeminiQualityChecker(GEMINI_API_KEY)
        
    def stop(self):
        self._is_running = False
        
    def should_check(self, item: TranslationItem) -> bool:
        """Bu item kontrol edilmeli mi?"""
        if self.check_mode == "all":
            return True
        elif self.check_mode == "empty":
            return not item.msgstr.strip()
        elif self.check_mode == "long":
            return len(item.msgid) > 50
        return True
    
    def run(self):
        try:
            items_to_check = [item for item in self.items if self.should_check(item)]
            
            if not items_to_check:
                self.error.emit("Kontrol edilecek öğe bulunamadı!")
                return
            
            results = {
                'perfect': 0,
                'good': 0,
                'moderate': 0,
                'weak': 0,
                'poor': 0,
                'total': len(items_to_check),
                'average_score': 0,
                'items': []
            }
            
            total_score = 0
            
            for i, item in enumerate(items_to_check):
                if not self._is_running:
                    break
                
                progress_pct = int((i + 1) / len(items_to_check) * 100)
                self.progress.emit(
                    progress_pct,
                    f"🤖 [{i+1}/{len(items_to_check)}] Kontrol ediliyor..."
                )
                
                # Gemini kontrolü
                result = self.checker.check_translation(
                    item.msgid, 
                    item.msgstr,
                    source_lang=self.source_lang,
                    target_lang=self.target_lang
                )
                
                # Sonucu kategorize et
                if result.status == QualityStatus.PERFECT:
                    results['perfect'] += 1
                elif result.status == QualityStatus.GOOD:
                    results['good'] += 1
                elif result.status == QualityStatus.MODERATE:
                    results['moderate'] += 1
                elif result.status == QualityStatus.WEAK:
                    results['weak'] += 1
                else:
                    results['poor'] += 1
                
                total_score += result.overall_score
                
                # Item sonucunu emit et
                item_result = {
                    'item': item,
                    'result': result
                }
                results['items'].append(item_result)
                self.item_checked.emit(i, item_result)
                
                # Rate limiting - daha kısa bekleme
                time.sleep(0.3)
            
            results['average_score'] = total_score / len(items_to_check) if items_to_check else 0
            
            self.progress.emit(100, "✅ Kontrol tamamlandı!")
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(f"Gemini kontrolü hatası: {str(e)}")

# =====================================================
# Test Worker Thread
# =====================================================
class TestWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
        
    def run(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            items = POFileParser.parse(content)
            
            empty_items = [item for item in items if not item.msgstr.strip()]
            filled_items = [item for item in items if item.msgstr.strip()]
            
            results = {
                'total': len(items),
                'empty': len(empty_items),
                'filled': len(filled_items),
                'empty_items': empty_items,
                'completion_rate': (len(filled_items) / len(items) * 100) if items else 0
            }
            
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(f"Test hatası: {str(e)}")

# =====================================================
# Ana Pencere (İYİLEŞTİRİLMİŞ UI)
# =====================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌍 PO Dosyası Çeviri Aracı Pro")
        self.setGeometry(100, 100, 1400, 900)
        
        # Settings
        self.settings = QSettings("POTranslator", "Pro")
        
        # Workers
        self.translation_worker = None
        self.gemini_worker = None
        self.test_worker = None
        
        # Gemini results cache
        self.gemini_results = []
        self.current_items = []
        
        # Ana widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Başlık
        title = QLabel("🌍 PO DOSYASI ÇEVİRİ ARACI - PROFESSIONAL")
        title.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            padding: 10px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #667eea, stop:1 #764ba2);
            color: white;
            border-radius: 5px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                padding: 10px 20px;
                margin: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #667eea;
                color: white;
            }
        """)
        
        # Sekmeleri oluştur
        self.create_translation_tab()
        self.create_test_tab()
        self.create_gemini_tab()
        self.create_results_tab()
        
        layout.addWidget(self.tabs)
        
        # Status bar
        self.statusBar().showMessage("Hazır")
        
    def create_translation_tab(self):
        """Çeviri sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Dosya seçimi
        file_group = QGroupBox("📁 Dosya Seçimi")
        file_layout = QVBoxLayout()
        
        # Input
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Kaynak PO:"))
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("Çevrilecek .po dosyasını seçin...")
        input_layout.addWidget(self.input_path, 1)
        btn_browse = QPushButton("📂 Seç")
        btn_browse.clicked.connect(self.browse_input)
        input_layout.addWidget(btn_browse)
        file_layout.addLayout(input_layout)
        
        # Output
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Çıkış Dizini:"))
        self.output_dir = QLineEdit()
        self.output_dir.setPlaceholderText("Çevrilmiş dosyaların kaydedileceği dizin...")
        output_layout.addWidget(self.output_dir, 1)
        btn_output = QPushButton("📁 Seç")
        btn_output.clicked.connect(self.browse_output)
        output_layout.addWidget(btn_output)
        file_layout.addLayout(output_layout)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Dil seçimi
        lang_group = QGroupBox("🌐 Hedef Diller")
        lang_layout = QVBoxLayout()
        
        self.lang_checkboxes = {}
        grid_layout = QHBoxLayout()
        
        for lang_code, lang_info in LANGUAGES.items():
            cb = QCheckBox(f"{lang_info['flag']} {lang_info['name']}")
            self.lang_checkboxes[lang_code] = cb
            grid_layout.addWidget(cb)
        
        btn_layout = QHBoxLayout()
        btn_select_all = QPushButton("✅ Tümünü Seç")
        btn_select_all.clicked.connect(self.select_all_langs)
        btn_layout.addWidget(btn_select_all)
        
        btn_clear_all = QPushButton("❌ Tümünü Kaldır")
        btn_clear_all.clicked.connect(self.clear_all_langs)
        btn_layout.addWidget(btn_clear_all)
        btn_layout.addStretch()
        
        lang_layout.addLayout(grid_layout)
        lang_layout.addLayout(btn_layout)
        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)
        
        # Seçenekler
        options_group = QGroupBox("⚙️ Çeviri Seçenekleri")
        options_layout = QVBoxLayout()
        
        self.force_retranslate = QCheckBox("🔄 Zaten çevrilmiş alanları da yeniden çevir")
        options_layout.addWidget(self.force_retranslate)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # İlerleme
        progress_group = QGroupBox("📊 İlerleme")
        progress_layout = QVBoxLayout()
        
        self.translation_progress = QProgressBar()
        progress_layout.addWidget(self.translation_progress)
        
        self.translation_status = QLabel("Hazır")
        progress_layout.addWidget(self.translation_status)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Butonlar
        btn_layout = QHBoxLayout()
        
        self.btn_start_translation = QPushButton("🚀 ÇEVİRİYİ BAŞLAT")
        self.btn_start_translation.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.btn_start_translation.clicked.connect(self.start_translation)
        btn_layout.addWidget(self.btn_start_translation)
        
        self.btn_stop_translation = QPushButton("⛔ DURDUR")
        self.btn_stop_translation.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.btn_stop_translation.setEnabled(False)
        self.btn_stop_translation.clicked.connect(self.stop_translation)
        btn_layout.addWidget(self.btn_stop_translation)
        
        layout.addLayout(btn_layout)
        
        self.tabs.addTab(tab, "🌍 Çeviri")
    
    def create_test_tab(self):
        """Test sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Dosya seçimi
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Test Edilecek Dosya:"))
        self.test_file_path = QLineEdit()
        file_layout.addWidget(self.test_file_path, 1)
        btn_test_browse = QPushButton("📂 Seç")
        btn_test_browse.clicked.connect(self.browse_test_file)
        file_layout.addWidget(btn_test_browse)
        layout.addLayout(file_layout)
        
        # Dosya Düzenleme İşlemleri
        organize_group = QGroupBox("📋 Dosya Düzenleme")
        organize_layout = QVBoxLayout()
        
        organize_info = QLabel("Boş msgstr alanlarını dosyanın en altına taşıyarak düzenli bir yapı oluşturun.")
        organize_info.setWordWrap(True)
        organize_info.setStyleSheet("color: #555; font-size: 12px; padding: 5px;")
        organize_layout.addWidget(organize_info)
        
        self.btn_move_empty_to_bottom = QPushButton("⬇️ Boş msgstr Alanlarını En Alta Taşı")
        self.btn_move_empty_to_bottom.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btn_move_empty_to_bottom.clicked.connect(self.move_empty_to_bottom)
        organize_layout.addWidget(self.btn_move_empty_to_bottom)
        
        organize_group.setLayout(organize_layout)
        layout.addWidget(organize_group)
        
        # Türkçe özel işlemler
        turkish_group = QGroupBox("🇹🇷 Türkçe Özel İşlemler")
        turkish_layout = QVBoxLayout()
        
        turkish_info = QLabel("Eğer dosya Türkçe ise, boş msgstr alanlarını msgid ile doldurabilirsiniz.")
        turkish_info.setWordWrap(True)
        turkish_layout.addWidget(turkish_info)
        
        self.btn_fill_turkish = QPushButton("🇹🇷 Boş Alanları Türkçe ile Doldur")
        self.btn_fill_turkish.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.btn_fill_turkish.clicked.connect(self.fill_turkish_empty)
        turkish_layout.addWidget(self.btn_fill_turkish)
        
        turkish_group.setLayout(turkish_layout)
        layout.addWidget(turkish_group)
        
        # Test butonu
        btn_test_layout = QHBoxLayout()
        self.btn_run_test = QPushButton("🔍 TESTİ BAŞLAT")
        self.btn_run_test.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btn_run_test.clicked.connect(self.run_test)
        btn_test_layout.addWidget(self.btn_run_test)
        layout.addLayout(btn_test_layout)
        
        # Sonuçlar
        results_group = QGroupBox("📊 Test Sonuçları")
        results_layout = QVBoxLayout()
        
        self.test_summary = QLabel("Test henüz çalıştırılmadı")
        self.test_summary.setStyleSheet("padding: 10px; font-size: 14px;")
        results_layout.addWidget(self.test_summary)
        
        self.test_table = QTableWidget()
        self.test_table.setColumnCount(3)
        self.test_table.setHorizontalHeaderLabels(["Satır", "msgid", "Durum"])
        self.test_table.horizontalHeader().setStretchLastSection(True)
        self.test_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        results_layout.addWidget(self.test_table)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        self.tabs.addTab(tab, "🔍 Test")
    
    def create_gemini_tab(self):
        """Gemini kalite kontrol sekmesi - İYİLEŞTİRİLMİŞ LAYOUT"""
        tab = QWidget()
        main_layout = QHBoxLayout(tab)
        
        # SOL PANEL - Ayarlar
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(400)
        
        # Dosya seçimi
        file_group = QGroupBox("📁 Dosya Seçimi")
        file_layout = QVBoxLayout()
        
        file_select_layout = QHBoxLayout()
        self.gemini_file_path = QLineEdit()
        self.gemini_file_path.setPlaceholderText("PO dosyası seçin...")
        file_select_layout.addWidget(self.gemini_file_path, 1)
        btn_gemini_browse = QPushButton("📂")
        btn_gemini_browse.setMaximumWidth(50)
        btn_gemini_browse.clicked.connect(self.browse_gemini_file)
        file_select_layout.addWidget(btn_gemini_browse)
        file_layout.addLayout(file_select_layout)
        
        file_group.setLayout(file_layout)
        left_layout.addWidget(file_group)
        
        # Dil seçimi
        lang_select_group = QGroupBox("🌐 Çeviri Dili")
        lang_select_layout = QVBoxLayout()
        
        lang_select_layout.addWidget(QLabel("msgstr alanlarının dili:"))
        self.target_lang_combo = QComboBox()
        for lang_code, lang_info in LANGUAGES.items():
            self.target_lang_combo.addItem(
                f"{lang_info['flag']} {lang_info['name']}", 
                lang_code
            )
        lang_select_layout.addWidget(self.target_lang_combo)
        
        lang_info_label = QLabel("⚠️ Kontrol edilecek dosyanın dilini seçin")
        lang_info_label.setStyleSheet("color: #e67e22; font-style: italic; font-size: 11px;")
        lang_info_label.setWordWrap(True)
        lang_select_layout.addWidget(lang_info_label)
        
        lang_select_group.setLayout(lang_select_layout)
        left_layout.addWidget(lang_select_group)
        
        # Kontrol ayarları
        settings_group = QGroupBox("⚙️ Kontrol Ayarları")
        settings_layout = QVBoxLayout()
        
        self.check_meaning = QCheckBox("✓ Anlam bütünlüğü")
        self.check_meaning.setChecked(True)
        settings_layout.addWidget(self.check_meaning)
        
        self.check_technical = QCheckBox("✓ Teknik terimler")
        self.check_technical.setChecked(True)
        settings_layout.addWidget(self.check_technical)
        
        self.check_format = QCheckBox("✓ Format & placeholder")
        self.check_format.setChecked(True)
        settings_layout.addWidget(self.check_format)
        
        self.check_grammar = QCheckBox("✓ Dilbilgisi")
        self.check_grammar.setChecked(True)
        settings_layout.addWidget(self.check_grammar)
        
        self.check_alternatives = QCheckBox("✓ Alternatif öneri")
        self.check_alternatives.setChecked(True)
        settings_layout.addWidget(self.check_alternatives)
        
        # Minimum skor
        score_layout = QVBoxLayout()
        score_layout.addWidget(QLabel("Minimum Kabul Skoru:"))
        self.min_score_slider = QSlider(Qt.Orientation.Horizontal)
        self.min_score_slider.setMinimum(0)
        self.min_score_slider.setMaximum(100)
        self.min_score_slider.setValue(75)
        self.min_score_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.min_score_slider.setTickInterval(10)
        score_layout.addWidget(self.min_score_slider)
        self.min_score_label = QLabel("75")
        self.min_score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.min_score_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.min_score_slider.valueChanged.connect(
            lambda v: self.min_score_label.setText(str(v))
        )
        score_layout.addWidget(self.min_score_label)
        settings_layout.addLayout(score_layout)
        
        # Kontrol modu
        mode_layout = QVBoxLayout()
        mode_layout.addWidget(QLabel("Kontrol Modu:"))
        
        self.check_mode_group = QButtonGroup()
        
        self.mode_all = QRadioButton("⦿ Tümünü kontrol et")
        self.mode_all.setChecked(True)
        self.check_mode_group.addButton(self.mode_all)
        mode_layout.addWidget(self.mode_all)
        
        self.mode_empty = QRadioButton("○ Sadece boş msgstr")
        self.check_mode_group.addButton(self.mode_empty)
        mode_layout.addWidget(self.mode_empty)
        
        self.mode_long = QRadioButton("○ Sadece uzun metinler")
        self.check_mode_group.addButton(self.mode_long)
        mode_layout.addWidget(self.mode_long)
        
        settings_layout.addLayout(mode_layout)
        settings_group.setLayout(settings_layout)
        left_layout.addWidget(settings_group)
        
        # API durumu
        api_group = QGroupBox("🔑 API Durumu")
        api_layout = QVBoxLayout()
        
        self.gemini_api_status = QLabel("📊 Gemini API: ✅ Hazır")
        self.gemini_api_status.setStyleSheet("color: green; font-weight: bold;")
        api_layout.addWidget(self.gemini_api_status)
        
        api_group.setLayout(api_layout)
        left_layout.addWidget(api_group)
        
        # İlerleme
        progress_group = QGroupBox("📊 İlerleme")
        progress_layout = QVBoxLayout()
        
        self.gemini_progress = QProgressBar()
        progress_layout.addWidget(self.gemini_progress)
        
        self.gemini_status = QLabel("Hazır")
        self.gemini_status.setWordWrap(True)
        progress_layout.addWidget(self.gemini_status)
        
        progress_group.setLayout(progress_layout)
        left_layout.addWidget(progress_group)
        
        # Butonlar
        btn_layout = QVBoxLayout()
        
        self.btn_start_gemini = QPushButton("🤖 KONTROLÜ BAŞLAT")
        self.btn_start_gemini.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.btn_start_gemini.clicked.connect(self.start_gemini_check)
        btn_layout.addWidget(self.btn_start_gemini)
        
        self.btn_stop_gemini = QPushButton("⛔ DURDUR")
        self.btn_stop_gemini.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.btn_stop_gemini.setEnabled(False)
        self.btn_stop_gemini.clicked.connect(self.stop_gemini_check)
        btn_layout.addWidget(self.btn_stop_gemini)
        
        left_layout.addLayout(btn_layout)
        left_layout.addStretch()
        
        # SAĞ PANEL - Sonuçlar
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Özet istatistikler - ÜST KISIMDA SABİT
        stats_group = QGroupBox("📊 Durum Raporu")
        stats_layout = QVBoxLayout()
        
        self.gemini_stats_label = QLabel("Kontrol başlatılmadı")
        self.gemini_stats_label.setStyleSheet("""
            QLabel {
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 5px;
                font-size: 13px;
                font-family: 'Courier New', monospace;
            }
        """)
        self.gemini_stats_label.setWordWrap(True)
        stats_layout.addWidget(self.gemini_stats_label)
        
        stats_group.setLayout(stats_layout)
        stats_group.setMaximumHeight(200)
        right_layout.addWidget(stats_group)
        
        # Sonuçlar scroll area
        results_label = QLabel("📋 Kontrol Sonuçları:")
        results_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        right_layout.addWidget(results_label)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.gemini_results_layout = QVBoxLayout(scroll_widget)
        self.gemini_results_layout.addStretch()
        scroll.setWidget(scroll_widget)
        right_layout.addWidget(scroll)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)
        
        self.tabs.addTab(tab, "🤖 Gemini Kontrol")
    
    def create_results_tab(self):
        """Sonuçlar sekmesi"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Özet istatistikler
        stats_group = QGroupBox("📊 Özet İstatistikler")
        stats_layout = QVBoxLayout()
        
        self.stats_label = QTextEdit()
        self.stats_label.setReadOnly(True)
        self.stats_label.setMaximumHeight(150)
        stats_layout.addWidget(self.stats_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Detaylı sonuçlar tablosu
        results_group = QGroupBox("📋 Detaylı Sonuçlar")
        results_layout = QVBoxLayout()
        
        # Filtre butonları
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filtre:"))
        
        self.filter_all = QPushButton("Tümü")
        self.filter_all.clicked.connect(lambda: self.filter_gemini_results("all"))
        filter_layout.addWidget(self.filter_all)
        
        self.filter_perfect = QPushButton("✅ Mükemmel")
        self.filter_perfect.clicked.connect(lambda: self.filter_gemini_results("perfect"))
        filter_layout.addWidget(self.filter_perfect)
        
        self.filter_warnings = QPushButton("⚠️ Uyarılar")
        self.filter_warnings.clicked.connect(lambda: self.filter_gemini_results("warnings"))
        filter_layout.addWidget(self.filter_warnings)
        
        self.filter_errors = QPushButton("❌ Hatalar")
        self.filter_errors.clicked.connect(lambda: self.filter_gemini_results("errors"))
        filter_layout.addWidget(self.filter_errors)
        
        filter_layout.addStretch()
        results_layout.addLayout(filter_layout)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Durum", "Skor", "msgid", "msgstr", "Sorunlar", "Öneri"
        ])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        results_layout.addWidget(self.results_table)
        
        # Detay paneli
        detail_group = QGroupBox("📄 Detaylı Analiz")
        detail_layout = QVBoxLayout()
        
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(200)
        detail_layout.addWidget(self.detail_text)
        
        detail_group.setLayout(detail_layout)
        results_layout.addWidget(detail_group)
        
        # Toplu işlemler
        bulk_layout = QHBoxLayout()
        
        self.btn_apply_suggestions = QPushButton("✓ Seçili Önerileri Uygula")
        self.btn_apply_suggestions.clicked.connect(self.apply_selected_suggestions)
        bulk_layout.addWidget(self.btn_apply_suggestions)
        
        self.btn_save_corrected = QPushButton("💾 Düzeltilmiş Dosyayı Kaydet")
        self.btn_save_corrected.clicked.connect(self.save_corrected_file)
        bulk_layout.addWidget(self.btn_save_corrected)
        
        self.btn_export_report = QPushButton("📄 Rapor Oluştur")
        self.btn_export_report.clicked.connect(self.export_report)
        bulk_layout.addWidget(self.btn_export_report)
        
        bulk_layout.addStretch()
        results_layout.addLayout(bulk_layout)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Tablo satır seçimi eventi
        self.results_table.itemSelectionChanged.connect(self.show_result_detail)
        
        self.tabs.addTab(tab, "📊 Sonuçlar")
    
    # =====================================================
    # Event Handlers - Çeviri
    # =====================================================
    
    def browse_input(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "PO Dosyası Seç", "", "PO Files (*.po)"
        )
        if file_path:
            self.input_path.setText(file_path)
    
    def browse_output(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Çıkış Dizini Seç")
        if dir_path:
            self.output_dir.setText(dir_path)
    
    def select_all_langs(self):
        for cb in self.lang_checkboxes.values():
            cb.setChecked(True)
    
    def clear_all_langs(self):
        for cb in self.lang_checkboxes.values():
            cb.setChecked(False)
    
    def start_translation(self):
        if not self.input_path.text():
            QMessageBox.warning(self, "Uyarı", "Lütfen kaynak PO dosyasını seçin!")
            return
        
        if not self.output_dir.text():
            QMessageBox.warning(self, "Uyarı", "Lütfen çıkış dizinini seçin!")
            return
        
        selected_langs = [code for code, cb in self.lang_checkboxes.items() if cb.isChecked()]
        if not selected_langs:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir hedef dil seçin!")
            return
        
        # Yedek al
        self.create_backup(self.input_path.text())
        
        self.translation_worker = TranslationWorker(
            self.input_path.text(),
            self.output_dir.text(),
            selected_langs,
            self.force_retranslate.isChecked()
        )
        
        self.translation_worker.progress.connect(self.update_translation_progress)
        self.translation_worker.finished.connect(self.translation_finished)
        self.translation_worker.error.connect(self.translation_error)
        
        self.btn_start_translation.setEnabled(False)
        self.btn_stop_translation.setEnabled(True)
        
        self.translation_worker.start()
    
    def stop_translation(self):
        if self.translation_worker:
            self.translation_worker.stop()
            self.translation_status.setText("⛔ Çeviri durduruldu")
            self.btn_start_translation.setEnabled(True)
            self.btn_stop_translation.setEnabled(False)
    
    def update_translation_progress(self, value, message):
        self.translation_progress.setValue(value)
        self.translation_status.setText(message)
        self.statusBar().showMessage(message)
    
    def translation_finished(self, results):
        self.btn_start_translation.setEnabled(True)
        self.btn_stop_translation.setEnabled(False)
        self.translation_progress.setValue(100)
        self.translation_status.setText("✅ Tüm çeviriler tamamlandı!")
        
        # İstatistikleri güncelle
        stats_text = "🎉 ÇEVİRİ TAMAMLANDI!\n\n"
        
        total_translated = sum(d['translated'] for d in results.values())
        total_errors = sum(d['errors'] for d in results.values())
        
        stats_text += f"✅ Toplam Çevrilen: {total_translated}\n"
        stats_text += f"⚠️ Hata: {total_errors}\n\n"
        
        stats_text += "Dil Detayları:\n"
        for lang_code, data in results.items():
            stats_text += f"\n{LANGUAGES[lang_code]['flag']} {data['name']}:\n"
            stats_text += f"  • Çevrilen: {data['translated']}\n"
            stats_text += f"  • Atlanan: {data['skipped']}\n"
            stats_text += f"  • Hata: {data['errors']}\n"
            stats_text += f"  • Dosya: {data['output']}\n"
        
        self.stats_label.setText(stats_text)
        
        # Sonuçlar sekmesine geç
        self.tabs.setCurrentIndex(3)
        
        QMessageBox.information(
            self, 
            "Başarılı", 
            f"Çeviri tamamlandı!\n\n{total_translated} alan çevrildi."
        )
    
    def translation_error(self, error_msg):
        self.btn_start_translation.setEnabled(True)
        self.btn_stop_translation.setEnabled(False)
        self.translation_status.setText(f"❌ Hata: {error_msg}")
        QMessageBox.critical(self, "Hata", error_msg)
    
    # =====================================================
    # Event Handlers - Test
    # =====================================================
    
    def browse_test_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Test Edilecek PO Dosyası", "", "PO Files (*.po)"
        )
        if file_path:
            self.test_file_path.setText(file_path)
    
    def run_test(self):
        if not self.test_file_path.text():
            QMessageBox.warning(self, "Uyarı", "Lütfen test edilecek dosyayı seçin!")
            return
        
        self.test_worker = TestWorker(self.test_file_path.text())
        self.test_worker.finished.connect(self.test_finished)
        self.test_worker.error.connect(self.test_error)
        
        self.btn_run_test.setEnabled(False)
        self.test_worker.start()
    
    def test_finished(self, results):
        self.btn_run_test.setEnabled(True)
        
        # Özet
        summary = f"""
📊 TEST SONUÇLARI

Toplam Çeviri: {results['total']}
✅ Dolu: {results['filled']} ({results['completion_rate']:.1f}%)
❌ Boş: {results['empty']} ({100-results['completion_rate']:.1f}%)
"""
        self.test_summary.setText(summary)
        
        # Tabloyu doldur
        self.test_table.setRowCount(len(results['empty_items']))
        for i, item in enumerate(results['empty_items']):
            self.test_table.setItem(i, 0, QTableWidgetItem(str(item.line_number)))
            self.test_table.setItem(i, 1, QTableWidgetItem(item.msgid[:100]))
            
            status_item = QTableWidgetItem("❌ BOŞ")
            status_item.setBackground(QColor(255, 200, 200))
            self.test_table.setItem(i, 2, status_item)
    
    def test_error(self, error_msg):
        self.btn_run_test.setEnabled(True)
        QMessageBox.critical(self, "Hata", error_msg)
    
    def fill_turkish_empty(self):
        """Boş msgstr alanlarını msgid ile doldur (Türkçe dosyalar için)"""
        if not self.test_file_path.text():
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir dosya seçin ve test edin!")
            return
        
        reply = QMessageBox.question(
            self,
            "Onay",
            "Boş msgstr alanları msgid değerleri ile doldurulacak. Devam edilsin mi?\n\n"
            "NOT: Orijinal dosya yedeklenecektir.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        try:
            file_path = self.test_file_path.text()
            
            # Yedek al
            backup_path = self.create_backup(file_path)
            
            # Dosyayı oku
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse et
            items = POFileParser.parse(content)
            
            # Boş olanları doldur
            filled_count = 0
            for item in items:
                if not item.msgstr.strip():
                    item.msgstr = item.msgid
                    item.translated = True
                    filled_count += 1
            
            # Kaydet
            new_content = POFileParser.update_po_file(content, items)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            QMessageBox.information(
                self,
                "Başarılı",
                f"✅ {filled_count} boş alan Türkçe ile dolduruldu!\n\n"
                f"Yedek: {backup_path}"
            )
            
            # Testi yeniden çalıştır
            self.run_test()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Doldurma hatası: {str(e)}")
    
    def move_empty_to_bottom(self):
        """Boş msgstr alanlarını dosyanın en altına taşı"""
        if not self.test_file_path.text():
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir dosya seçin!")
            return
        
        reply = QMessageBox.question(
            self,
            "Onay",
            "Boş msgstr alanları dosyanın en altına taşınacak.\n\n"
            "Bu işlem dosya yapısını değiştirir. Devam edilsin mi?\n\n"
            "NOT: Orijinal dosya yedeklenecektir.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.No:
            return
        
        try:
            file_path = self.test_file_path.text()
            
            # Yedek al
            backup_path = self.create_backup(file_path)
            
            # Dosyayı oku
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # PO dosyasını parse et - entry'leri ayır
            entries = self.parse_po_entries(original_content)
            
            if not entries:
                QMessageBox.warning(self, "Uyarı", "Dosyada çeviri bulunamadı!")
                return
            
            # Header'ı ayır (dosyanın başındaki yorumlar ve metadata)
            header = self.extract_po_header(original_content)
            
            # Dolu ve boş olanları ayır
            filled_entries = []
            empty_entries = []
            
            for entry in entries:
                if entry['msgstr'].strip():
                    filled_entries.append(entry)
                else:
                    empty_entries.append(entry)
            
            # Yeni dosya içeriği oluştur
            new_content = header + "\n\n"
            
            # Önce dolu olanlar
            new_content += "# ==============================================\n"
            new_content += "# ÇEVRILMIŞ ALANLAR\n"
            new_content += "# ==============================================\n\n"
            for entry in filled_entries:
                new_content += self.format_po_entry(entry) + "\n\n"
            
            # Sonra boş olanlar
            if empty_entries:
                new_content += "# ==============================================\n"
                new_content += "# ÇEVRİLMEMİŞ ALANLAR (BOŞ)\n"
                new_content += "# ==============================================\n\n"
                for entry in empty_entries:
                    new_content += self.format_po_entry(entry) + "\n\n"
            
            # Dosyayı kaydet
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            QMessageBox.information(
                self,
                "Başarılı",
                f"✅ Dosya düzenlendi!\n\n"
                f"📝 Dolu alanlar: {len(filled_entries)}\n"
                f"📭 Boş alanlar: {len(empty_entries)}\n\n"
                f"Boş alanlar dosyanın en altına taşındı.\n\n"
                f"💾 Yedek: {backup_path}"
            )
            
            # Testi yeniden çalıştır
            self.run_test()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Taşıma hatası: {str(e)}")
    
    def extract_po_header(self, content: str) -> str:
        """PO dosyasının header kısmını çıkar"""
        lines = content.split('\n')
        header_lines = []
        
        for line in lines:
            # İlk msgid bulunana kadar olan kısım header
            if line.strip().startswith('msgid ') and 'msgid ""' not in line:
                break
            header_lines.append(line)
        
        return '\n'.join(header_lines).rstrip()
    
    def parse_po_entries(self, content: str) -> list:
        """PO dosyasındaki tüm entry'leri parse et"""
        entries = []
        
        # Her entry'yi ayıkla (msgid'den sonraki msgstr'e kadar)
        pattern = r'((?:#.*\n)*)(msgid\s+"[^"]*"(?:\s*\n"[^"]*")*\s*\nmsgstr\s+"[^"]*"(?:\s*\n"[^"]*")*)'
        
        matches = re.finditer(pattern, content, re.MULTILINE)
        
        for match in matches:
            comments = match.group(1)
            entry_text = match.group(2)
            
            # msgid ve msgstr'i ayıkla
            msgid_match = re.search(r'msgid\s+"([^"]*)"', entry_text)
            msgstr_match = re.search(r'msgstr\s+"([^"]*)"', entry_text)
            
            if msgid_match:
                msgid = msgid_match.group(1)
                msgstr = msgstr_match.group(1) if msgstr_match else ""
                
                # Boş msgid'leri atla
                if msgid.strip():
                    entries.append({
                        'comments': comments,
                        'msgid': msgid,
                        'msgstr': msgstr,
                        'full_text': match.group(0)
                    })
        
        return entries
    
    def format_po_entry(self, entry: dict) -> str:
        """Entry'yi PO formatında formatla"""
        result = entry['comments']
        result += f'msgid "{entry["msgid"]}"\n'
        result += f'msgstr "{entry["msgstr"]}"'
        return result
    
    # =====================================================
    # Event Handlers - Gemini (İYİLEŞTİRİLMİŞ)
    # =====================================================
    
    def browse_gemini_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Kontrol Edilecek PO Dosyası", "", "PO Files (*.po)"
        )
        if file_path:
            self.gemini_file_path.setText(file_path)
    
    def start_gemini_check(self):
        if not self.gemini_file_path.text():
            QMessageBox.warning(self, "Uyarı", "Lütfen kontrol edilecek dosyayı seçin!")
            return
        
        try:
            # Dosyayı oku ve parse et
            with open(self.gemini_file_path.text(), 'r', encoding='utf-8') as f:
                content = f.read()
            
            items = POFileParser.parse(content)
            self.current_items = items
            
            if not items:
                QMessageBox.warning(self, "Uyarı", "Dosyada çeviri bulunamadı!")
                return
            
            # Kontrol modunu belirle
            if self.mode_all.isChecked():
                check_mode = "all"
            elif self.mode_empty.isChecked():
                check_mode = "empty"
            else:
                check_mode = "long"
            
            # Hedef dili al
            target_lang = self.target_lang_combo.currentData()
            
            self.gemini_worker = GeminiWorker(
                items,
                self.check_meaning.isChecked(),
                self.check_technical.isChecked(),
                self.check_format.isChecked(),
                self.check_grammar.isChecked(),
                self.check_alternatives.isChecked(),
                self.min_score_slider.value(),
                check_mode,
                target_lang,
                "TR"
            )
            
            self.gemini_worker.progress.connect(self.update_gemini_progress)
            self.gemini_worker.item_checked.connect(self.gemini_item_checked)
            self.gemini_worker.finished.connect(self.gemini_finished)
            self.gemini_worker.error.connect(self.gemini_error)
            
            self.btn_start_gemini.setEnabled(False)
            self.btn_stop_gemini.setEnabled(True)
            
            # Önceki sonuçları temizle
            self.gemini_results = []
            for i in reversed(range(self.gemini_results_layout.count())):
                widget = self.gemini_results_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            # İstatistikleri sıfırla
            self.gemini_stats_label.setText("🤖 Kontrol başlatıldı...\n\nLütfen bekleyin...")
            
            self.gemini_worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dosya okuma hatası: {str(e)}")
    
    def stop_gemini_check(self):
        if self.gemini_worker:
            self.gemini_worker.stop()
            self.gemini_status.setText("⛔ Kontrol durduruldu")
            self.btn_start_gemini.setEnabled(True)
            self.btn_stop_gemini.setEnabled(False)
    
    def update_gemini_progress(self, value, message):
        self.gemini_progress.setValue(value)
        self.gemini_status.setText(message)
        self.statusBar().showMessage(message)
    
    def gemini_item_checked(self, index, item_result):
        """Her kontrol edilen item için kart oluştur - OPTİMİZE EDİLMİŞ"""
        item = item_result['item']
        result = item_result['result']
        
        self.gemini_results.append(item_result)
        
        # Anlık istatistik güncellemesi
        self.update_gemini_stats()
        
        # Kart widget
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        card.setLineWidth(2)
        
        status = result.status
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {status.color};
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }}
        """)
        
        card_layout = QVBoxLayout(card)
        
        # Header
        header_layout = QHBoxLayout()
        
        status_label = QLabel(f"{status.icon} {status.label}")
        status_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(status_label)
        
        score_label = QLabel(f"Skor: {result.overall_score}/100")
        score_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(score_label)
        
        header_layout.addStretch()
        
        line_label = QLabel(f"Satır: {item.line_number}")
        header_layout.addWidget(line_label)
        
        card_layout.addLayout(header_layout)
        
        # Çeviri
        msgid_label = QLabel(f"<b>msgid:</b> {item.msgid[:100]}")
        msgid_label.setWordWrap(True)
        card_layout.addWidget(msgid_label)
        
        if item.msgstr.strip():
            msgstr_label = QLabel(f"<b>msgstr:</b> {item.msgstr[:100]}")
        else:
            msgstr_label = QLabel(f"<b>msgstr:</b> <i style='color: #e74c3c;'>[BOŞ]</i>")
        msgstr_label.setWordWrap(True)
        card_layout.addWidget(msgstr_label)
        
        # Sorunlar
        if result.issues:
            issues_text = "<b>⚠️ Sorunlar:</b><br>" + "<br>".join(f"• {issue}" for issue in result.issues[:3])
            issues_label = QLabel(issues_text)
            issues_label.setWordWrap(True)
            card_layout.addWidget(issues_label)
        
        # Öneri
        if result.suggestion and result.suggestion != item.msgstr:
            suggestion_type = "🤖 YZ Çevirisi" if not item.msgstr.strip() else "💡 Öneri"
            suggestion_label = QLabel(f"<b>{suggestion_type}:</b> {result.suggestion[:100]}")
            suggestion_label.setWordWrap(True)
            
            if not item.msgstr.strip():
                suggestion_label.setStyleSheet("background-color: #e8f5e9; padding: 8px; border-radius: 5px; color: #1b5e20; font-weight: bold;")
            else:
                suggestion_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
            
            card_layout.addWidget(suggestion_label)
            
            # Öneriyi uygula butonu
            btn_apply = QPushButton("✓ Öneriyi Kullan")
            btn_apply.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    padding: 6px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
            btn_apply.clicked.connect(lambda checked, idx=index: self.apply_suggestion(idx))
            card_layout.addWidget(btn_apply)
        
        # Yorum
        if result.comment:
            comment_label = QLabel(f"<i>{result.comment[:100]}</i>")
            comment_label.setWordWrap(True)
            card_layout.addWidget(comment_label)
        
        # Kartı en üste ekle (yeni sonuçlar üstte görünsün)
        self.gemini_results_layout.insertWidget(0, card)
    
    def update_gemini_stats(self):
        """Anlık istatistikleri güncelle"""
        if not self.gemini_results:
            return
        
        total = len(self.gemini_results)
        perfect = sum(1 for r in self.gemini_results if r['result'].status == QualityStatus.PERFECT)
        good = sum(1 for r in self.gemini_results if r['result'].status == QualityStatus.GOOD)
        moderate = sum(1 for r in self.gemini_results if r['result'].status == QualityStatus.MODERATE)
        weak = sum(1 for r in self.gemini_results if r['result'].status == QualityStatus.WEAK)
        poor = sum(1 for r in self.gemini_results if r['result'].status == QualityStatus.POOR)
        
        avg_score = sum(r['result'].overall_score for r in self.gemini_results) / total if total > 0 else 0
        suggestions = sum(1 for r in self.gemini_results if r['result'].suggestion)
        
        stats_text = f"""📊 DURUM RAPORU (Canlı)

✓ Kontrol Edilen: {total}
⭐ Ortalama Skor: {avg_score:.1f}/100

🎯 Durum Dağılımı:
  🟢 Mükemmel: {perfect}
  🟢 İyi: {good}
  🟡 Orta: {moderate}
  🟠 Zayıf: {weak}
  🔴 Hatalı: {poor}

💡 Öneriler: {suggestions}
⚠️ Dikkat: {moderate + weak + poor}"""
        
        self.gemini_stats_label.setText(stats_text)
    
    def gemini_finished(self, results):
        self.btn_start_gemini.setEnabled(True)
        self.btn_stop_gemini.setEnabled(False)
        self.gemini_progress.setValue(100)
        self.gemini_status.setText("✅ Kontrol tamamlandı!")
        
        # İstatistikleri güncelle
        stats_text = f"""
🤖 GEMİNİ KALİTE KONTROL RAPORU

📊 Genel İstatistikler:
─────────────────────────
Toplam Kontrol: {results['total']}
Ortalama Skor: {results['average_score']:.1f}/100

🎯 Durum Dağılımı:
─────────────────────────
✅ Mükemmel (90-100): {results['perfect']} ({results['perfect']/results['total']*100:.1f}%)
✅ İyi (80-89): {results['good']} ({results['good']/results['total']*100:.1f}%)
🟡 Orta (70-79): {results['moderate']} ({results['moderate']/results['total']*100:.1f}%)
🟠 Zayıf (60-69): {results['weak']} ({results['weak']/results['total']*100:.1f}%)
🔴 Hatalı (<60): {results['poor']} ({results['poor']/results['total']*100:.1f}%)

💡 Öneriler: {sum(1 for r in results['items'] if r['result'].suggestion)}
⚠️ Dikkat Gereken: {results['moderate'] + results['weak'] + results['poor']}
"""
        
        self.stats_label.setText(stats_text)
        
        # Sonuçlar tablosunu doldur
        self.populate_results_table(results['items'])
        
        # Sonuçlar sekmesine geç
        self.tabs.setCurrentIndex(3)
        
        QMessageBox.information(
            self,
            "Başarılı",
            f"Gemini kontrolü tamamlandı!\n\n"
            f"Ortalama Skor: {results['average_score']:.1f}/100\n"
            f"Dikkat Gereken: {results['moderate'] + results['weak'] + results['poor']}"
        )
    
    def gemini_error(self, error_msg):
        self.btn_start_gemini.setEnabled(True)
        self.btn_stop_gemini.setEnabled(False)
        self.gemini_status.setText(f"❌ Hata: {error_msg}")
        QMessageBox.critical(self, "Hata", error_msg)
    
    def apply_suggestion(self, index):
        """Belirli bir önerinin uygulanması"""
        if index >= len(self.gemini_results):
            return
        
        item_result = self.gemini_results[index]
        item = item_result['item']
        result = item_result['result']
        
        if result.suggestion:
            item.msgstr = result.suggestion
            item.translated = True
            
            QMessageBox.information(
                self,
                "Başarılı",
                f"Öneri uygulandı!\n\n"
                f"Yeni msgstr: {result.suggestion[:100]}"
            )
    
    # =====================================================
    # Event Handlers - Sonuçlar
    # =====================================================
    
    def populate_results_table(self, items):
        """Sonuçlar tablosunu doldur"""
        self.results_table.setRowCount(len(items))
        
        for i, item_result in enumerate(items):
            item = item_result['item']
            result = item_result['result']
            
            # Durum
            status_item = QTableWidgetItem(f"{result.status.icon} {result.status.label}")
            status_item.setBackground(QColor(result.status.color))
            self.results_table.setItem(i, 0, status_item)
            
            # Skor
            score_item = QTableWidgetItem(str(result.overall_score))
            self.results_table.setItem(i, 1, score_item)
            
            # msgid
            msgid_item = QTableWidgetItem(item.msgid[:50] + "..." if len(item.msgid) > 50 else item.msgid)
            self.results_table.setItem(i, 2, msgid_item)
            
            # msgstr
            msgstr_text = item.msgstr[:50] if item.msgstr.strip() else "[BOŞ]"
            msgstr_item = QTableWidgetItem(msgstr_text + "..." if len(msgstr_text) > 50 else msgstr_text)
            self.results_table.setItem(i, 3, msgstr_item)
            
            # Sorunlar
            issues_text = ", ".join(result.issues[:2]) if result.issues else "-"
            issues_item = QTableWidgetItem(issues_text[:50])
            self.results_table.setItem(i, 4, issues_item)
            
            # Öneri
            suggestion_text = result.suggestion[:50] if result.suggestion else "-"
            suggestion_item = QTableWidgetItem(suggestion_text)
            self.results_table.setItem(i, 5, suggestion_item)
    
    def filter_gemini_results(self, filter_type):
        """Sonuçları filtrele"""
        if not self.gemini_results:
            return
        
        filtered_items = []
        
        for item_result in self.gemini_results:
            result = item_result['result']
            
            if filter_type == "all":
                filtered_items.append(item_result)
            elif filter_type == "perfect" and result.status == QualityStatus.PERFECT:
                filtered_items.append(item_result)
            elif filter_type == "warnings" and result.status in [QualityStatus.MODERATE, QualityStatus.WEAK]:
                filtered_items.append(item_result)
            elif filter_type == "errors" and result.status == QualityStatus.POOR:
                filtered_items.append(item_result)
        
        self.populate_results_table(filtered_items)
    
    def show_result_detail(self):
        """Seçili satırın detayını göster"""
        selected_rows = self.results_table.selectionModel().selectedRows()
        
        if not selected_rows or not self.gemini_results:
            return
        
        row = selected_rows[0].row()
        
        if row >= len(self.gemini_results):
            return
        
        item_result = self.gemini_results[row]
        item = item_result['item']
        result = item_result['result']
        
        detail_html = f"""
<div style='font-family: Arial; padding: 10px;'>
    <h3 style='color: #2c3e50;'>📋 Detaylı Analiz</h3>
    
    <p><b>Satır:</b> {item.line_number}</p>
    
    <p><b>msgid:</b><br>
    <span style='background-color: #ecf0f1; padding: 5px; display: block; border-radius: 3px;'>
    {item.msgid}
    </span></p>
    
    <p><b>msgstr:</b><br>
    <span style='background-color: {"#fee" if not item.msgstr.strip() else "#ecf0f1"}; padding: 5px; display: block; border-radius: 3px;'>
    {item.msgstr if item.msgstr.strip() else "<i style='color: red;'>[BOŞ]</i>"}
    </span></p>
    
    <hr>
"""
        
        if item.msgstr.strip():
            detail_html += f"""
    <h4>🎯 Skor Detayları:</h4>
    <ul>
        <li><b>Anlam:</b> {result.scores.get('meaning', 0)}/100</li>
        <li><b>Dilbilgisi:</b> {result.scores.get('grammar', 0)}/100</li>
        <li><b>Doğallık:</b> {result.scores.get('naturalness', 0)}/100</li>
        <li><b>Teknik:</b> {result.scores.get('technical', 0)}/100</li>
        <li><b>Format:</b> {result.scores.get('format', 0)}/100</li>
    </ul>
    
    <p><b>🎯 Genel Skor:</b> <span style='color: #e74c3c; font-size: 18px; font-weight: bold;'>{result.overall_score}/100</span></p>
"""
        else:
            detail_html += """
    <div style='background-color: #fff3cd; padding: 10px; border-radius: 5px; border-left: 4px solid #ffc107;'>
        <h4 style='margin-top: 0;'>⚠️ Çeviri Yapılmamış</h4>
        <p>Bu alan için henüz çeviri yapılmamış. Yapay zeka otomatik çeviri önerisi oluşturdu.</p>
    </div>
"""
        
        if result.issues:
            detail_html += "<h4>⚠️ Sorunlar:</h4><ul>"
            for issue in result.issues:
                detail_html += f"<li>{issue}</li>"
            detail_html += "</ul>"
        
        if result.suggestion:
            suggestion_type = "🤖 YZ Çevirisi" if not item.msgstr.strip() else "💡 İyileştirme"
            detail_html += f"""
    <h4>{suggestion_type}:</h4>
    <p style='background-color: {"#e8f5e9" if not item.msgstr.strip() else "#d4edda"}; padding: 10px; border-radius: 5px; color: #155724;'>
    <b>Önerilen:</b> {result.suggestion}
    </p>
"""
        
        if result.comment:
            detail_html += f"""
    <h4>💬 Yorum:</h4>
    <p style='background-color: #fff3cd; padding: 10px; border-radius: 5px;'>
    {result.comment}
    </p>
"""
        
        detail_html += "</div>"
        
        self.detail_text.setHtml(detail_html)
    
    def apply_selected_suggestions(self):
        """Seçili önerileri uygula"""
        selected_rows = self.results_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce satırları seçin!")
            return
        
        applied_count = 0
        
        for row_index in selected_rows:
            row = row_index.row()
            
            if row >= len(self.gemini_results):
                continue
            
            item_result = self.gemini_results[row]
            result = item_result['result']
            
            if result.suggestion:
                item_result['item'].msgstr = result.suggestion
                item_result['item'].translated = True
                applied_count += 1
        
        if applied_count > 0:
            QMessageBox.information(
                self,
                "Başarılı",
                f"✅ {applied_count} öneri uygulandı!"
            )
    
    def save_corrected_file(self):
        """Düzeltilmiş dosyayı kaydet"""
        if not self.current_items:
            QMessageBox.warning(self, "Uyarı", "Kaydedilecek veri bulunamadı!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Düzeltilmiş Dosyayı Kaydet",
            "",
            "PO Files (*.po)"
        )
        
        if not file_path:
            return
        
        try:
            # Orijinal dosyayı oku
            with open(self.gemini_file_path.text(), 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Güncellenmiş içeriği oluştur
            new_content = POFileParser.update_po_file(content, self.current_items)
            
            # Kaydet
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            QMessageBox.information(
                self,
                "Başarılı",
                f"✅ Dosya kaydedildi!\n\n{file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kaydetme hatası: {str(e)}")
    
    def export_report(self):
        """HTML rapor oluştur"""
        if not self.gemini_results:
            QMessageBox.warning(self, "Uyarı", "Rapor oluşturulacak veri bulunamadı!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Raporu Kaydet",
            "gemini_quality_report.html",
            "HTML Files (*.html)"
        )
        
        if not file_path:
            return
        
        try:
            html_content = self.generate_html_report()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            QMessageBox.information(
                self,
                "Başarılı",
                f"✅ Rapor oluşturuldu!\n\n{file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Rapor oluşturma hatası: {str(e)}")
    
    def generate_html_report(self):
        """HTML rapor içeriği oluştur"""
        
        # İstatistikler
        total = len(self.gemini_results)
        perfect = sum(1 for r in self.gemini_results if r['result'].status == QualityStatus.PERFECT)
        good = sum(1 for r in self.gemini_results if r['result'].status == QualityStatus.GOOD)
        moderate = sum(1 for r in self.gemini_results if r['result'].status == QualityStatus.MODERATE)
        weak = sum(1 for r in self.gemini_results if r['result'].status == QualityStatus.WEAK)
        poor = sum(1 for r in self.gemini_results if r['result'].status == QualityStatus.POOR)
        
        avg_score = sum(r['result'].overall_score for r in self.gemini_results) / total if total > 0 else 0
        
        html = f"""
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini Kalite Kontrol Raporu</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 30px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .stat-card h3 {{
            margin: 0;
            font-size: 36px;
        }}
        .stat-card p {{
            margin: 5px 0 0 0;
            opacity: 0.9;
        }}
        .status-distribution {{
            margin: 30px 0;
        }}
        .status-bar {{
            display: flex;
            height: 40px;
            border-radius: 5px;
            overflow: hidden;
            margin-bottom: 20px;
        }}
        .status-segment {{
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }}
        .results-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        .results-table th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        .results-table td {{
            padding: 10px;
            border-bottom: 1px solid #ecf0f1;
        }}
        .results-table tr:hover {{
            background: #f8f9fa;
        }}
        .status-badge {{
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: bold;
            display: inline-block;
        }}
        .perfect {{ background: #d4edda; color: #155724; }}
        .good {{ background: #d1ecf1; color: #0c5460; }}
        .moderate {{ background: #fff3cd; color: #856404; }}
        .weak {{ background: #ffe5cc; color: #cc6600; }}
        .poor {{ background: #f8d7da; color: #721c24; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Gemini Kalite Kontrol Raporu</h1>
        <p class="subtitle">Oluşturulma Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>{total}</h3>
                <p>Toplam Kontrol</p>
            </div>
            <div class="stat-card">
                <h3>{avg_score:.1f}</h3>
                <p>Ortalama Skor</p>
            </div>
            <div class="stat-card">
                <h3>{perfect + good}</h3>
                <p>Başarılı</p>
            </div>
            <div class="stat-card">
                <h3>{moderate + weak + poor}</h3>
                <p>Dikkat Gereken</p>
            </div>
        </div>
        
        <div class="status-distribution">
            <h2>Durum Dağılımı</h2>
            <div class="status-bar">
"""
        
        if perfect > 0:
            html += f'<div class="status-segment" style="width: {perfect/total*100}%; background: #28a745;">{perfect}</div>'
        if good > 0:
            html += f'<div class="status-segment" style="width: {good/total*100}%; background: #17a2b8;">{good}</div>'
        if moderate > 0:
            html += f'<div class="status-segment" style="width: {moderate/total*100}%; background: #ffc107;">{moderate}</div>'
        if weak > 0:
            html += f'<div class="status-segment" style="width: {weak/total*100}%; background: #fd7e14;">{weak}</div>'
        if poor > 0:
            html += f'<div class="status-segment" style="width: {poor/total*100}%; background: #dc3545;">{poor}</div>'
        
        html += """
            </div>
        </div>
        
        <h2>Detaylı Sonuçlar</h2>
        <table class="results-table">
            <thead>
                <tr>
                    <th>Satır</th>
                    <th>Durum</th>
                    <th>Skor</th>
                    <th>msgid</th>
                    <th>msgstr</th>
                    <th>Sorunlar</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for item_result in self.gemini_results:
            item = item_result['item']
            result = item_result['result']
            
            status_class = result.status.name.lower()
            issues_text = ", ".join(result.issues[:2]) if result.issues else "-"
            msgstr_display = item.msgstr[:60] if item.msgstr.strip() else "[BOŞ]"
            
            html += f"""
                <tr>
                    <td>{item.line_number}</td>
                    <td><span class="status-badge {status_class}">{result.status.icon} {result.status.label}</span></td>
                    <td><b>{result.overall_score}</b>/100</td>
                    <td>{item.msgid[:60]}...</td>
                    <td>{msgstr_display}...</td>
                    <td>{issues_text}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        
        return html
    
    # =====================================================
    # Yardımcı Fonksiyonlar
    # =====================================================
    
    def create_backup(self, file_path):
        """Dosya yedeği oluştur"""
        backup_dir = os.path.join(os.path.dirname(file_path), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}.bak")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return backup_path
            
        except Exception as e:
            print(f"Yedekleme hatası: {e}")
            return None

# =====================================================
# Ana Program
# =====================================================
def main():
    app = QApplication(sys.argv)
    
    # Modern tema
    app.setStyle("Fusion")
    
    # Açık tema
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()