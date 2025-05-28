"""
Performans izleme ve optimizasyon
"""
import time
import cv2
from collections import deque

class PerformanceMonitor:
    def __init__(self, window_size=30):
        self.frame_times = deque(maxlen=window_size)
        self.detection_times = deque(maxlen=window_size)
        self.tracking_times = deque(maxlen=window_size)
        self.last_time = time.time()
        
    def start_timer(self):
        """Zamanlayıcıyı başlat"""
        return time.time()
        
    def end_timer(self, start_time, timer_type='frame'):
        """Zamanlayıcıyı bitir ve kaydet"""
        elapsed = time.time() - start_time
        
        if timer_type == 'frame':
            self.frame_times.append(elapsed)
        elif timer_type == 'detection':
            self.detection_times.append(elapsed)
        elif timer_type == 'tracking':
            self.tracking_times.append(elapsed)
            
    def get_fps(self):
        """Ortalama FPS hesapla"""
        if len(self.frame_times) > 0:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            return 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        return 0
        
    def get_stats(self):
        """Performans istatistiklerini al"""
        stats = {
            'fps': self.get_fps(),
            'avg_frame_time': sum(self.frame_times) / len(self.frame_times) if self.frame_times else 0,
            'avg_detection_time': sum(self.detection_times) / len(self.detection_times) if self.detection_times else 0,
            'avg_tracking_time': sum(self.tracking_times) / len(self.tracking_times) if self.tracking_times else 0
        }
        return stats
        
    def draw_stats(self, frame):
        """İstatistikleri frame üzerine çiz"""
        stats = self.get_stats()
        y_offset = 20
        
        texts = [
            f"FPS: {stats['fps']:.1f}",
            f"Frame: {stats['avg_frame_time']*1000:.1f}ms",
            f"Detection: {stats['avg_detection_time']*1000:.1f}ms",
            f"Tracking: {stats['avg_tracking_time']*1000:.1f}ms"
        ]
        
        for i, text in enumerate(texts):
            cv2.putText(frame, text, (10, y_offset + i*20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                       
        return frame