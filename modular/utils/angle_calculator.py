import numpy as np
from config.constants import (
    CAMERA_WIDTH, CAMERA_HEIGHT,
    CAMERA_FOV_HORIZONTAL, CAMERA_FOV_VERTICAL,
    MOTOR_CALIBRATION_X, MOTOR_CALIBRATION_Y
)


class AngleCalculator:
    """Piksel hatasından motor açısı hesaplama"""
    
    @staticmethod
    def pixel_to_angle(pixel_error_x, pixel_error_y):
        """
        Piksel hatasını açıya dönüştür
        
        Args:
            pixel_error_x: Yatay piksel hatası (pozitif = sağ)
            pixel_error_y: Dikey piksel hatası (pozitif = aşağı)
            
        Returns:
            (angle_x, angle_y): Derece cinsinden açılar
        """
        # Piksel başına düşen açı
        degrees_per_pixel_x = CAMERA_FOV_HORIZONTAL / CAMERA_WIDTH
        degrees_per_pixel_y = CAMERA_FOV_VERTICAL / CAMERA_HEIGHT
        
        # Açı hesaplama
        angle_x = pixel_error_x * degrees_per_pixel_x * MOTOR_CALIBRATION_X
        angle_y = pixel_error_y * degrees_per_pixel_y * MOTOR_CALIBRATION_Y
        
        # Debug bilgisi
        print(f"[AngleCalc] Piksel hatası: X={pixel_error_x}, Y={pixel_error_y}")
        print(f"[AngleCalc] Piksel başına derece: X={degrees_per_pixel_x:.4f}, Y={degrees_per_pixel_y:.4f}")
        print(f"[AngleCalc] Hesaplanan açı: X={angle_x:.2f}°, Y={angle_y:.2f}°")
        
        return angle_x, angle_y
    
    @staticmethod
    def calculate_move_command(pixel_error_x, pixel_error_y, threshold=5):
        """
        Hareket komutunu hesapla - TEK SEFERDE GİDECEK ŞEKİLDE
        """
        angle_x, angle_y = AngleCalculator.pixel_to_angle(pixel_error_x, pixel_error_y)
        
        # Minimum hareket eşiği (derece)
        min_angle = 0.5
        
        # Hangi eksen daha büyük hataya sahip?
        if abs(angle_x) > abs(angle_y):
            # Yatay hareket öncelikli
            if abs(angle_x) >= min_angle:
                if angle_x > 0:
                    return 'R', abs(angle_x)
                else:
                    return 'L', abs(angle_x)
        else:
            # Dikey hareket öncelikli
            if abs(angle_y) >= min_angle:
                if angle_y > 0:
                    return 'D', abs(angle_y)
                else:
                    return 'U', abs(angle_y)
        
        # Hareket gerekmez
        return None, 0