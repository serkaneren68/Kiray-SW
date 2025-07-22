import cv2


class QRDetector:
    def __init__(self):
        self.qr_detector = cv2.QRCodeDetector()
    
    def detect(self, frame):
        try:
            data, pts, _ = self.qr_detector.detectAndDecode(frame)
            if data in ("A", "B"):
                return data
        except:
            pass
        return None