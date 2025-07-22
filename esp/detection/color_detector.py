import cv2
import numpy as np
from config.constants import COLOR_RANGES


class ColorDetector:
    @staticmethod
    def detect_color(roi):
        if roi.size == 0:
            return None
            
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        counts = {"Kırmızı": 0, "Yeşil": 0, "Mavi": 0}
        
        for renk, araliklar in COLOR_RANGES.items():
            mask = None
            for lo, hi in araliklar:
                m = cv2.inRange(hsv, lo, hi)
                mask = m if mask is None else cv2.bitwise_or(mask, m)
            counts[renk] = cv2.countNonZero(mask)
        
        dominant_color = max(counts, key=counts.get)
        
        if counts[dominant_color] > 20:
            return dominant_color
        else:
            return None