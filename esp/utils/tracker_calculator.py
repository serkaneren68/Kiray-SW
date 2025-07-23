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
        
        # PID kontrolü için
        self.last_error_x = 0
        self.last_error_y = 0
        self.integral_x = 0
        self.integral_y = 0
        
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
        
        # PID KONTROL (daha hassas ve hızlı takip için)
        # Proportional
        p_x = PID_KP * pixel_error_x
        p_y = PID_KP * pixel_error_y
        
        # Integral
        self.integral_x += pixel_error_x
        self.integral_y += pixel_error_y
        i_x = PID_KI * self.integral_x
        i_y = PID_KI * self.integral_y
        
        # Derivative
        d_x = PID_KD * (pixel_error_x - self.last_error_x)
        d_y = PID_KD * (pixel_error_y - self.last_error_y)
        
        self.last_error_x = pixel_error_x
        self.last_error_y = pixel_error_y
        
        # PID çıktısı (piksel cinsinden)
        pid_output_x = p_x + i_x + d_x
        pid_output_y = p_y + i_y + d_y
        
        # Derece cinsinden hata
        degree_error_x = pid_output_x * self.degrees_per_pixel_x
        degree_error_y = -pid_output_y * self.degrees_per_pixel_y
        
        # Step motor adımlarına çevir
        raw_yaw_steps = degree_error_x * STEPS_PER_DEGREE_YAW
        raw_pitch_steps = degree_error_y * STEPS_PER_DEGREE_PITCH
        
        # Direkt adım sayısı (MOVEMENT_SCALE zaten uygulandı)
        yaw_steps = int(raw_yaw_steps)
        pitch_steps = int(raw_pitch_steps)
        
        # Maksimum adım sınırı
        yaw_steps = np.clip(yaw_steps, -MAX_STEPS_PER_MOVE, MAX_STEPS_PER_MOVE)
        pitch_steps = np.clip(pitch_steps, -MAX_STEPS_PER_MOVE, MAX_STEPS_PER_MOVE)
        
        # Minimum hareket eşiği (çok küçük hareketleri engelle)
        if abs(yaw_steps) < 5:
            yaw_steps = 0
        if abs(pitch_steps) < 5:
            pitch_steps = 0
        
        return yaw_steps, pitch_steps