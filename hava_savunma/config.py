"""
Uygulama konfigürasyonları ve sabitler
"""
import numpy as np

# Pencere ayarları
WINDOW_TITLE = "Hava Savunma Kontrol Paneli"
WINDOW_SIZE = "1920x1080"
WINDOW_BG = "black"

# Kamera ayarları
CAMERA_INDEX = 0
CAMERA_WIDTH = 780
CAMERA_HEIGHT = 480

# Model ayarları
MODEL_PATH = "best2.pt"

# Tesseract yolu
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Renk aralıkları (HSV)
COLOR_RANGES = {
    "kirmizi": [
        (np.array([0, 100, 100]), np.array([10, 255, 255])),
        (np.array([160, 100, 100]), np.array([179, 255, 255]))
    ],
    "yesil": [
        (np.array([35, 100, 100]), np.array([85, 255, 255]))
    ],
    "mavi": [
        (np.array([100, 100, 100]), np.array([135, 255, 255]))
    ]
}

# Minimum değerler
MIN_COLOR_PIXELS = 20
MIN_CONTOUR_AREA = 1500

# Crosshair ayarları
CROSSHAIR_SIZE = 20
CROSSHAIR_COLOR = (0, 255, 0)
CROSSHAIR_THICKNESS = 2

