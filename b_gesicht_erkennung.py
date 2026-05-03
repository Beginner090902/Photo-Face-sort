from peewee import *
import cv2
from insightface.app import FaceAnalysis
from src.a_db_ordner_handler import Bilder_daten_Handler
from src.g_db_settings_handler import SettingsHandler
from src.custom_logging import setup_logger
from PySide6.QtCore import Qt  
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QApplication
import cv2
import os

loger = setup_logger(__name__)

def starte_gesicht_erkennung_alle(ui):
    folder_path = ui.selected_folder_path.text()
    db_path = f"{folder_path}/db.db"

    bilder_db = Bilder_daten_Handler(db_path=db_path)
    settings_db = SettingsHandler(db_path=db_path)
    alle_bilder_ojekte = bilder_db.get_all_bilder()

    # ProgressBar konfigurieren
    ui.scan_progressBar.setMaximum(len(alle_bilder_ojekte))
    ui.scan_progressBar.setMinimum(0)
    ui.scan_progressBar.setValue(0)
    ui.scan_progressBar.setVisible(True)
    ui.scan_progressBar.setFormat("%p% - %v von %m Bildern")

    # 1. ORIGINALBILD path
    bild_path = alle_bilder_ojekte[0].name
    voller_pfad = f"{folder_path}/{bild_path}"
    

    pixmap = QPixmap(voller_pfad)
    scalier_und_anzeigen_in_objekt(element=ui.label,pixmap=pixmap)


    # 2. Modell laden für Gesichtserkennung
    app = FaceAnalysis(name='antelopev2')
    if settings_db.mode == "CPU":
        mode = -1
    elif settings_db.mode == "GPU":  # elif statt if
        mode = 0
    else:
        loger.error(f"un plausible einstellung CPU oder GPU modus aus DB: {settings_db.mode}")
        return
    
    app.prepare(ctx_id=mode)

    # 3. Bild mit OpenCV laden und Gesichter erkennen
    img = cv2.imread(voller_pfad)
    faces = app.get(img)

    # 4. Rechtecke auf das Bild zeichnen
    for face in faces:
        print("Embedding Länge:", len(face.embedding))
        print("Bounding Box:", face.bbox)
        
        x1, y1, x2, y2 = map(int, face.bbox)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 8)

    # 5. *** DAS FEHLTE: BILD MIT RECTANGLES IN label_2 ANZEIGEN ***
    # Konvertiere OpenCV-Bild (BGR) zu QPixmap
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, ch = img_rgb.shape
    bytes_per_line = ch * w
    qt_image = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
    modifizierte_pixmap = QPixmap.fromImage(qt_image)
    scalier_und_anzeigen_in_objekt(element=ui.label_2,pixmap=modifizierte_pixmap)

    print(f"Bild mit {len(faces)} Gesichtern in label_2 angezeigt")

def scalier_und_anzeigen_in_objekt(element,pixmap):
    element.setScaledContents(False)
    label_size = element.size()
    scaled_pixmap = pixmap.scaled(
        label_size.width(), 
        label_size.height(),
        Qt.AspectRatioMode.KeepAspectRatio,  # Behält Seitenverhältnis
        Qt.TransformationMode.SmoothTransformation  # Sanfte Skalierung
    )
    element.setPixmap(scaled_pixmap)
    element.setAlignment(Qt.AlignmentFlag.AlignCenter)
    QApplication.processEvents()  # Qt aktualisieren