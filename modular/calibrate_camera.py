# calibrate_camera.py
import cv2
import numpy as np
from utils.angle_calculator import AngleCalculator

def calibrate_fov():
    """Kamera FOV kalibrasyonu"""
    cap = cv2.VideoCapture(0)
    
    print("Kalibrasyon:")
    print("1. Bilinen bir mesafede bilinen boyutta nesne koyun")
    print("2. Space tuşuna basın")
    print("3. ESC çıkış")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        # Crosshair
        cv2.line(frame, (center_x - 20, center_y), 
                (center_x + 20, center_y), (0, 255, 0), 2)
        cv2.line(frame, (center_x, center_y - 20), 
                (center_x, center_y + 20), (0, 255, 0), 2)
        
        # Grid çiz
        for i in range(0, w, 100):
            cv2.line(frame, (i, 0), (i, h), (128, 128, 128), 1)
        for i in range(0, h, 100):
            cv2.line(frame, (0, i), (w, i), (128, 128, 128), 1)
        
        cv2.putText(frame, f"Çözünürlük: {w}x{h}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("FOV Kalibrasyon", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == 32:  # Space
            # Test hareketi
            print("\nTest için:")
            print("1. Nesneyi sağa 100 piksel kaydırın")
            print("2. Motoru kaç derece döndürmeniz gerektiğini ölçün")
            print("3. CAMERA_FOV_HORIZONTAL = (derece * genişlik) / 100")
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    calibrate_fov()