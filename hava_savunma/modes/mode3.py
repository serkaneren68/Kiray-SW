"""
Mod 3: QR kod ve şekil tespiti ile angajman
"""
from .base_mode import BaseMode
from detection.shape_detector import ShapeDetector
import cv2

class Mode3(BaseMode):
    def __init__(self, app):
        super().__init__(app)
        self.shape_detector = ShapeDetector()
        self.qr_detector = cv2.QRCodeDetector()
        
    def process(self, frame):
        """QR kod ve şekil tespiti yap"""
        if not self.app.awaiting_confirmation:
            # QR kod tespiti
            data, pts, _ = self.qr_detector.detectAndDecode(frame)
            if data in ("A", "B"):
                self.app.detected_letter = data
                self.app.confirmed_letter = data
                self.app.letter_frame.letter_label.config(text=f"Harf: {data}")
                
                        # Renk ve şekil tespiti
            processed_frame, result = self.shape_detector.detect_color_shape(frame)
            color, shape = result
            
            if color and shape:
                self.app.detected_shape = f"{color} {shape}"
                self.app.confirmed_shape = f"{color} {shape}"
                self.app.letter_frame.shape_label.config(text=f"Şekil: {color} {shape}")
                self.app.awaiting_confirmation = True
                
            frame = processed_frame
        else:
            # Onay bekleniyorsa sadece frame'i göster
            pass
            
        # Crosshair ekle
        return self.add_crosshair(frame)