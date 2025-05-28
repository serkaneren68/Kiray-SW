"""
Tüm modların türetileceği optimize edilmiş temel sınıf
"""
from abc import ABC, abstractmethod
import cv2
import config

class BaseMode(ABC):
    def __init__(self, app):
        self.app = app
        self.last_detections = []
        self.last_tracked_objects = []
        
    @abstractmethod
    def process(self, frame):
        """Her mod bu metodu implement etmeli"""
        pass
        
    def process_optimized(self, frame, tracked_objects=None):
        """Optimize edilmiş işleme metodu"""
        if tracked_objects is not None:
            self.last_tracked_objects = tracked_objects
            
        # Mod spesifik işleme
        processed_frame = self.process(frame)
        
        # Her zaman crosshair ekle
        return self.add_crosshair(processed_frame)
        
    def add_crosshair(self, frame):
        """Frame'e crosshair ekle"""
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        # Yatay ve dikey çizgi
        cv2.line(frame, 
                (center_x - config.CROSSHAIR_SIZE, center_y), 
                (center_x + config.CROSSHAIR_SIZE, center_y), 
                config.CROSSHAIR_COLOR, config.CROSSHAIR_THICKNESS)
        cv2.line(frame, 
                (center_x, center_y - config.CROSSHAIR_SIZE), 
                (center_x, center_y + config.CROSSHAIR_SIZE), 
                config.CROSSHAIR_COLOR, config.CROSSHAIR_THICKNESS)
                
                
        return frame
        
    def draw_track_info(self, frame, track, bbox):
        """Track bilgilerini detaylı çiz"""
        x1, y1, x2, y2 = bbox
        
        # IFF durumuna göre renk
        if track.iff_status == "FRIEND":
            color = (0, 255, 0)  # Yeşil
        elif track.iff_status == "ENEMY":
            color = (0, 0, 255)  # Kırmızı  
        else:
            color = (255, 255, 0)  # Sarı
            
        # Ana kutu
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Bilgi paneli arka planı
        info_bg_height = 60
        cv2.rectangle(frame, (x1, y1-info_bg_height), (x2, y1), (0, 0, 0), -1)
        cv2.rectangle(frame, (x1, y1-info_bg_height), (x2, y1), color, 1)
        
        # Bilgiler
        vx, vy, speed = track.get_velocity()
        info_lines = [
            f"ID: {track.id} | {track.iff_status}",
            f"Speed: {speed:.1f} px/s",
            f"Threat: {track.threat_level:.0f}%"
        ]
        
        for i, line in enumerate(info_lines):
            cv2.putText(frame, line, (x1+5, y1-45+i*15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                       
        return frame