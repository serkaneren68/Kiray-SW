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
    'up': b'U',
    'down': b'D',
    'left': b'L',
    'right': b'R',
    'shot': b'S',
    'stop': b'X'
}

# GUI ayarları
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 480
# Kamera ayarları
CAMERA_WIDTH = 800
CAMERA_HEIGHT = 480


# Kamera dönüşüm ayarları
CAMERA_ROTATE_90 = False  # 90 derece saat yönünde döndür
CAMERA_FLIP_HORIZONTAL = False  # Yatay aynala
CAMERA_FLIP_VERTICAL = False  # Dikey aynala


# Takip ayarları
CENTER_TOLERANCE = 100    # Merkez toleransı (piksel)
COMMAND_DELAY = 0.1       # Komutlar arası gecikme (saniye)
PIXEL_THRESHOLD = 20      # Hareket eşiği (piksel) - Mod 1 için
MIN_AREA_THRESHOLD = 1500 # Minimum alan eşiği

# Mod 1 için özel ayarlar
MOD1_PIXEL_THRESHOLD = 20    # Hareket için minimum hata
MOD1_COMMAND_DELAY = 0.1     # Komutlar arası minimum süre
MOD1_STEP_SIZE = 20         # Her harekette kaç adım

# Kamera FOV (Field of View) açıları - Kameranıza göre ayarlayın
CAMERA_FOV_HORIZONTAL = 60  # Yatay görüş açısı (derece)
CAMERA_FOV_VERTICAL = 45    # Dikey görüş açısı (derece)

# Motor kalibrasyonu
MOTOR_CALIBRATION_X = 0.05   # X ekseni kalibrasyon çarpanı
MOTOR_CALIBRATION_Y = 0.05   # Y ekseni kalibrasyon çarpanı