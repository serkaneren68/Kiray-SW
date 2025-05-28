"""
Mod 2: Renk bazlı dost/düşman ayrımı
"""
from .base_mode import BaseMode
from detection.color_detector import ColorDetector

class Mode2(BaseMode):
    def __init__(self, app):
        super().__init__(app)
        self.color_detector = ColorDetector()
        
    def process(self, frame):
        """Renk bazlı dost/düşman tespiti yap"""
        # YOLO ile tespit
        detections = self.app.yolo_detector.detect(frame)
        
        # Her tespit için renk analizi
        labels = []
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            roi = frame[y1:y2, x1:x2]
            
            color = self.color_detector.detect_color(roi)
            iff_status = self.color_detector.classify_iff(color)
            labels.append(iff_status)
        
        # Tespitleri çiz
        frame = self.app.yolo_detector.draw_detections(frame, detections, labels)
        
        # Crosshair ekle
        return self.add_crosshair(frame)