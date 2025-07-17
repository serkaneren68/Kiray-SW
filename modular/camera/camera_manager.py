import cv2
import os
from config.constants import CAMERA_WIDTH, CAMERA_HEIGHT


class CameraManager:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None
        self.rotate_90 = False  # 90 derece döndürme
        self.flip_horizontal = False  # Yatay aynalama
        self.flip_vertical = False  # Dikey aynalama
        
        # Ortam değişkenleri (Windows için)
        os.environ["OPENCV_VIDEOIO_PRIORITY_DSHOW"] = "1"
    
    def set_transformations(self, rotate_90=False, flip_horizontal=False, flip_vertical=False):
        """Görüntü dönüşümlerini ayarla"""
        self.rotate_90 = rotate_90
        self.flip_horizontal = flip_horizontal
        self.flip_vertical = flip_vertical
        print(f"Dönüşümler: Döndürme={rotate_90}, Yatay Aynalama={flip_horizontal}, Dikey Aynalama={flip_vertical}")
    
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
            ret, frame = self.cap.read()
            
            if ret and frame is not None:
                # Dönüşümleri uygula
                frame = self.apply_transformations(frame)
                
            return ret, frame
        return False, None
    
    def apply_transformations(self, frame):
        """Görüntüye dönüşümleri uygula"""
        if frame is None:
            return frame
        
        # Önce aynalamaları yap
        if self.flip_horizontal and self.flip_vertical:
            # Her iki aynalama = 180 derece dönme
            frame = cv2.flip(frame, -1)  # -1 = hem yatay hem dikey
        elif self.flip_horizontal:
            frame = cv2.flip(frame, 1)  # 1 = yatay aynalama
        elif self.flip_vertical:
            frame = cv2.flip(frame, 0)  # 0 = dikey aynalama
        
        # Sonra döndür (isteniyorsa)
        if self.rotate_90:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        
        return frame
    
    def get_output_dimensions(self):
        """Dönüşümlerden sonraki boyutları döndür"""
        if self.rotate_90:
            # 90 derece döndürüldüğünde boyutlar yer değiştirir
            return CAMERA_HEIGHT, CAMERA_WIDTH
        else:
            return CAMERA_WIDTH, CAMERA_HEIGHT
    
    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()