"""
Track yönetimi ve analiz
"""
import numpy as np
from collections import deque
from datetime import datetime
import math

class Track:
    """Tek bir hedefin track bilgisi"""
    def __init__(self, track_id):
        self.id = track_id
        self.positions = deque(maxlen=30)  # Son 30 pozisyon
        self.timestamps = deque(maxlen=30)
        self.color = None
        self.iff_status = "UNKNOWN"
        self.threat_level = 0
        self.created_at = datetime.now()
        self.last_seen = datetime.now()
        self.is_engaged = False
        
    def update(self, bbox, timestamp=None):
        """Track bilgilerini güncelle"""
        if timestamp is None:
            timestamp = datetime.now()
            
        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2
        
        self.positions.append((cx, cy))
        self.timestamps.append(timestamp)
        self.last_seen = timestamp
        
    def get_velocity(self):
        """Ortalama hızı hesapla"""
        if len(self.positions) < 2:
            return 0, 0, 0
            
        # Son iki pozisyon arasındaki farkı al
        dx = self.positions[-1][0] - self.positions[-2][0]
        dy = self.positions[-1][1] - self.positions[-2][1]
        dt = (self.timestamps[-1] - self.timestamps[-2]).total_seconds()
        
        if dt > 0:
            vx = dx / dt
            vy = dy / dt
            speed = math.sqrt(vx**2 + vy**2)
            return vx, vy, speed
        return 0, 0, 0
        
    def predict_position(self, seconds_ahead):
        """Gelecekteki pozisyonu tahmin et"""
        vx, vy, _ = self.get_velocity()
        if len(self.positions) > 0:
            current_x, current_y = self.positions[-1]
            pred_x = current_x + vx * seconds_ahead
            pred_y = current_y + vy * seconds_ahead
            return pred_x, pred_y
        return None
        
    def calculate_threat_score(self, center_x, center_y):
        """Tehdit skorunu hesapla"""
        if len(self.positions) == 0:
            return 0
            
        # Merkeze olan mesafe
        cx, cy = self.positions[-1]
        distance = math.sqrt((cx - center_x)**2 + (cy - center_y)**2)
        
        # Hız
        _, _, speed = self.get_velocity()
        
        # Yaklaşıyor mu?
        approaching = False
        if len(self.positions) >= 2:
            old_dist = math.sqrt((self.positions[-2][0] - center_x)**2 + 
                               (self.positions[-2][1] - center_y)**2)
            approaching = distance < old_dist
            
        # Tehdit skoru hesaplama
        threat = 0
        
        # Mesafe faktörü (yakın = daha tehlikeli)
        if distance > 0:
            threat += (1000 / distance) * 0.4
            
        # Hız faktörü
        threat += speed * 0.3
        
        # Yaklaşma faktörü
        if approaching:
            threat += 30
            
        # IFF durumu
        if self.iff_status == "ENEMY":
            threat *= 2
        elif self.iff_status == "FRIEND":
            threat = 0
            
        self.threat_level = min(100, threat)  # 0-100 arası
        return self.threat_level

class TrackManager:
    """Tüm track'leri yöneten sınıf"""
    def __init__(self):
        self.tracks = {}  # track_id -> Track object
        self.frame_center = (640, 360)  # Varsayılan merkez
        
    def update_tracks(self, tracked_objects):
        """ByteTracker'dan gelen track'leri güncelle"""
        current_ids = set()
        
        for obj in tracked_objects:
            track_id = obj['id']
            bbox = obj['bbox']
            current_ids.add(track_id)
            
            # Yeni track mı?
            if track_id not in self.tracks:
                self.tracks[track_id] = Track(track_id)
                
            # Track'i güncelle
            self.tracks[track_id].update(bbox)
            
        # Kayıp track'leri temizle (5 saniye görülmeyenler)
        lost_threshold = datetime.now()
        for track_id in list(self.tracks.keys()):
            if track_id not in current_ids:
                track = self.tracks[track_id]
                if (lost_threshold - track.last_seen).total_seconds() > 5:
                    del self.tracks[track_id]
                    
    def get_prioritized_targets(self):
        """Tehdit seviyesine göre sıralanmış hedefler"""
        targets = []
        for track in self.tracks.values():
            if track.iff_status != "FRIEND" and not track.is_engaged:
                track.calculate_threat_score(*self.frame_center)
                targets.append(track)
                
        # Tehdit seviyesine göre sırala
        return sorted(targets, key=lambda t: t.threat_level, reverse=True)
        
    def set_frame_center(self, width, height):
        """Frame merkezini ayarla"""
        self.frame_center = (width // 2, height // 2)