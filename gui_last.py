import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
import threading
import numpy as np
import easyocr

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Hava Savunma Kontrol Paneli")
        self.running = False
        self.warning = False
        self.mode = tk.StringVar(value="Mod 1")
        self.detected_letter = ""
        self.detected_target = ""
        
        left_frame = ttk.Frame(root, width=200)
        left_frame.pack(side="left", fill="y", padx=5, pady=5)
        ttk.Label(left_frame, text="Tespit Edilenler:").pack(anchor="nw")
        self.listbox = tk.Listbox(left_frame, height=20)
        self.listbox.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(root, width=640, height=480, bg="black")
        self.canvas.pack(side="left", padx=5, pady=5)

        mode_frame = ttk.LabelFrame(root, text="Modlar")
        mode_frame.place(x=660, y=20)
        for m in ["Mod 1", "Mod 2", "Mod 3"]:
            ttk.Radiobutton(
                mode_frame, text=m, variable=self.mode, value=m
            ).pack(anchor="w", padx=5, pady=2)

        self.engage_info = ttk.Label(root, text="Güncel Angajman: Harf: -, Hedef: -", font=("Arial", 10))
        self.engage_info.place(x=660, y=160)

        self.engage_button = ttk.Button(root, text="Angajmanı Kabul Et", command=self.accept_engagement)
        self.engage_button.place(x=660, y=190)

        self.engage_status = ttk.Label(root, text="", font=("Arial", 10))
        self.engage_status.place(x=660, y=230)

        control_frame = ttk.Frame(root)
        control_frame.pack(side="bottom", fill="x", pady=5)
        ttk.Button(control_frame, text="Başlat", command=self.start).pack(side="left", padx=10)
        ttk.Button(control_frame, text="Durdur", command=self.stop).pack(side="left")

        root.bind("0", self.trigger_warning)

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
        msg = f"Harf: {self.detected_letter}, Hedef: {self.detected_target} angajmanı kabul edildi."
        self.engage_status.config(text=msg)

    def detect_color_shape(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        color_ranges = {
            "Kırmızı": [
                (np.array([0, 100, 100]), np.array([10, 255, 255])),
                (np.array([160, 100, 100]), np.array([179, 255, 255]))
            ],
            "Yeşil": [(np.array([40, 70, 70]), np.array([80, 255, 255]))],
            "Mavi": [(np.array([100, 150, 0]), np.array([140, 255, 255]))],
        }

        target_detected = ""

        for renk, araliklar in color_ranges.items():
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

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break

            if counter % skip == 0:
                annotated_frame = frame.copy()
                labels = []

                if self.mode.get() == "Mod 1" or self.mode.get() == "Mod 2":
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
                            if avg_sat < 50 and avg_val > 180:
                                color_name = "Beyaz"
                            elif avg_val < 50:
                                color_name = "Siyah"
                            elif avg_sat < 50:
                                color_name = "Gri"
                            elif (0 <= avg_hue <= 10) or (160 <= avg_hue <= 180):
                                color_name = "Kırmızı"
                            elif 11 <= avg_hue <= 25:
                                color_name = "Turuncu"
                            elif 26 <= avg_hue <= 35:
                                color_name = "Sarı"
                            elif 36 <= avg_hue <= 85:
                                color_name = "Yeşil"
                            elif 86 <= avg_hue <= 125:
                                color_name = "Mavi"
                            elif 126 <= avg_hue <= 159:
                                color_name = "Mor"
                            else:
                                color_name = "Belirsiz"
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
                    self.engage_info.config(
                        text=f"Güncel Angajman: Harf: {self.detected_letter}, Hedef: {self.detected_target}"
                    )

                last_annotated = annotated_frame

            display_frame = last_annotated if last_annotated is not None else frame
            counter += 1

            self.listbox.delete(0, tk.END)
            for lbl in sorted(set(labels)):
                self.listbox.insert(tk.END, lbl)

            if self.warning:
                overlay = display_frame.copy()
                h, w = overlay.shape[:2]
                cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 255), thickness=50)
                display_frame = cv2.addWeighted(overlay, 0.5, display_frame, 0.5, 0)
                self.warning = False

            img_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)
            tk_img = ImageTk.PhotoImage(pil_img)

            self.canvas.create_image(0, 0, anchor="nw", image=tk_img)
            self.canvas.image = tk_img

        cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x550")
    app = App(root)
    root.mainloop()
