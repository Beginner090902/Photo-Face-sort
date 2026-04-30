from peewee import *
import cv2
from insightface.app import FaceAnalysis


db = SqliteDatabase("gesichter.db")

# Modell laden
app = FaceAnalysis(name='antelopev2')
app.prepare(ctx_id=0)  # 0 = GPU, -1 = CPU


img = cv2.imread("Bilder/aaa.jpg")

# Faces erkennen
faces = app.get(img)
print("gesichter")
print(faces)

def add_picture_gesichter_to_db(picture_name,db_path):
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
