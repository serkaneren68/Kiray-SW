import cv2
import numpy as np
from ultralytics import YOLO
from config.constants import COLOR_RANGES, MIN_AREA_THRESHOLD
from detection.color_detector import ColorDetector
from detection.shape_detector import ShapeDetector
from detection.tracker import ObjectTracker


class ObjectDetector:
    def __init__(self, model_path="sonuncu.engine"):
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

    def detect_and_track_target(self, frame, mode, locked_box):
        """Kilitlenmiş hedefi takip et, başka hedeflere geçme"""
        if not self.model:
            return frame, None, []
        
        ann = frame.copy()
        current_target_box = None
        all_boxes = []
        
        try:
            results = self.model(frame, imgsz=640)[0]
            
            if len(results.boxes) == 0:
                return ann, None, []
            
            # Tüm balonları bul
            all_detections = []
            for i in range(len(results.boxes)):
                box = results.boxes.xyxy[i].cpu().numpy()
                cls = int(results.boxes.cls[i].cpu().numpy())
                conf = float(results.boxes.conf[i].cpu().numpy())
                
                if results.names[cls] != "balloon":
                    continue
                
                x1, y1, x2, y2 = map(int, box)
                all_detections.append([x1, y1, x2, y2, conf])
                all_boxes.append([x1, y1, x2, y2])
            
            if not all_detections:
                return ann, None, []
            
            # Kilitli hedefin mevcut pozisyonunu bul
            # IoU (Intersection over Union) kullanarak eşleştir
            best_iou = 0
            best_match = None
            
            locked_x1, locked_y1, locked_x2, locked_y2 = locked_box
            locked_center_x = (locked_x1 + locked_x2) / 2
            locked_center_y = (locked_y1 + locked_y2) / 2
            
            for det in all_detections:
                x1, y1, x2, y2, conf = det
                
                # IoU hesapla
                iou = self.calculate_iou(locked_box, [x1, y1, x2, y2])
                
                # Ayrıca merkez noktası mesafesini kontrol et
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                distance = np.sqrt((center_x - locked_center_x)**2 + 
                                (center_y - locked_center_y)**2)
                
                # IoU > 0.3 veya merkez mesafesi < 100 piksel ise aynı hedef
                if iou > 0.3 or (iou > 0.1 and distance < 100):
                    if iou > best_iou:
                        best_iou = iou
                        best_match = det
            
            if best_match is not None:
                # Kilitli hedef bulundu
                x1, y1, x2, y2, conf = best_match
                current_target_box = [x1, y1, x2, y2]
                
                # Kilitli hedefi çiz - KIRMIZI
                cv2.rectangle(ann, (x1, y1), (x2, y2), (0, 0, 255), 3)
                cv2.putText(ann, f"KiLiTLi {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                
                # Merkez noktası
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                cv2.circle(ann, (center_x, center_y), 5, (0, 0, 255), -1)
                
                # Crosshair'e olan çizgi
                h, w = frame.shape[:2]
                cv2.line(ann, (center_x, center_y), (w//2, h//2), 
                        (0, 255, 255), 2)
                
                # IoU değerini göster
                cv2.putText(ann, f"IoU: {best_iou:.2f}", 
                        (x1, y2 + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                
                # Diğer balonları GRİ ile göster (hedef değil)
                for det in all_detections:
                    if det is not best_match:
                        dx1, dy1, dx2, dy2, dconf = det
                        cv2.rectangle(ann, (dx1, dy1), (dx2, dy2), (128, 128, 128), 1)
                        cv2.putText(ann, "DiGER", (dx1, dy1 - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (128, 128, 128), 1)
            
            return ann, current_target_box, all_boxes
            
        except Exception as e:
            print(f"Hedef takip hatası: {e}")
            return ann, None, []

    def calculate_iou(self, box1, box2):
        """İki kutunun IoU (Intersection over Union) değerini hesapla"""
        x1_1, y1_1, x2_1, y2_1 = box1
        x1_2, y1_2, x2_2, y2_2 = box2
        
        # Kesişim alanı
        xi1 = max(x1_1, x1_2)
        yi1 = max(y1_1, y1_2)
        xi2 = min(x2_1, x2_2)
        yi2 = min(y2_1, y2_2)
        
        if xi2 < xi1 or yi2 < yi1:
            return 0.0
        
        intersection = (xi2 - xi1) * (yi2 - yi1)
        
        # Birleşim alanı
        box1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
        box2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = box1_area + box2_area - intersection
        
        return intersection / union if union > 0 else 0