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
CANVAS_WIDTH = 780
CANVAS_HEIGHT = 475

# Kamera ayarları
CAMERA_WIDTH = 780
CAMERA_HEIGHT = 480

# Takip ayarları
CENTER_TOLERANCE = 50
COMMAND_DELAY = 0.1
PIXEL_THRESHOLD = 20
MIN_AREA_THRESHOLD = 1500