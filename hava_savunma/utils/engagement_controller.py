"""
Angajman kontrolü ve atış yönetimi
"""
import time
import math
from datetime import datetime

class EngagementController:
    def __init__(self):
        self.engaged_targets = {}  # target_id -> engagement_info
        self.restricted_angle = None
        self.ammo_count = 100
        self.last_shot_time = 0
        self.shot_cooldown = 0.5  # saniye
        
    def can_engage(self, track, frame_center):
        """Hedefin angajman için uygun olup olmadığını kontrol et"""
        # IFF kontrolü
        if track.iff_status == "FRIEND":
            return False, "Dost hedef"
            
        # Mühimmat kontrolü
        if self.ammo_count <= 0:
            return False, "Mühimmat yok"
            
        # Atış hızı kontrolü
        current_time = time.time()
        if current_time - self.last_shot_time < self.shot_cooldown:
            return False, "Bekleme süresi"
            
        # Yasaklı bölge kontrolü
        if self.restricted_angle is not None:
            angle = self.calculate_angle(track, frame_center)
            if self.is_in_restricted_area(angle):
                return False, "Yasaklı bölgede"
                
        return True, "Angajman uygun"
        
    def calculate_angle(self, track, frame_center):
        """Hedefin merkeze göre açısını hesapla"""
        if len(track.positions) > 0:
            cx, cy = track.positions[-1]
            dx = cx - frame_center[0]
            dy = cy - frame_center[1]
            angle = math.degrees(math.atan2(dy, dx))
            return (angle + 360) % 360  # 0-360 arası
        return 0
        
    def is_in_restricted_area(self, angle):
        """Açının yasaklı bölgede olup olmadığını kontrol et"""
        if self.restricted_angle is None:
            return False
            
        # ±30 derece yasaklı bölge
        min_angle = (self.restricted_angle - 30) % 360
        max_angle = (self.restricted_angle + 30) % 360
        
        if min_angle < max_angle:
            return min_angle <= angle <= max_angle
        else:  # 0 dereceden geçiyor
            return angle >= min_angle or angle <= max_angle
            
    def engage_target(self, track_id):
        """Hedefe angajman başlat"""
        if track_id not in self.engaged_targets:
            self.engaged_targets[track_id] = {
                'start_time': datetime.now(),
                'shots_fired': 0,
                'status': 'active'
            }
            
    def fire_at_target(self, track_id):
        """Hedefe ateş et"""
        if self.ammo_count > 0 and track_id in self.engaged_targets:
            self.ammo_count -= 1
            self.last_shot_time = time.time()
            self.engaged_targets[track_id]['shots_fired'] += 1
            return True
        return False
        
    def disengage_target(self, track_id):
        """Hedef angajmanını sonlandır"""
        if track_id in self.engaged_targets:
            self.engaged_targets[track_id]['status'] = 'completed'
            self.engaged_targets[track_id]['end_time'] = datetime.now()