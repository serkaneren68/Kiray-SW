"""
Şekil tespit modülü
"""
import cv2
import numpy as np
import math
import config

class ShapeDetector:
    def __init__(self):
        self.min_area = config.MIN_CONTOUR_AREA
        
    def detect_shape(self, mask):
        """Mask üzerinden şekil tespiti yap"""
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
            
        # En büyük konturu bul
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        if area < self.min_area:
            return None
            
        # Şekil analizi
        perimeter = cv2.arcLength(largest_contour, True)
        if perimeter == 0:
            return None
            
        approx = cv2.approxPolyDP(largest_contour, 0.02 * perimeter, True)
        circularity = 4 * math.pi * (area / (perimeter * perimeter))
        
        # Şekil sınıflandırması
        if circularity >= 0.80:
            return "Daire"
        elif len(approx) == 3:
            return "ucgen"
        elif len(approx) == 4:
            return "Kare"
        else:
            return None
            
    def detect_color_shape(self, frame):
        """Frame'de renk ve şekil tespiti yap"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        best_result = None
        best_area = 0
        best_contour = None
        
        for color_name, ranges in config.COLOR_RANGES.items():
            # Renk maskesi oluştur
            mask = None
            for lower, upper in ranges:
                m = cv2.inRange(hsv, lower, upper)
                mask = m if mask is None else cv2.bitwise_or(mask, m)
            
            # Morfolojik işlemler
            kernel = np.ones((5,5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Şekil tespiti
            shape = self.detect_shape(mask)
            if not shape:
                continue
                
            # En büyük konturu bul
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                area = cv2.contourArea(contour)
                if area >= self.min_area and area > best_area:
                    best_area = area
                    best_result = (color_name, shape)
                    best_contour = contour
        
        # Sonucu çiz ve döndür
        if best_contour is not None:
            x, y, w, h = cv2.boundingRect(best_contour)
            label = f"{best_result[0]} {best_result[1]}"
            cv2.drawContours(frame, [best_contour], -1, (0, 255, 0), 2)
            cv2.putText(frame, label, (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            return frame, best_result
            
        return frame, (None, None)