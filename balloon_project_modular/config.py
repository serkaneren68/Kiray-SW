# config.py
import numpy as np

# Renk aralıkları (HSV formatında)
COLOR_RANGES = {
    "Kırmızı": [
        (np.array([0, 100, 100]), np.array([10, 255, 255])),
        (np.array([160, 100, 100]), np.array([179, 255, 255]))
    ],
    "Yeşil": [(np.array([40, 70, 70]), np.array([80, 255, 255]))],
    "Mavi": [(np.array([100, 150, 0]), np.array([140, 255, 255]))]
}

# Renk tonu eşleştirmeleri
HUE_MAPPING = {
    (0, 10): "Kırmızı",
    (11, 25): "Turuncu",
    (26, 35): "Sarı",
    (36, 85): "Yeşil",
    (86, 125): "Mavi",
    (126, 159): "Mor"
}

# Şekil tespiti parametreleri
SHAPE_PARAMS = {
    "min_area": 1500,          # Minimum kontur alanı
    "min_circularity": 0.3,    # Minimum dairesellik değeri
    "epsilon_factor": 0.04     # Kontur yaklaşım faktörü
}

# OCR ve Genel Ayarlar
GENERAL_SETTINGS = {
    "allowed_letters": ['A', 'B'],  # İzin verilen harfler
    "frame_skip": 2,                # Çerçeve atlama sayısı
    "warning_thickness": 50         # Uyarı çerçeve kalınlığı
}

# Renk Sınıflandırma Eşikleri
COLOR_THRESHOLDS = {
    "white_sat": 50,        # Beyaz için maks doygunluk
    "white_val": 180,        # Beyaz için minimum parlaklık
    "black_val": 50,         # Siyah için maks parlaklık
    "gray_sat": 50           # Gri için maks doygunluk
}