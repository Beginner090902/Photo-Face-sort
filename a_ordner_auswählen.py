# ordnerhandler.py (einfache Variante)
from os import replace
from sre_constants import BIGCHARSET
from PySide6.QtWidgets import QFileDialog,QListWidgetItem,QApplication
from PySide6.QtCore import QSize,Qt
from PySide6.QtGui import QPixmap, QIcon
from pathlib import Path
from peewee import *
from src.custom_logging import setup_logger

loger = setup_logger(__name__)




def start_select_folder(parent_widget):
    folder_path = select_folder(parent_widget)
    db_path = add_db_to_folder(folder_path)
    parent_widget.selected_folder_path.setText(folder_path)
    show_images_from_folder_in_qlistwidget(folder_path,parent_widget, db_path)

def select_folder(parent_widget):
    """Einfache Funktion für Ordnerauswahl"""
    folder = QFileDialog.getExistingDirectory(
        parent_widget, 
        "Ordner auswählen", 
        "",
        QFileDialog.ShowDirsOnly
    )
    loger.info(f"Ordner wurde ausgewählt {folder}")

    db_path = f"{folder}/db.db"
    try:
        db = SqliteDatabase(db_path)
        db.connect()
        loger.info(f"DB erstellt oder existiert schon im pfad {db_path}")

    except Exception as e:
        loger.error(f"Fehler bei Datenbankverbindung: {e}")

    return folder if folder else None

def add_db_to_folder(folder_path):
    db_path = f"{folder_path}/db.db"
    try:
        db = SqliteDatabase(db_path)
        db.connect()
        loger.info(f"DB erstellt oder existiert schon im pfad {db_path}")
        db.close()

    except Exception as e:
        loger.error(f"Fehler bei Datenbankverbindung: {e}")

    return db_path

def add_picture_names_to_db(picture_name,db_path):
    db = SqliteDatabase(db_path)

    class BaseModel(Model):
        class Meta:
            database = db

    class Bilder_daten(BaseModel):
        name = CharField(unique=True)

    class Gesicht(BaseModel):
        bild = ForeignKeyField(Bilder_daten, backref='gesichter')
        embedding = BlobField()  # Binary für numpy array
        bbox = CharField()       # Als String speichern "x1,y1,x2,y2"
        alter = IntegerField()
        geschlecht = IntegerField()
    
    # Tabelle erstellen (falls nicht existiert)
    db.connect()
    db.create_tables([Bilder_daten])
    
    # Daten einfügen
    Bilder_daten.get_or_create(
        name=picture_name)

    

def show_images_from_folder_in_qlistwidget(folder_path, list_widget, db_path):
    """Zeigt Bilder mit Fortschrittsanzeige an"""
    if not folder_path:
        return
    
    list_widget.ordner_list_bilder.clear()
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    folder = Path(folder_path)
    
    # Alle Bilddateien sammeln
    image_files = [f for f in folder.iterdir() 
                   if f.is_file() and f.suffix.lower() in image_extensions]
    #print(image_files)
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
        
        image_name = str(file_path).replace(folder_path+"/","")
        add_picture_names_to_db(picture_name=image_name,db_path=db_path)
        # Fortschritt aktualisieren
        progress_value = i + 1
        list_widget.ordner_loading_progressbar.setValue(progress_value)


    # Nach dem Laden: Text ändern
    list_widget.ordner_loading_progressbar.setFormat("Fertig! %v Bilder geladen")