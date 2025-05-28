"""
Renk tespit modülü
"""
import cv2
import numpy as np
import config

class ColorDetector:
    def __init__(self):
        self.color_ranges = config.COLOR_RANGES
        self.min_pixels = config.MIN_COLOR_PIXELS
        
    def detect_color(self, roi):
        """ROI içindeki baskın rengi tespit et"""
        if roi.size == 0:
            return None
            
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        counts = {}
        
        for color_name, ranges in self.color_ranges.items():
            mask = None
            for lower, upper in ranges:
                m = cv2.inRange(hsv, lower, upper)
                mask = m if mask is None else cv2.bitwise_or(mask, m)
            
            pixel_count = cv2.countNonZero(mask)
            counts[color_name] = pixel_count
        
        # En çok piksele sahip rengi bul
        dominant_color = max(counts, key=counts.get)
        
        # Minimum piksel kontrolü
        if counts[dominant_color] > self.min_pixels:
            return dominant_color
        else:
            return None
            
    def classify_iff(self, color):
        """Renk bazında dost/düşman sınıflandırması"""
        if color:
            color_upper = color.upper()
            if color_upper == "MAVI":
                return "dost"
            elif color_upper == "KIRMIZI":
                return "dusman"
        return "BİLİNMİYOR"