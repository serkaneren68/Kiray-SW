"""
Kamera ve video işlemleri
"""
import cv2
import config

class VideoHandler:
    def __init__(self):
        self.cap = None
        self.is_initialized = False
        
    def initialize(self):
        """Kamerayı başlat"""
        try:
            self.cap = cv2.VideoCapture(config.CAMERA_INDEX, cv2.CAP_DSHOW)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
            self.is_initialized = True
            print("Kamera başarıyla açıldı")
            return True
        except Exception as e:
            print(f"Kamera açılırken hata: {e}")
            return False
            
    def read(self):
        """Kameradan frame oku"""
        if not self.is_initialized or not self.cap.isOpened():
            return None
            
        ret, frame = self.cap.read()
        if ret:
            return frame
        else:
            print("Frame okunamadı")
            return None
            
    def release(self):
        """Kamerayı kapat"""
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.is_initialized = False
            print("Kamera kapatıldı")