"""
Mod 1: Basit balon tespiti
"""
from .base_mode import BaseMode

class Mode1(BaseMode):
    def process(self, frame):
        """Basit balon tespiti yap"""
        # YOLO ile tespit
        detections = self.app.yolo_detector.detect(frame)
        
        # Tespitleri çiz
        frame = self.app.yolo_detector.draw_detections(frame, detections)
        
        # Crosshair ekle
        return self.add_crosshair(frame)