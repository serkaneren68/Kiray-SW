import cv2

def add_crosshair(frame):
    """Frame'e crosshair (çapraz çizgi) ekler"""
    h, w = frame.shape[:2]
    center_x, center_y = w // 2, h // 2

    # Yatay ve dikey sarı çizgi çiz
    cv2.line(frame, (center_x - 20, center_y), (center_x + 20, center_y), (0, 255, 0), 2)
    cv2.line(frame, (center_x, center_y - 20), (center_x, center_y + 20), (0, 255, 0), 2)

    return frame