"""
YOLO model ile nesne tespiti
"""
from ultralytics import YOLO
import cv2

class YoloDetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        
    def detect(self, frame):
        """Frame'de nesne tespiti yap"""
        results = self.model(frame, imgsz=640)[0]
        detections = []
        
        for i, box in enumerate(results.boxes.xyxy.cpu().numpy()):
            cls = int(results.boxes.cls[i].cpu().numpy())
            conf = float(results.boxes.conf[i].cpu().numpy())
            
            if results.names[cls] == "balloon":
                x1, y1, x2, y2 = map(int, box)
                detections.append({
                    'bbox': (x1, y1, x2, y2),
                    'confidence': conf,
                    'class': 'balloon'
                })
                
        return detections
    
    def draw_detections(self, frame, detections, labels=None):
        """Tespitleri frame üzerine çiz"""
        for i, det in enumerate(detections):
            x1, y1, x2, y2 = det['bbox']
            label = labels[i] if labels and i < len(labels) else det['class']
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                       
        return frame