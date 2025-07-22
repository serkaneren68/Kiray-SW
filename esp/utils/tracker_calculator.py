import numpy as np
from config.constants import *

class TrackerCalculator:
    def __init__(self):
        self.camera_width = CAMERA_WIDTH
        self.camera_height = CAMERA_HEIGHT
        
        # Piksel başına derece hesapla
        self.degrees_per_pixel_x = CAMERA_FOV_HORIZONTAL / CAMERA_WIDTH
        self.degrees_per_pixel_y = CAMERA_FOV_VERTICAL / CAMERA_HEIGHT
        
        # Merkez noktası
        self.center_x = CAMERA_WIDTH // 2
        self.center_y = CAMERA_HEIGHT // 2
        
        print(f"Tracker Calculator başlatıldı:")
        print(f"Piksel başına derece - X: {self.degrees_per_pixel_x:.4f}, Y: {self.degrees_per_pixel_y:.4f}")
    
    def calculate_movement(self, bbox):
        """Hedefi merkeze getirmek için gereken hareketi hesapla"""
        if bbox is None or len(bbox) != 4:
            return 0, 0
        
        x1, y1, x2, y2 = bbox
        
        # Nesnenin merkezi
        object_center_x = (x1 + x2) / 2
        object_center_y = (y1 + y2) / 2
        
        # Piksel hatası
        pixel_error_x = object_center_x - self.center_x
        pixel_error_y = object_center_y - self.center_y
        
        # Ölü bölge kontrolü
        if abs(pixel_error_x) < TRACKING_DEADZONE and abs(pixel_error_y) < TRACKING_DEADZONE:
            return 0, 0
        
        # Derece cinsinden hata
        degree_error_x = pixel_error_x * self.degrees_per_pixel_x
        degree_error_y = -pixel_error_y * self.degrees_per_pixel_y  # Y ekseni ters
        
        # Step motor adımlarına çevir
        raw_yaw_steps = degree_error_x * STEPS_PER_DEGREE_YAW
        raw_pitch_steps = degree_error_y * STEPS_PER_DEGREE_PITCH
        
        # Ölçekleme ve sınırlama
        yaw_steps = int(raw_yaw_steps * MOVEMENT_SCALE)
        pitch_steps = int(raw_pitch_steps * MOVEMENT_SCALE)
        
        # Maksimum adım sınırı
        yaw_steps = np.clip(yaw_steps, -MAX_STEPS_PER_MOVE, MAX_STEPS_PER_MOVE)
        pitch_steps = np.clip(pitch_steps, -MAX_STEPS_PER_MOVE, MAX_STEPS_PER_MOVE)
        
        return yaw_steps, pitch_steps