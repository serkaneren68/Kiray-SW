"""
ByteTrack entegrasyonu için wrapper sınıf
"""
import numpy as np
from collections import defaultdict
import sys

# ByteTrack import
try:
    from yolox.tracker.byte_tracker import BYTETracker, STrack
    from yolox.tracker.basetrack import BaseTrack
except ImportError:
    print("ByteTrack import edilemedi. Alternatif yöntem deneniyor...")
    try:
        sys.path.append('ByteTrack')
        from tracker.byte_tracker import BYTETracker, STrack
        from tracker.basetrack import BaseTrack
    except:
        print("ByteTrack bulunamadı. Lütfen kurulumu kontrol edin.")
        raise

# ByteTracker için args sınıfı
class TrackerArgs:
    def __init__(self):
        # Tracking parametreleri
        self.track_thresh = 0.5
        self.track_buffer = 30
        self.match_thresh = 0.8
        self.mot20 = False  # MOT20 test set için
        self.min_box_area = 10
        self.fuse_score = True
        
class ByteTrackerWrapper:
    def __init__(self, track_thresh=0.5, track_buffer=30, match_thresh=0.8):
        """
        ByteTracker başlatıcı
        
        Args:
            track_thresh: Takip eşiği
            track_buffer: Track buffer boyutu
            match_thresh: Eşleştirme eşiği
        """
        # Args nesnesini oluştur
        self.args = TrackerArgs()
        self.args.track_thresh = track_thresh
        self.args.track_buffer = track_buffer
        self.args.match_thresh = match_thresh
        
        # ByteTracker'ı başlat
        self.tracker = BYTETracker(self.args, frame_rate=30)
        self.tracks = {}
        self.frame_id = 0
        
    def update(self, detections, frame_shape):
        """
        Detections: List of dictionaries with 'bbox' and 'confidence'
        Returns: List of tracks with IDs
        """
        self.frame_id += 1
        
        if not detections:
            # Boş detection durumunda da tracker'ı güncelle
            online_targets = self.tracker.update(np.empty((0, 5)), frame_shape, frame_shape)
            return []
            
        # ByteTrack formatına dönüştür
        dets = []
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            score = det['confidence']
            # ByteTrack formatı: [x1, y1, x2, y2, score]
            dets.append([x1, y1, x2, y2, score])
            
        dets = np.array(dets)
        
        # Frame shape'i tuple olarak ver
        img_info = frame_shape[0:2]  # (height, width)
        img_size = frame_shape[0:2]
        
        # ByteTracker'ı güncelle
        online_targets = self.tracker.update(dets, img_info, img_size)
        
        # Sonuçları hazırla
        tracked_objects = []
        for track in online_targets:
            if track.is_activated:
                tlbr = track.tlbr
                tracked_objects.append({
                    'id': track.track_id,
                    'bbox': tlbr.astype(int).tolist(),  # [x1, y1, x2, y2]
                    'score': track.score,
                    'state': 'tracked',
                    'age': self.frame_id - track.start_frame,
                    'velocity': self._calculate_velocity(track)
                })
                
        return tracked_objects
        
    def _calculate_velocity(self, track):
        """Hedefin hızını hesapla"""
        if hasattr(track, 'mean') and len(track.mean) >= 4:
            # Kalman state'inden hız bilgisi al
            vx = track.mean[2]
            vy = track.mean[3]
            speed = np.sqrt(vx**2 + vy**2)
            return {'vx': vx, 'vy': vy, 'speed': speed}
        return {'vx': 0, 'vy': 0, 'speed': 0}