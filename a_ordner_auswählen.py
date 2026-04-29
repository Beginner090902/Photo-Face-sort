# ordnerhandler.py (einfache Variante)
from PySide6.QtWidgets import QFileDialog,QListWidgetItem,QApplication
from PySide6.QtCore import QSize,Qt
from PySide6.QtGui import QPixmap, QIcon
from pathlib import Path
from peewee import SqliteDatabase
from src.custom_logging import setup_logger

loger = setup_logger(__name__)

db = SqliteDatabase("gesichter.db")
db.create_tables([])

def start_select_folder(parent_widget):
    folder_path = select_folder(parent_widget)
    parent_widget.selected_folder_path.setText(folder_path)
    show_images_from_folder_in_qlistwidget(folder_path,parent_widget)

def select_folder(parent_widget):
    """Einfache Funktion für Ordnerauswahl"""
    folder = QFileDialog.getExistingDirectory(
        parent_widget, 
        "Ordner auswählen", 
        "",
        QFileDialog.ShowDirsOnly
    )
    loger.info(f"Ordner wurde ausgewählt {folder}")
    return folder if folder else None

def show_images_from_folder_in_qlistwidget(folder_path, list_widget):
    """Zeigt Bilder mit Fortschrittsanzeige an"""
    if not folder_path:
        return
    
    list_widget.ordner_list_bilder.clear()
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    folder = Path(folder_path)
    
    # Alle Bilddateien sammeln
    image_files = [f for f in folder.iterdir() 
                   if f.is_file() and f.suffix.lower() in image_extensions]
    print(image_files)
    # Fortschritt in der Konsole (optional)
    loger.info(f"Lade {len(image_files)} Bilder...")

        # ProgressBar konfigurieren
    list_widget.ordner_loading_progressbar.setMaximum(len(image_files))
    list_widget.ordner_loading_progressbar.setMinimum(0)
    list_widget.ordner_loading_progressbar.setValue(0)
    list_widget.ordner_loading_progressbar.setVisible(True)
    
    # Optional: Text-Format für Prozentanzeige
    list_widget.ordner_loading_progressbar.setFormat("%p% - %v von %m Bildern")
    for i, file_path in enumerate(image_files):
        pixmap = QPixmap(str(file_path))
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            item = QListWidgetItem()
            item.setIcon(QIcon(scaled_pixmap))
            item.setText(file_path.name)
            list_widget.ordner_list_bilder.addItem(item)
            
            # Ermöglicht UI-Updates während des Ladens
            QApplication.processEvents()
        
        # Fortschritt aktualisieren
        progress_value = i + 1
        list_widget.ordner_loading_progressbar.setValue(progress_value)

    # Nach dem Laden: Text ändern
    list_widget.ordner_loading_progressbar.setFormat("Fertig! %v Bilder geladen")