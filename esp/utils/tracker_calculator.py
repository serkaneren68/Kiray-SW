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
        
        # İLK TAKİP KONTROLÜ İÇİN
        self.first_tracking = True
        self.tracking_frames = 0
        
        # INTEGRAL SINIRI (Anti-windup)
        self.integral_limit = 500  # Piksel * frame
        
        print(f"Tracker Calculator başlatıldı:")
        print(f"Piksel başına derece - X: {self.degrees_per_pixel_x:.4f}, Y: {self.degrees_per_pixel_y:.4f}")
    
    def reset(self):
        """PID değerlerini sıfırla"""
        self.last_error_x = 0
        self.last_error_y = 0
        self.integral_x = 0
        self.integral_y = 0
        self.first_tracking = True
        self.tracking_frames = 0
        print("Tracker PID değerleri sıfırlandı")
    
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
            # Merkezdeyken integral değerlerini azalt
            self.integral_x *= 0.9
            self.integral_y *= 0.9
            return 0, 0
        
        # İLK TAKİP YUMUŞAK BAŞLANGIÇ
        if self.first_tracking:
            self.last_error_x = pixel_error_x  # İlk frame'de derivative sıfır olsun
            self.last_error_y = pixel_error_y
            self.integral_x = 0  # İntegral sıfırdan başlasın
            self.integral_y = 0
            self.first_tracking = False
        
        self.tracking_frames += 1
        
        # İlk 10 frame için yumuşak başlangıç
        startup_factor = min(1.0, self.tracking_frames / 10.0)
        
        # PID KONTROL
        # Proportional
        p_x = PID_KP * pixel_error_x
        p_y = PID_KP * pixel_error_y
        
        # Integral (sınırlı)
        self.integral_x += pixel_error_x
        self.integral_y += pixel_error_y
        
        # Integral anti-windup
        self.integral_x = np.clip(self.integral_x, -self.integral_limit, self.integral_limit)
        self.integral_y = np.clip(self.integral_y, -self.integral_limit, self.integral_limit)
        
        i_x = PID_KI * self.integral_x
        i_y = PID_KI * self.integral_y
        
        # Derivative
        d_x = PID_KD * (pixel_error_x - self.last_error_x)
        d_y = PID_KD * (pixel_error_y - self.last_error_y)
        
        self.last_error_x = pixel_error_x
        self.last_error_y = pixel_error_y
        
        # PID çıktısı (piksel cinsinden)
        pid_output_x = (p_x + i_x + d_x) * startup_factor
        pid_output_y = (p_y + i_y + d_y) * startup_factor
        
        # Derece cinsinden hata
        degree_error_x = pid_output_x * self.degrees_per_pixel_x
        degree_error_y = -pid_output_y * self.degrees_per_pixel_y
        
        # Step motor adımlarına çevir VE MOVEMENT_SCALE UYGULA
        raw_yaw_steps = degree_error_x * STEPS_PER_DEGREE_YAW * MOVEMENT_SCALE
        raw_pitch_steps = degree_error_y * STEPS_PER_DEGREE_PITCH * MOVEMENT_SCALE
        
        # Direkt adım sayısı
        yaw_steps = int(raw_yaw_steps)
        pitch_steps = int(raw_pitch_steps)
        
        # İlk frame'lerde maksimum hareketi daha da sınırla
        if self.tracking_frames < 5:
            max_first_steps = 50
            yaw_steps = np.clip(yaw_steps, -max_first_steps, max_first_steps)
            pitch_steps = np.clip(pitch_steps, -max_first_steps, max_first_steps)
        else:
            # Normal maksimum adım sınırı
            yaw_steps = np.clip(yaw_steps, -MAX_STEPS_PER_MOVE, MAX_STEPS_PER_MOVE)
            pitch_steps = np.clip(pitch_steps, -MAX_STEPS_PER_MOVE, MAX_STEPS_PER_MOVE)
        
        # Minimum hareket eşiği
        if abs(yaw_steps) < MIN_STEPS_PER_MOVE:
            yaw_steps = 0
        if abs(pitch_steps) < MIN_STEPS_PER_MOVE:
            pitch_steps = 0
        
        # Debug
        if self.tracking_frames % 10 == 0:  # Her 10 frame'de bir
            print(f"[TRACKER] Frame: {self.tracking_frames}, Hata: X={pixel_error_x:.1f}, Y={pixel_error_y:.1f}, Adım: Yaw={yaw_steps}, Pitch={pitch_steps}")
        
        return yaw_steps, pitch_steps