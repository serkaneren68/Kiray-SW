import gc
import time
import psutil
import os
from PIL import Image, ImageTk
import cv2

class ImageManager:
    """Tkinter image memory yönetimi"""
    def __init__(self):
        self.current_image = None
        self.image_history = []
        self.max_history = 2  # Son 2 image'ı tut
        
    def create_display_image(self, cv_frame):
        """CV2 frame'den Tkinter image oluştur"""
        try:
            # Eski image'ı temizle
            if self.current_image:
                del self.current_image
                
            # RGB'ye çevir
            rgb_frame = cv2.cvtColor(cv_frame, cv2.COLOR_BGR2RGB)
            
            # PIL Image oluştur
            pil_image = Image.fromarray(rgb_frame)
            
            # Tkinter PhotoImage oluştur
            self.current_image = ImageTk.PhotoImage(pil_image)
            
            # Geçmişe ekle
            self.image_history.append(self.current_image)
            
            # Fazla image'ları temizle
            if len(self.image_history) > self.max_history:
                old_image = self.image_history.pop(0)
                del old_image
                
            return self.current_image
            
        except Exception as e:
            print(f"Image creation error: {e}")
            return None
            
    def cleanup_all(self):
        """Tüm image'ları temizle"""
        for img in self.image_history:
            try:
                del img
            except:
                pass
        self.image_history.clear()
        
        if self.current_image:
            try:
                del self.current_image
                self.current_image = None
            except:
                pass


class FrameBuffer:
    """CV2 frame buffer yönetimi"""
    def __init__(self, max_frames=3):
        self.frames = []
        self.max_frames = max_frames
        
    def add_frame(self, frame):
        """Frame ekle"""
        # Kopyala (referans yerine)
        frame_copy = frame.copy()
        self.frames.append(frame_copy)
        
        # Fazla frame'leri temizle
        while len(self.frames) > self.max_frames:
            old_frame = self.frames.pop(0)
            del old_frame
            
    def get_latest_frame(self):
        """En son frame'i al"""
        if self.frames:
            return self.frames[-1]
        return None
        
    def cleanup(self):
        """Tüm frame'leri temizle"""
        for frame in self.frames:
            try:
                del frame
            except:
                pass
        self.frames.clear()


class MemoryMonitor:
    """Memory kullanımını izle"""
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_memory = self.get_memory_usage()
        self.peak_memory = self.start_memory
        self.cleanup_counter = 0
        self.cleanup_interval = 100  # Her 100 frame'de cleanup
        
    def get_memory_usage(self):
        """Mevcut memory kullanımı (MB)"""
        return self.process.memory_info().rss / 1024 / 1024
        
    def should_cleanup(self):
        """Cleanup gerekli mi kontrol et"""
        self.cleanup_counter += 1
        current_memory = self.get_memory_usage()
        
        # Peak memory güncelle
        if current_memory > self.peak_memory:
            self.peak_memory = current_memory
            
        # Cleanup koşulları
        memory_increase = current_memory - self.start_memory
        interval_cleanup = self.cleanup_counter >= self.cleanup_interval
        
        if interval_cleanup or memory_increase > 500:  # 500MB artış
            self.cleanup_counter = 0
            return True
            
        return False
        
    def force_cleanup(self):
        """Zorla garbage collection"""
        collected = gc.collect()
        current_memory = self.get_memory_usage()
        print(f"Memory cleanup: {collected} objects collected, Current: {current_memory:.1f}MB")
        return collected
        
    def get_stats(self):
        """Memory istatistikleri"""
        current = self.get_memory_usage()
        return {
            'current_mb': current,
            'peak_mb': self.peak_memory,
            'increase_mb': current - self.start_memory,
            'cleanup_counter': self.cleanup_counter
        }