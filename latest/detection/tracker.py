import numpy as np
import sys
import os

# ByteTrack yolu
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BT_DIR = os.path.join(BASE_DIR, "ByteTrack")
if BT_DIR not in sys.path:
    sys.path.insert(0, BT_DIR)

try:
    from yolox.tracker.byte_tracker import BYTETracker
    BYTETRACK_AVAILABLE = True
    print("ByteTrack başarıyla yüklendi")
except ImportError as e:
    print(f"ByteTrack bulunamadı: {e}")
    BYTETRACK_AVAILABLE = False


class ObjectTracker:
    def __init__(self):
        self.tracker = None
        self.tracked_objects = {}
        
        if BYTETRACK_AVAILABLE:
            # ByteTracker parametreleri
            self.tracker_args = type('Args', (), {
                'track_thresh': 0.5,
                'track_buffer': 30,
                'match_thresh': 0.8,
                'mot20': False,
                'min_box_area': 10,  # Minimum kutu alanı
                'aspect_ratio_thresh': 1.6,  # En-boy oranı eşiği
            })()
            
            try:
                self.tracker = BYTETracker(self.tracker_args, frame_rate=30)
                print("ByteTracker başlatıldı")
            except Exception as e:
                print(f"ByteTracker başlatma hatası: {e}")
                self.tracker = None
    
    def update(self, detections, frame_shape):
        """
        detections: YOLO çıktıları (x1, y1, x2, y2, score formatında)
        frame_shape: (height, width)
        """
        if not BYTETRACK_AVAILABLE or self.tracker is None:
            print("ByteTracker kullanılamıyor")
            return []
        
        if len(detections) == 0:
            return []
        
        try:
            # Debug bilgisi
            print(f"Update - Detections: {len(detections)}, Shape: {detections.shape}")
            
            # frame_shape'i tuple olarak gönder
            height, width = frame_shape
            img_size = (height, width)
            
            # ByteTracker'a gönder - img_info ve img_size parametreleriyle
            # ByteTracker bazı versiyonlarda farklı parametre bekler
            online_targets = self.tracker.update(detections, img_info=img_size, img_size=img_size)
            
            print(f"Online targets: {len(online_targets)}")
            
            tracked_objects = []
            for t in online_targets:
                tlwh = t.tlwh  # top-left-width-height
                tid = t.track_id
                score = t.score
                
                # xyxy formatına dönüştür
                x1, y1, w, h = tlwh
                x2 = x1 + w
                y2 = y1 + h
                
                # Geçerli koordinatları kontrol et
                if x1 >= 0 and y1 >= 0 and x2 > x1 and y2 > y1:
                    tracked_objects.append({
                        'id': int(tid),
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'score': float(score)
                    })
            
            return tracked_objects
            
        except Exception as e:
            print(f"Tracker update hatası: {e}")
            
            # Alternatif çağrı yöntemi dene
            try:
                # Sadece img_size ile dene
                height, width = frame_shape
                online_targets = self.tracker.update(detections, (height, width))
                
                tracked_objects = []
                for t in online_targets:
                    tlwh = t.tlwh
                    tid = t.track_id
                    score = t.score
                    
                    x1, y1, w, h = tlwh
                    x2 = x1 + w
                    y2 = y1 + h
                    
                    if x1 >= 0 and y1 >= 0 and x2 > x1 and y2 > y1:
                        tracked_objects.append({
                            'id': int(tid),
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'score': float(score)
                        })
                
                return tracked_objects
                
            except Exception as e2:
                print(f"Alternatif tracker update da başarısız: {e2}")
                
                # En son çare: Basit takip mantığı
                return self.simple_tracking(detections)
    
    def simple_tracking(self, detections):
        """ByteTracker çalışmazsa basit bir takip mantığı"""
        tracked_objects = []
        for i, det in enumerate(detections):
            x1, y1, x2, y2, score = det
            tracked_objects.append({
                'id': i,  # Basit ID ataması
                'bbox': [int(x1), int(y1), int(x2), int(y2)],
                'score': float(score)
            })
        return tracked_objects