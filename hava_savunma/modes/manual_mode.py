"""
Manuel kontrol modu
"""
from .base_mode import BaseMode

class ManualMode(BaseMode):
    def process(self, frame):
        """Manuel modda sadece crosshair ekle"""
        return self.add_crosshair(frame)