import cv2
import math
import numpy as np


class ShapeDetector:
    @staticmethod
    def detect_shape(mask):
        if mask.size == 0:
            return None
            
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not cnts:
            return None
        c = max(cnts, key=cv2.contourArea)
        peri = cv2.arcLength(c, True)
        if peri == 0:
            return None
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        area = cv2.contourArea(c)
        circularity = 4 * math.pi * (area / (peri * peri))

        if circularity >= 0.80:
            return "Daire"
        elif len(approx) == 3:
            return "Üçgen"
        elif len(approx) == 4:
            return "Kare"
        else:
            return None