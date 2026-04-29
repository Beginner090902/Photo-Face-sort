from peewee import SqliteDatabase
import cv2
from insightface.app import FaceAnalysis


db = SqliteDatabase("gesichter.db")

# Modell laden
app = FaceAnalysis(name='antelopev2')
app.prepare(ctx_id=0)  # 0 = GPU, -1 = CPU

def scan_all_imgs()
# Bild laden
img = cv2.imread("test.jpeg")

# Faces erkennen
faces = app.get(img)

for face in faces:
    print("Embedding Länge:", len(face.embedding))
    print("Bounding Box:", face.bbox)

    # Rechteck zeichnen
    x1, y1, x2, y2 = map(int, face.bbox)
    cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)

cv2.imshow("Result", img)
cv2.waitKey(0)