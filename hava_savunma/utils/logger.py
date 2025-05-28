"""
Logging ve hata yönetimi
"""
import logging
import os
from datetime import datetime

class SystemLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # Logger kurulumu
        log_file = os.path.join(
            log_dir, 
            f"hava_savunma_{datetime.now():%Y%m%d_%H%M%S}.log"
        )
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Logger
        self.logger = logging.getLogger('HavaSavunma')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def log_detection(self, detections):
        """Tespit bilgilerini logla"""
        self.logger.info(f"Detected {len(detections)} objects")
        
    def log_tracking(self, tracks):
        """Tracking bilgilerini logla"""
        active_tracks = len([t for t in tracks.values() if t.last_seen])
        self.logger.info(f"Tracking {active_tracks} active targets")
        
    def log_engagement(self, track_id, action):
        """Angajman olaylarını logla"""
        self.logger.warning(f"ENGAGEMENT: Track {track_id} - {action}")
        
    def log_error(self, error, context=""):
        """Hataları logla"""
        self.logger.error(f"{context}: {str(error)}")