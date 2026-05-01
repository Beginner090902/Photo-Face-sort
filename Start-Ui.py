import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
#from PySide6.QtCore import QCoreApplication
from PySide6.QtUiTools import QUiLoader
from src.custom_logging import setup_logger
from a_ordner_auswählen import start_select_folder, start_show_images_from_folder_in_qlistwidget
from src.g_db_settings_handler import SettingsHandler


loger = setup_logger(__name__)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # UI laden (passen Sie den Dateinamen an)
        loader = QUiLoader()
        self.ui = loader.load('QT-Ui/Main.ui')
        loger.info("UI geladen")
        self.ui.show()
        

        # Bilder
        self.ui.btn_load_folder.clicked.connect(lambda: start_select_folder(self.ui))
        self.ui.bilder_anzeigen.clicked.connect(lambda: start_show_images_from_folder_in_qlistwidget(self.ui))
        self.ui.bilder_laden_meldung.setVisible(False)

        # Einstellungen
        # In den Tab wechseln
        self.ui.tabWidget.currentChanged.connect(lambda: on_change_in_tab(self))
        # Thread anzahl ändern
        self.ui.spin_threads.valueChanged.connect(lambda: on_thread_changed())
        # Modus umstellen
        self.ui.combo_mode.currentTextChanged.connect(lambda: on_modus_changed())

        def make_settings_invisible():
            self.ui.spin_threads.setVisible(False)
            self.ui.label_threads.setVisible(False)
            self.ui.label_gpu_or_cpu.setVisible(False)
            self.ui.combo_mode.setVisible(False)

        def make_settings_visible():
            self.ui.spin_threads.setVisible(True)
            self.ui.label_threads.setVisible(True)
            self.ui.label_gpu_or_cpu.setVisible(True)
            self.ui.combo_mode.setVisible(True)

        def on_modus_changed():
            modus = self.ui.combo_mode.currentText()
            loger.info(f"Modus size changed to {modus}")
            folder_path = self.ui.selected_folder_path.text()
            db_path = str(folder_path)+"/db.db"
            Settingsdb = SettingsHandler(db_path)
            Settingsdb.mode = modus
            on_change_in_tab(self)

        def on_thread_changed():
            threads = self.ui.spin_threads.value()
            loger.info(f"Thread size changed to {threads}")
            folder_path = self.ui.selected_folder_path.text()
            db_path = str(folder_path)+"/db.db"
            Settingsdb = SettingsHandler(db_path)
            Settingsdb.threads = threads
            on_change_in_tab(self)

        def on_change_in_tab(self):
            index = self.ui.tabWidget.currentIndex()
            loger.info(f"Tab gewechselt zu index: {index}")

            
            # Oder nach Tab-Name
            if index == 6:
                folder_path = self.ui.selected_folder_path.text()
                if not folder_path:
                    make_settings_invisible()
                    self.ui.einstellungen_nachrichten_text.setText("Kein Ordner gelden")
                    loger.error(f"kein ordner gelden")
                    return
                make_settings_visible()
                self.ui.einstellungen_nachrichten_text.setText("Ordner gefunden")
                db_path = str(folder_path)+"/db.db"
                loger.info(f"db path {db_path}")
                Settingsdb = SettingsHandler(db_path)
                threads = Settingsdb.threads
                mode = Settingsdb.mode

                self.ui.combo_mode.setCurrentText(mode) 
                self.ui.spin_threads.setValue(threads)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

