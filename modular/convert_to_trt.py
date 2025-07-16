# create_engine.py - Bu dosyayı oluşturup çalıştırın
from ultralytics import YOLO

# PT modelinizi yükleyin
model = YOLO("ikinci.pt")

# Engine formatına dönüştürün
model.export(
    format='engine',
    imgsz=640,
    device=0,
    half=True,  # FP16 precision
    workspace=4,  # GB
    verbose=True
)

print("Yeni engine dosyası oluşturuldu!")