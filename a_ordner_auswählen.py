from os import replace
from sre_constants import BIGCHARSET
from PySide6.QtWidgets import QFileDialog,QListWidgetItem,QApplication
from PySide6.QtCore import QSize,Qt
from PySide6.QtGui import QPixmap, QIcon
from pathlib import Path
from peewee import *
from src.custom_logging import setup_logger
from src.g_db_settings_handler import SettingsHandler
from src.a_db_ordner_handler import Bilder_daten_Handler

loger = setup_logger(__name__)




def start_select_folder(parent_widget):
    folder_path = select_folder(parent_widget)
    if folder_path == None:
        return
    db_path = add_db_to_folder(folder_path)

    Settingsdb = SettingsHandler(db_path)
    Settingsdb.folder_path=folder_path
    Settingsdb.db_path=db_path
    parent_widget.selected_folder_path.setText(Settingsdb.folder_path)

    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    folder = Path(folder_path)

    # Alle Bilddateien sammeln
    image_files = [f for f in folder.glob('**/*') 
        if f.is_file() and f.suffix.lower() in image_extensions]
            # ProgressBar konfigurieren
    parent_widget.ordner_loading_names_to_progressbar.setMaximum(len(image_files))
    parent_widget.ordner_loading_names_to_progressbar.setMinimum(0)
    parent_widget.ordner_loading_names_to_progressbar.setValue(0)
    parent_widget.ordner_loading_names_to_progressbar.setVisible(True)
    
    # Optional: Text-Format für Prozentanzeige
    parent_widget.ordner_loading_names_to_progressbar.setFormat("%p% - %v von %m Bildern")
    for i, file_path in enumerate(image_files):
        # Ermöglicht UI-Updates während des Ladens
        QApplication.processEvents()
    
        image_name = str(file_path).replace(folder_path+"/","")
        bilder_db = Bilder_daten_Handler(db_path=db_path)
        bilder_db.add_or_update_bild(name=image_name)
        #add_picture_names_to_db(picture_name=image_name,db_path=db_path)
        # Fortschritt aktualisieren
        progress_value = i + 1
        parent_widget.ordner_loading_names_to_progressbar.setValue(progress_value)


    # Nach dem Laden: Text ändern
    parent_widget.ordner_loading_names_to_progressbar.setFormat("Fertig! %v Bilder geladen")
    
    
    Settingsdb.close()


def select_folder(parent_widget):
    folder = QFileDialog.getExistingDirectory(
        parent_widget, 
        "Ordner auswählen", 
        "",
        QFileDialog.ShowDirsOnly
    )
    if not folder:
        loger.error("Kein Ordner wurde gewählt:")
        return None
    loger.info(f"Der Ordner wurde gewählt: {folder}")
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

    

def start_show_images_from_folder_in_qlistwidget(list_widget):
    folder_path = list_widget.selected_folder_path.text()
    if not folder_path:
        loger.error(f"Kein Ordner Gelden")
        list_widget.bilder_laden_meldung.setVisible(True)
        return
    list_widget.bilder_laden_meldung.setVisible(False)
    db_path = folder_path+"/db.db"
    """Zeigt Bilder mit Fortschrittsanzeige an"""
    if not folder_path:
        loger.error("No Folder Path")
        return
    
    list_widget.ordner_list_bilder.clear()
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    folder = Path(folder_path)
    
    # Alle Bilddateien sammeln
    image_files = [f for f in folder.glob('**/*') 
                   if f.is_file() and f.suffix.lower() in image_extensions]
    #print(image_files)
    # Fortschritt in der Konsole (optional)
    loger.info(f"Lade {len(image_files)} Bilder...")

        # ProgressBar konfigurieren
    list_widget.ordner_loading_pictures_progressbar.setMaximum(len(image_files))
    list_widget.ordner_loading_pictures_progressbar.setMinimum(0)
    list_widget.ordner_loading_pictures_progressbar.setValue(0)
    list_widget.ordner_loading_pictures_progressbar.setVisible(True)
    
    # Optional: Text-Format für Prozentanzeige
    list_widget.ordner_loading_pictures_progressbar.setFormat("%p% - %v von %m Bildern")
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
        list_widget.ordner_loading_pictures_progressbar.setValue(progress_value)


    # Nach dem Laden: Text ändern
    list_widget.ordner_loading_pictures_progressbar.setFormat("Fertig! %v Bilder geladen")