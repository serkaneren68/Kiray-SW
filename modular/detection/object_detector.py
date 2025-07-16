import cv2
import numpy as np
from ultralytics import YOLO
from config.constants import COLOR_RANGES, MIN_AREA_THRESHOLD
from detection.color_detector import ColorDetector
from detection.shape_detector import ShapeDetector
from detection.tracker import ObjectTracker


class ObjectDetector:
    def __init__(self, model_path="ikinci.engine"):
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
            
            # Hiç tespit yoksa
            if len(results.boxes) == 0:
                return ann, None, []
            
            # Tespitleri topla
            for i in range(len(results.boxes)):
                # Güvenli bir şekilde verileri al
                box = results.boxes.xyxy[i].cpu().numpy()
                cls = int(results.boxes.cls[i].cpu().numpy())
                conf = float(results.boxes.conf[i].cpu().numpy())
                
                if results.names[cls] != "balloon":
                    continue
                
                x1, y1, x2, y2 = map(int, box)
                
                # ByteTracker formatı için detection ekle [x1, y1, x2, y2, score]
                detections.append([float(x1), float(y1), float(x2), float(y2), conf])
            
            # Eğer hiç balon yoksa
            if len(detections) == 0:
                return ann, None, []
            
            # Tracking KAPALI ise sadece normal tespitleri göster
            if not self.enable_tracking:
                for det in detections:
                    x1, y1, x2, y2, conf = det
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    # Renk tespiti (Mod 2 için)
                    roi = frame[y1:y2, x1:x2]
                    text = "balloon"
                    color = (0, 255, 0)  # Yeşil
                    
                    if mode == "Mod 2" and roi.size > 0:
                        clr = self.color_detector.detect_color(roi)
                        if clr:
                            clr_upper = clr.upper()
                            if clr_upper == "MAVI":
                                text = "dost"
                                color = (255, 0, 0)  # Mavi
                            elif clr_upper == "KIRMIZI":
                                text = "dusman"
                                color = (0, 0, 255)  # Kırmızı
                    
                    cv2.rectangle(ann, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(ann, f"{text} {conf:.2f}", (x1, y1 - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # İlk tespitin kutusunu döndür
                if detections:
                    x1, y1, x2, y2, _ = detections[0]
                    return ann, [int(x1), int(y1), int(x2), int(y2)], []
            
            # Tracking AÇIK ise
            else:
                h, w = frame.shape[:2]
                detections_np = np.array(detections)
                
                # Debug print
                print(f"Detections shape: {detections_np.shape}")
                
                tracked_objects = self.tracker.update(detections_np, (h, w))
                
                print(f"Tracked objects: {len(tracked_objects)}")
                
                # Takip edilen nesneleri görselleştir
                for obj in tracked_objects:
                    x1, y1, x2, y2 = obj['bbox']
                    track_id = obj['id']
                    
                    # Renk tespiti
                    roi = frame[y1:y2, x1:x2]
                    text = f"ID:{track_id}"
                    color = (0, 255, 0)  # Yeşil
                    
                    if mode == "Mod 2" and roi.size > 0:
                        clr = self.color_detector.detect_color(roi)
                        if clr:
                            clr_upper = clr.upper()
                            if clr_upper == "MAVI":
                                color = (255, 0, 0)  # Mavi
                                text = f"ID:{track_id} - dost"
                            elif clr_upper == "KIRMIZI":
                                color = (0, 0, 255)  # Kırmızı
                                text = f"ID:{track_id} - dusman"
                            else:
                                text = f"ID:{track_id} - balloon"
                        else:
                            text = f"ID:{track_id} - balloon"
                    else:
                        text = f"ID:{track_id} - balloon"
                    
                    cv2.rectangle(ann, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(ann, text, (x1, y1 - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # En yakın nesneyi döndür (takip için)
                if tracked_objects:
                    return ann, tracked_objects[0]['bbox'], tracked_objects
                else:
                    # Eğer tracker boş dönerse normal tespitleri kullan
                    if detections:
                        x1, y1, x2, y2, _ = detections[0]
                        return ann, [int(x1), int(y1), int(x2), int(y2)], []
                    
        except Exception as e:
            print(f"Model işleme hatası: {e}")
            import traceback
            traceback.print_exc()
            
        return ann, None, []