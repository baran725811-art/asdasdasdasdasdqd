import sys
import os
import re
import time
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QFileDialog, 
    QProgressBar, QComboBox, QGroupBox, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QTabWidget,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette
import deepl

# =====================================================
# DeepL API KEY
# =====================================================
API_KEY = "64605b99-7c0c-481b-a28a-5dbd1b72377d:fx"

# =====================================================
# Dil Konfigürasyonları
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

# =====================================================
# Çeviri Thread Sınıfı
# =====================================================
class TranslationWorker(QThread):
    progress = pyqtSignal(int, str)  # progress, message
    finished = pyqtSignal(dict)  # results
    error = pyqtSignal(str)
    
    def __init__(self, input_path, output_dir, target_langs, force_retranslate):
        super().__init__()
        self.input_path = input_path
        self.output_dir = output_dir
        self.target_langs = target_langs
        self.force_retranslate = force_retranslate
        self.translator = deepl.Translator(API_KEY)
        self._is_running = True
        
    def stop(self):
        self._is_running = False
        
    def is_turkish_text(self, text):
        """Türkçe metin kontrolü"""
        if not text.strip():
            return False
        turkish_chars = set('çğıöşüÇĞIİÖŞÜ')
        turkish_words = {'için', 'olan', 'bir', 'bu', 'şu', 've', 'ile', 'gibi'}
        has_turkish = any(char in turkish_chars for char in text)
        words = re.findall(r'\b\w+\b', text.lower())
        turkish_count = sum(1 for w in words if w in turkish_words)
        return has_turkish or (len(words) > 0 and turkish_count / len(words) > 0.2)
    
    def translate_text(self, text, target_lang):
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
            return text
    
    def escape_po_string(self, text):
        """PO formatı için escape"""
        if not text:
            return '""'
        text = text.replace('\\', '\\\\')
        text = text.replace('"', '\\"')
        text = text.replace('\n', '\\n')
        text = text.replace('\t', '\\t')
        text = text.replace('\r', '\\r')
        return f'"{text}"'
    
    def run(self):
        try:
            # Dosyayı oku
            with open(self.input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            pattern = r'(msgid\s+"([^"]*)"\s*\n)(msgstr\s+"([^"]*)")'
            matches = list(re.finditer(pattern, content, re.MULTILINE))
            
            if not matches:
                self.error.emit("PO dosyasında çevrilebilir içerik bulunamadı!")
                return
            
            results = {}
            
            for lang_code in self.target_langs:
                if not self._is_running:
                    break
                    
                lang_name = LANGUAGES[lang_code]["name"]
                self.progress.emit(0, f"🌍 {lang_name} çevirisi başlıyor...")
                
                new_content = content
                translated = 0
                skipped = 0
                errors = 0
                empty_fields = []
                
                for i, match in enumerate(matches):
                    if not self._is_running:
                        break
                        
                    progress_pct = int((i + 1) / len(matches) * 100)
                    
                    full_match = match.group(0)
                    msgid_part = match.group(1)
                    msgid_text = match.group(2)
                    msgstr_part = match.group(3)
                    msgstr_text = match.group(4)
                    
                    if not msgid_text.strip():
                        continue
                    
                    # Zaten çevrilmiş mi?
                    if msgstr_text and not self.force_retranslate:
                        skipped += 1
                        continue
                    
                    self.progress.emit(
                        progress_pct, 
                        f"🔄 {lang_name}: '{msgid_text[:50]}...' çeviriliyor"
                    )
                    
                    # Çeviri yap
                    translated_text = self.translate_text(msgid_text, lang_code)
                    
                    if translated_text and translated_text != msgid_text:
                        new_msgstr = f'msgstr {self.escape_po_string(translated_text)}'
                        new_match = msgid_part + new_msgstr
                        new_content = new_content.replace(full_match, new_match, 1)
                        translated += 1
                    else:
                        errors += 1
                        empty_fields.append({
                            'line': i + 1,
                            'msgid': msgid_text,
                            'error': 'Çeviri başarısız'
                        })
                
                # Dosyayı kaydet
                output_path = os.path.join(self.output_dir, f"django_{lang_code.lower().replace('-', '_')}.po")
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                results[lang_code] = {
                    'name': lang_name,
                    'translated': translated,
                    'skipped': skipped,
                    'errors': errors,
                    'empty_fields': empty_fields,
                    'output': output_path,
                    'total': len(matches)
                }
                
                self.progress.emit(100, f"✅ {lang_name} tamamlandı!")
            
            self.finished.emit(results)
            
        except Exception as e:
            self.error.emit(f"Hata: {str(e)}")

# =====================================================
# Ana Pencere
# =====================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌍 PO Dosyası Çeviri Aracı Pro")
        self.setGeometry(100, 100, 1200, 800)
        self.worker = None
        
        # Ana widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # =====================================================
        # Başlık
        # =====================================================
        title = QLabel("🌍 PO DOSYASI ÇEVİRİ ARACI - PROFESSIONAL")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # =====================================================
        # Dosya Seçim Bölümü
        # =====================================================
        file_group = QGroupBox("📁 Dosya Seçimi")
        file_layout = QVBoxLayout()
        
        # Giriş dosyası
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Kaynak PO Dosyası:"))
        self.input_path = QLineEdit()
        self.input_path.setPlaceholderText("Çevrilecek .po dosyasını seçin...")
        input_layout.addWidget(self.input_path, 1)
        btn_browse = QPushButton("📂 Dosya Seç")
        btn_browse.clicked.connect(self.browse_input)
        input_layout.addWidget(btn_browse)
        file_layout.addLayout(input_layout)
        
        # Çıkış dizini
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Çıkış Dizini:"))
        self.output_dir = QLineEdit()
        self.output_dir.setPlaceholderText("Çevrilmiş dosyaların kaydedileceği dizin...")
        output_layout.addWidget(self.output_dir, 1)
        btn_output = QPushButton("📁 Dizin Seç")
        btn_output.clicked.connect(self.browse_output)
        output_layout.addWidget(btn_output)
        file_layout.addLayout(output_layout)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # =====================================================
        # Dil Seçimi
        # =====================================================
        lang_group = QGroupBox("🌐 Hedef Diller (Çoklu Seçim)")
        lang_layout = QVBoxLayout()
        
        self.lang_checkboxes = {}
        grid_layout = QHBoxLayout()
        
        for lang_code, lang_info in LANGUAGES.items():
            cb = QCheckBox(f"{lang_info['flag']} {lang_info['name']}")
            self.lang_checkboxes[lang_code] = cb
            grid_layout.addWidget(cb)
        
        # Hepsini seç/kaldır
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
        
        # =====================================================
        # Seçenekler
        # =====================================================
        options_group = QGroupBox("⚙️ Çeviri Seçenekleri")
        options_layout = QVBoxLayout()
        
        self.force_retranslate = QCheckBox("🔄 Zaten çevrilmiş alanları da yeniden çevir")
        self.force_retranslate.setToolTip("İşaretli ise, dolu msgstr alanları da yeniden çevrilir")
        options_layout.addWidget(self.force_retranslate)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # =====================================================
        # İlerleme
        # =====================================================
        progress_group = QGroupBox("📊 İlerleme Durumu")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Hazır")
        self.status_label.setStyleSheet("padding: 5px;")
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # =====================================================
        # Butonlar
        # =====================================================
        btn_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("🚀 ÇEVİRİYİ BAŞLAT")
        self.btn_start.setStyleSheet("""
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
        """)
        self.btn_start.clicked.connect(self.start_translation)
        btn_layout.addWidget(self.btn_start)
        
        self.btn_stop = QPushButton("⛔ DURDUR")
        self.btn_stop.setStyleSheet("""
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
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_translation)
        btn_layout.addWidget(self.btn_stop)
        
        layout.addLayout(btn_layout)
        
        # =====================================================
        # Sonuçlar Tablosu
        # =====================================================
        results_group = QGroupBox("📋 Çeviri Sonuçları")
        results_layout = QVBoxLayout()
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Dil", "Çevrilen", "Atlanan", "Hata", "Toplam", "Dosya"
        ])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        results_layout.addWidget(self.results_table)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
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
        # Doğrulama
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
        
        # Worker başlat
        self.worker = TranslationWorker(
            self.input_path.text(),
            self.output_dir.text(),
            selected_langs,
            self.force_retranslate.isChecked()
        )
        
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.translation_finished)
        self.worker.error.connect(self.translation_error)
        
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.results_table.setRowCount(0)
        
        self.worker.start()
    
    def stop_translation(self):
        if self.worker:
            self.worker.stop()
            self.status_label.setText("⛔ Çeviri durduruldu")
            self.btn_start.setEnabled(True)
            self.btn_stop.setEnabled(False)
    
    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def translation_finished(self, results):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.progress_bar.setValue(100)
        self.status_label.setText("✅ Tüm çeviriler tamamlandı!")
        
        # Tabloyu doldur
        self.results_table.setRowCount(len(results))
        for i, (lang_code, data) in enumerate(results.items()):
            self.results_table.setItem(i, 0, QTableWidgetItem(f"{LANGUAGES[lang_code]['flag']} {data['name']}"))
            self.results_table.setItem(i, 1, QTableWidgetItem(str(data['translated'])))
            self.results_table.setItem(i, 2, QTableWidgetItem(str(data['skipped'])))
            self.results_table.setItem(i, 3, QTableWidgetItem(str(data['errors'])))
            self.results_table.setItem(i, 4, QTableWidgetItem(str(data['total'])))
            self.results_table.setItem(i, 5, QTableWidgetItem(data['output']))
            
            # Hatalı satırları vurgula
            if data['errors'] > 0:
                for col in range(6):
                    item = self.results_table.item(i, col)
                    item.setBackground(QColor(255, 235, 235))
        
        # Özet mesaj
        total_translated = sum(d['translated'] for d in results.values())
        total_errors = sum(d['errors'] for d in results.values())
        
        msg = f"🎉 Çeviri Tamamlandı!\n\n"
        msg += f"✅ Toplam {total_translated} alan çevrildi\n"
        if total_errors > 0:
            msg += f"⚠️ {total_errors} alan çevrilemedi (manuel kontrol gerekli)\n"
        msg += f"\n📁 Dosyalar: {self.output_dir.text()}"
        
        QMessageBox.information(self, "Başarılı", msg)
    
    def translation_error(self, error_msg):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.status_label.setText(f"❌ Hata: {error_msg}")
        QMessageBox.critical(self, "Hata", error_msg)

# =====================================================
# Ana Program
# =====================================================
def main():
    app = QApplication(sys.argv)
    
    # Modern tema
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()