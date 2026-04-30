import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog
from PySide6.QtCore import QCoreApplication
from PySide6.QtUiTools import QUiLoader
from src.custom_logging import setup_logger
from a_ordner_auswählen import start_select_folder


loger = setup_logger(__name__)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # UI laden (passen Sie den Dateinamen an)
        loader = QUiLoader()
        self.ui = loader.load('QT-Ui/Main.ui')
        loger.info("UI geladen")
        self.ui.show()
        
        # Button mit Funktion verbinden
        self.ui.btn_load_folder.clicked.connect(lambda: start_select_folder(self.ui))
    
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())