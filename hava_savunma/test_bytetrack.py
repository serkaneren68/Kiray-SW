"""
ByteTrack entegrasyonunu test etmek için script
"""
import cv2
import numpy as np
from tracking.byte_tracker import ByteTrackerWrapper
from tracking.track_manager import TrackManager

def create_test_detections(frame_num):
    """Test için sahte detection'lar oluştur"""
    detections = []
    
    # Hareketli hedef 1
    x1 = 100 + frame_num * 5
    y1 = 100
    detections.append({
        'bbox': (x1, y1, x1+50, y1+50),
        'confidence': 0.9
    })
    
    # Hareketli hedef 2 (ters yön)
    x2 = 600 - frame_num * 3
    y2 = 200
    detections.append({
        'bbox': (x2, y2, x2+50, y2+50),
        'confidence': 0.85
    })
    
    return detections

def test_bytetrack():
    """ByteTrack'i test et"""
    # Boş frame oluştur
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Tracker'ları başlat
    tracker = ByteTrackerWrapper()
    track_manager = TrackManager()
    
    # Video writer (opsiyonel)
    out = cv2.VideoWriter('bytetrack_test.mp4', 
                         cv2.VideoWriter_fourcc(*'mp4v'), 
                         30, (640, 480))
    
    for frame_num in range(100):
        # Frame'i temizle
        frame.fill(0)
        
        # Test detection'ları oluştur
        detections = create_test_detections(frame_num)
        
        # ByteTracker'ı güncelle
        tracked_objects = tracker.update(detections, frame.shape[:2])
        
        # Track manager'ı güncelle
        track_manager.update_tracks(tracked_objects)
        
        # Görselleştir
        for obj in tracked_objects:
            track_id = obj['id']
            x1, y1, x2, y2 = obj['bbox']
            
            # Kutu çiz
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"ID: {track_id}", (x1, y1-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                       
            # Track bilgisi
            if track_id in track_manager.tracks:
                track = track_manager.tracks[track_id]
                
                # Trajectory çiz
                if len(track.positions) > 2:
                    points = [(int(p[0]), int(p[1])) for p in track.positions]
                    for i in range(1, len(points)):
                        cv2.line(frame, points[i-1], points[i], (255, 0, 0), 1)
                        
        # Frame numarasını yaz
        cv2.putText(frame, f"Frame: {frame_num}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                   
        # Göster
        cv2.imshow('ByteTrack Test', frame)
        out.write(frame)
        
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
            
    cv2.destroyAllWindows()
    out.release()

if __name__ == "__main__":
    test_bytetrack()