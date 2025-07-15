import cv2
import os
from config.constants import CAMERA_WIDTH, CAMERA_HEIGHT


class CameraManager:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        
        # Ortam değişkenleri (Windows için)
        os.environ["OPENCV_VIDEOIO_PRIORITY_DSHOW"] = "1"
    
    def start_camera(self):
        try:
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                backends = [cv2.CAP_MSMF, cv2.CAP_ANY, 0]
                for backend in backends:
                    self.cap = cv2.VideoCapture(self.camera_index, backend)
                    if self.cap.isOpened():
                        print(f"Kamera {backend} backend'i ile açıldı")
                        break
            
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.camera_index)
                
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            
            # Buffer temizleme
            for _ in range(5):
                self.cap.read()
                
            return self.cap.isOpened()
            
        except Exception as e:
            print(f"Kamera açma hatası: {e}")
            return False
    
    def read_frame(self):
        if self.cap and self.cap.isOpened():
            return self.cap.read()
        return False, None
    
    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()