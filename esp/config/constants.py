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
CANVAS_WIDTH = 900
CANVAS_HEIGHT = 490

# Kamera ayarları
CAMERA_WIDTH = 900
CAMERA_HEIGHT = 540

# Step motor konfigürasyonu
STEPS_PER_DEGREE_YAW = 17.78    # 6400 adım / 360 derece
STEPS_PER_DEGREE_PITCH = 17.78  # 6400 adım / 360 derece

# Kamera FOV (Field of View) değerleri
CAMERA_FOV_HORIZONTAL = 60
CAMERA_FOV_VERTICAL = 45

# Takip ayarları - DENGELİ VE HASSAS
TRACKING_DEADZONE = 20      # Merkez için kabul edilebilir hata (piksel)
TRACKING_INTERVAL = 0.08    # 80ms - dengeli güncelleme
MOVEMENT_SCALE = 0.8        # Daha kontrollü hareket

# Dinamik hız ayarları
MAX_STEPS_PER_MOVE = 150    # Maksimum adım
MIN_STEPS_PER_MOVE = 5      # Minimum adım (titreşimi önler)

# Hız profili - mesafeye göre
SPEED_PROFILE = {
    'fast_distance': 200,    # 200 pikselden uzaksa hızlı
    'slow_distance': 50,     # 50 pikselden yakınsa yavaş
    'fast_scale': 1.5,       # Uzak için ölçek
    'slow_scale': 0.3        # Yakın için ölçek
}
# PID kontrol parametreleri (opsiyonel)
PID_KP = 0.55 # Proportional gain
PID_KD = 0.25 # Derivative gain
PID_KI = 0.015 # Integral gain  

# Minimum nesne alanı
MIN_AREA_THRESHOLD = 1500