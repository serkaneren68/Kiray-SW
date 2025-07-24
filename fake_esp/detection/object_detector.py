import cv2
import numpy as np
from ultralytics import YOLO
from config.constants import COLOR_RANGES, MIN_AREA_THRESHOLD
from detection.color_detector import ColorDetector
from detection.shape_detector import ShapeDetector
from detection.tracker import ObjectTracker


class ObjectDetector:
    def __init__(self, model_path="sonuncu.pt"):
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            print(f"YOLO model yükleme hatası: {e}")
            self.model = None
        
        self.color_detector = ColorDetector()
        self.shape_detector = ShapeDetector()
        self.tracker = ObjectTracker()
        self.enable_tracking = False
    
    def set_tracking(self, enabled):
        self.enable_tracking = enabled
        print(f"Tracking {'enabled' if enabled else 'disabled'}")
    
    def detect_color_shape(self, frame):
        if frame is None or frame.size == 0:
            return frame, (None, None, None)
            
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        best_area = 0
        best_color = None
        best_shape = None
        best_cnt = None

        for renk, araliklar in COLOR_RANGES.items():
            mask_full = None
            for lo, hi in araliklar:
                m = cv2.inRange(hsv, lo, hi)
                mask_full = m if mask_full is None else cv2.bitwise_or(mask_full, m)
            kernel = np.ones((5,5), np.uint8)
            mask_full = cv2.morphologyEx(mask_full, cv2.MORPH_OPEN, kernel)

            shape = self.shape_detector.detect_shape(mask_full)
            if not shape:
                continue

            cnts, _ = cv2.findContours(mask_full, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in cnts:
                area = cv2.contourArea(c)
                if area >= MIN_AREA_THRESHOLD and area > best_area:
                    best_area = area
                    best_color = renk
                    best_shape = shape
                    best_cnt = c

        if best_cnt is not None:
            x, y, w, h = cv2.boundingRect(best_cnt)
            label = f"{best_color} {best_shape}"
            cv2.drawContours(frame, [best_cnt], -1, (0,255,0), 2)
            cv2.putText(frame, label, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
            return frame, (best_color, best_shape, (x, y, w, h))

        return frame, (None, None, None)
    
    def detect_objects(self, frame, mode):
        if not self.model:
            return frame, None, []
        
        ann = frame.copy()
        detections = []
        tracked_objects = []
        
        try:
            results = self.model(frame, imgsz=640)[0]
            
            if len(results.boxes) == 0:
                return ann, None, []
            
            # Tespitleri topla
            for i in range(len(results.boxes)):
                box = results.boxes.xyxy[i].cpu().numpy()
                cls = int(results.boxes.cls[i].cpu().numpy())
                conf = float(results.boxes.conf[i].cpu().numpy())
                
                if results.names[cls] != "balloon":
                    continue
                
                x1, y1, x2, y2 = map(int, box)
                
                # MOD 1 - TÜM BALONLARI GÖSTER
                if mode == "Mod 1":
                    detections.append([float(x1), float(y1), float(x2), float(y2), conf])
                    
                    # BOUNDING BOX'I HER ZAMAN ÇİZ
                    cv2.rectangle(ann, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(ann, f"balloon {conf:.2f}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # MOD 2 - RENK TESPİTİ
                elif mode == "Mod 2":
                    roi = frame[y1:y2, x1:x2]
                    if roi.size > 0:
                        clr = self.color_detector.detect_color(roi)
                        if clr and clr.upper() == "KIRMIZI":
                            detections.append([float(x1), float(y1), float(x2), float(y2), conf])
                            cv2.rectangle(ann, (x1, y1), (x2, y2), (0, 0, 255), 2)
                            cv2.putText(ann, f"DUSMAN {conf:.2f}", (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                        elif clr and clr.upper() == "MAVI":
                            cv2.rectangle(ann, (x1, y1), (x2, y2), (255, 0, 0), 2)
                            cv2.putText(ann, f"DOST {conf:.2f}", (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                        else:
                            cv2.rectangle(ann, (x1, y1), (x2, y2), (128, 128, 128), 2)
                            cv2.putText(ann, f"? {conf:.2f}", (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (128, 128, 128), 2)
            
            if len(detections) == 0:
                return ann, None, []
            
            # Tracking işlemleri...
            # (geri kalan kod aynı)
            
            # Tracking KAPALI ise
            if not self.enable_tracking:
                if detections:
                    x1, y1, x2, y2, _ = detections[0]
                    return ann, [int(x1), int(y1), int(x2), int(y2)], []
            
            # Tracking AÇIK ise
            else:
                h, w = frame.shape[:2]
                detections_np = np.array(detections)
                
                tracked_objects = self.tracker.update(detections_np, (h, w))
                
                # Takip edilen düşman nesneleri görselleştir
                for obj in tracked_objects:
                    x1, y1, x2, y2 = obj['bbox']
                    track_id = obj['id']
                    
                    cv2.rectangle(ann, (x1, y1), (x2, y2), (0, 0, 255), 3)
                    cv2.putText(ann, f"DUSMAN ID:{track_id}", (x1, y1 - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    
                    # Hedef işareti
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    cv2.drawMarker(ann, (cx, cy), (0, 0, 255), cv2.MARKER_CROSS, 15, 2)
                
                if tracked_objects:
                    return ann, tracked_objects[0]['bbox'], tracked_objects
                        
        except Exception as e:
            print(f"Model işleme hatası: {e}")
            
        return ann, None, []