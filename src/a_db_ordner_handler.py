from peewee import *
from src.custom_logging import setup_logger
import numpy as np
import json

loger = setup_logger(__name__)

class Bilder_daten_Handler:
    def __init__(self, db_path):
        self.db = SqliteDatabase(db_path)
        
        # Modell definieren (AUSSERHALB des __init__ wäre besser)
        class Bilder_daten(Model):
            class Meta:
                database = self.db
            
            id = AutoField()  # Primärschlüssel automatisch
            name = CharField(unique=True)  # Bildpfad als eindeutiger Name
            embedding = BlobField(null=True)  # Binary für numpy array
            bbox = TextField(null=True)      # Als JSON String speichern
            alter = IntegerField(null=True)
            geschlecht = IntegerField(null=True)
        
        self.db.connect()
        self.db.create_tables([Bilder_daten])
        self.Bilder_daten = Bilder_daten
    
    # NEUEN EINTRAG ERSTELLEN (für jedes Bild einzeln)
    def add_or_update_bild(self, name, embedding=None, bbox=None, alter=None, geschlecht=None):
        """Fügt neuen Bild-Eintrag hinzu oder aktualisiert existierenden"""
        try:
            # Prüfen ob Bild bereits existiert
            bild, created = self.Bilder_daten.get_or_create(
                name=name,
                defaults={
                    'embedding': embedding,
                    'bbox': bbox,
                    'alter': alter,
                    'geschlecht': geschlecht
                }
            )
            
            # Wenn nicht neu, updaten
            if not created:
                bild.embedding = embedding
                bild.bbox = bbox
                bild.alter = alter
                bild.geschlecht = geschlecht
                bild.save()
            
            loger.info(f"{'Neu' if created else 'Aktualisiert'}: {name}")
            return bild
            
        except Exception as e:
            loger.error(f"Fehler beim Speichern von {name}: {e}")
            return None
    
    # EMBEDDING SPEICHERN (numpy array zu Blob)
    def save_embedding(self, name, embedding_array):
        """Speichert numpy array als Blob"""
        # numpy array zu bytes konvertieren
        embedding_bytes = embedding_array.tobytes()
        
        bild, _ = self.Bilder_daten.get_or_create(name=name)
        bild.embedding = embedding_bytes
        bild.save()
    
    # EMBEDDING LADEN (Blob zu numpy array)
    def load_embedding(self, name):
        """Lädt numpy array aus Blob"""
        try:
            bild = self.Bilder_daten.get(self.Bilder_daten.name == name)
            if bild.embedding:
                # bytes zurück zu numpy array (Shape muss bekannt sein!)
                return np.frombuffer(bild.embedding, dtype=np.float64)
            return None
        except DoesNotExist:
            loger.error(f"Bild nicht gefunden: {name}")
            return None
    
    # BBOX SPEICHERN (als JSON String)
    def save_bbox(self, name, bbox_tuple):
        """bbox_tuple = (x1, y1, x2, y2)"""
        bbox_json = json.dumps(bbox_tuple)
        
        bild, _ = self.Bilder_daten.get_or_create(name=name)
        bild.bbox = bbox_json
        bild.save()
    
    # BBOX LADEN
    def load_bbox(self, name):
        """Lädt bbox als Tuple"""
        try:
            bild = self.Bilder_daten.get(self.Bilder_daten.name == name)
            if bild.bbox:
                return tuple(json.loads(bild.bbox))
            return None
        except DoesNotExist:
            return None
    
    # ALTER SPEICHERN
    def save_alter(self, name, alter):
        bild, _ = self.Bilder_daten.get_or_create(name=name)
        bild.alter = alter
        bild.save()
    
    # GESCHLECHT SPEICHERN
    def save_geschlecht(self, name, geschlecht):  # 0=weiblich, 1=männlich
        bild, _ = self.Bilder_daten.get_or_create(name=name)
        bild.geschlecht = geschlecht
        bild.save()
    
    # ALLE DATEN EINES BILDES LADEN
    def get_bild(self, name):
        """Kompletten Eintrag eines Bildes laden"""
        try:
            return self.Bilder_daten.get(self.Bilder_daten.name == name)
        except DoesNotExist:
            loger.warning(f"Bild nicht gefunden: {name}")
            return None
    
    # ALLE BILDER LADEN
    def get_all_bilder(self):
        """Alle Bild-Einträge laden"""
        return list(self.Bilder_daten.select())
    
    # BILD LÖSCHEN
    def delete_bild(self, name):
        try:
            bild = self.Bilder_daten.get(self.Bilder_daten.name == name)
            bild.delete_instance()
            loger.info(f"Gelöscht: {name}")
            return True
        except DoesNotExist:
            return False
    
    def close(self):
        self.db.close()