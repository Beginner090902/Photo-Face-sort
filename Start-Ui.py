import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtCore import QCoreApplication
from PySide6.QtUiTools import QUiLoader
from src.custom_logging import setup_logger
from a_ordner_auswählen import start_select_folder
from g_settings import start_einstellung_db


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
        folder_path = self.ui.selected_folder_path.Text()

        #Einstellungen
        self.ui.tab_settings.clicked.connect(lambda: start_einstellung_db(self.ui))

    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())