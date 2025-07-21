import numpy as np

# Renk aralıkları tanımı
COLOR_RANGES = {
    "Kırmızı": [
        (np.array([0, 100, 100]), np.array([10, 255, 255])),
        (np.array([160, 100, 100]), np.array([179, 255, 255]))
    ],
    "Yeşil": [
        (np.array([35, 100, 100]), np.array([85, 255, 255]))
    ],
    "Mavi": [
        (np.array([100, 100, 100]), np.array([135, 255, 255]))
    ]
}

# Arduino komutları
ARDUINO_COMMANDS = {
    'up': b'U\n',
    'down': b'D\n',
    'left': b'L\n',
    'right': b'R\n',
    'shot': b'S\n',
    'stop': b'X\n'
}

# GUI ayarları
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 480

# Kamera ayarları
CAMERA_WIDTH = 800
CAMERA_HEIGHT = 480

# Step motor konfigürasyonu - KALİBRE EDİLMİŞ DEĞERLER
STEPS_PER_DEGREE_YAW = 2.22    # 800 adım / 360 derece
STEPS_PER_DEGREE_PITCH = 2.22  # 800 adım / 360 derece

# Kamera FOV (Field of View) değerleri
CAMERA_FOV_HORIZONTAL = 60  # Yatay görüş açısı (derece)
CAMERA_FOV_VERTICAL = 45    # Dikey görüş açısı (derece)

# Takip ayarları
TRACKING_DEADZONE = 15      # Piksel cinsinden ölü bölge
TRACKING_INTERVAL = 0.1     # Takip güncelleme süresi (saniye)
MOVEMENT_SCALE = 0.5        # Hareket ölçekleme faktörü
MAX_STEPS_PER_MOVE = 30     # Tek seferde maksimum adım

# Minimum nesne alanı
MIN_AREA_THRESHOLD = 1500