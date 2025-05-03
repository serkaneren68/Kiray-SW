import cv2
import numpy as np
import easyocr
import threading
import tkinter as tk
from ultralytics import YOLO
from config import COLOR_RANGES, HUE_MAPPING

class DetectionSystem:
    def __init__(self, ui_callback, engagement_callback):
        self.ui_callback = ui_callback
        self.engagement_callback = engagement_callback
        self.running = False
        self.warning = False
        self.mode = tk.StringVar(value="Mod 1")
        self.detected_letter = ""
        self.detected_target = ""
        self.model = YOLO("best2.pt")
        self.reader = easyocr.Reader(['en'], gpu=True)

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.video_loop, daemon=True).start()

    def stop(self):
        self.running = False

    def trigger_warning(self, event=None):
        self.warning = True

    def accept_engagement(self):
        self.engagement_callback(self.detected_letter, self.detected_target)

    def detect_color_shape(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        target_detected = ""

        for renk, araliklar in COLOR_RANGES.items():
            for lower, upper in araliklar:
                mask = cv2.inRange(hsv, lower, upper)
                kernel = np.ones((5, 5), np.uint8)
                mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    if area < 1500:
                        continue
                    perimeter = cv2.arcLength(cnt, True)
                    if perimeter == 0:
                        continue
                    circularity = 4 * np.pi * (area / (perimeter * perimeter))
                    if circularity < 0.3:
                        continue
                    approx = cv2.approxPolyDP(cnt, 0.04 * perimeter, True)
                    shape = "Bilinmiyor"
                    if len(approx) == 3:
                        shape = "Üçgen"
                    elif len(approx) == 4:
                        shape = "Kare"
                    elif len(approx) > 5:
                        shape = "Daire"
                    if shape != "Bilinmiyor":
                        x, y, w, h = cv2.boundingRect(cnt)
                        cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)
                        cv2.putText(frame, f"{renk} {shape}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                        target_detected = f"{renk} {shape}"
        return frame, target_detected

    def detect_letters(self, frame):
        results = self.reader.readtext(frame)
        letter_detected = ""
        for (bbox, text, prob) in results:
            (top_left, top_right, bottom_right, bottom_left) = bbox
            top_left = tuple(map(int, top_left))
            bottom_right = tuple(map(int, bottom_right))
            if text.strip().upper() in ['A', 'B']:
                cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
                cv2.putText(frame, f'{text}', top_left, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                letter_detected = text.strip().upper()
        return frame, letter_detected

    def video_loop(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        skip = 2
        counter = 0
        last_annotated = None
        labels = []

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break

            if counter % skip == 0:
                annotated_frame = frame.copy()
                labels = []

                if self.mode.get() in ["Mod 1", "Mod 2"]:
                    results = self.model(frame, imgsz=640)[0]
                    for box, cls in zip(results.boxes.xyxy, results.boxes.cls):
                        x1, y1, x2, y2 = map(int, box.cpu().numpy())
                        class_id = int(cls)
                        class_name = results.names[class_id]

                        if class_name != "balloon":
                            continue

                        labels.append(class_name)
                        label_text = class_name

                        if self.mode.get() == "Mod 2":
                            roi = frame[y1:y2, x1:x2]
                            if roi.size == 0:
                                continue
                            hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                            hue = hsv_roi[:, :, 0]
                            sat = hsv_roi[:, :, 1]
                            val = hsv_roi[:, :, 2]
                            avg_hue = int(np.median(hue))
                            avg_sat = int(np.median(sat))
                            avg_val = int(np.median(val))

                            color_name = "Belirsiz"
                            for (h_range, name) in HUE_MAPPING.items():
                                if h_range[0] <= avg_hue <= h_range[1]:
                                    color_name = name
                                    break
                            if avg_sat < 50 and avg_val > 180:
                                color_name = "Beyaz"
                            elif avg_val < 50:
                                color_name = "Siyah"
                            elif avg_sat < 50:
                                color_name = "Gri"

                            label_text = f"{class_name} ({color_name})"

                        cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(
                            annotated_frame,
                            label_text,
                            (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6,
                            (255, 255, 255),
                            2,
                            cv2.LINE_AA
                        )
                elif self.mode.get() == "Mod 3":
                    annotated_frame, detected_target = self.detect_color_shape(annotated_frame)
                    annotated_frame, detected_letter = self.detect_letters(annotated_frame)
                    if detected_letter:
                        self.detected_letter = detected_letter
                    if detected_target:
                        self.detected_target = detected_target

                last_annotated = annotated_frame

            display_frame = last_annotated if last_annotated is not None else frame
            counter += 1

            if self.warning:
                overlay = display_frame.copy()
                h, w = overlay.shape[:2]
                cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 255), thickness=50)
                display_frame = cv2.addWeighted(overlay, 0.5, display_frame, 0.5, 0)
                self.warning = False

            self.ui_callback(display_frame, labels)
        
        cap.release()