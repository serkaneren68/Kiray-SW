# gui.py

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
import threading
import numpy as np

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Hava Savunma Kontrol Paneli")
        self.running = False
        self.warning = False
        self.mode = tk.StringVar(value="Mod 1")

        # Sol: Tespit Edilenler Listesi
        left_frame = ttk.Frame(root, width=200)
        left_frame.pack(side="left", fill="y", padx=5, pady=5)
        ttk.Label(left_frame, text="Tespit Edilenler:").pack(anchor="nw")
        self.listbox = tk.Listbox(left_frame, height=20)
        self.listbox.pack(fill="both", expand=True)

        # Ortada: Video Görüntüsü
        self.canvas = tk.Canvas(root, width=640, height=480, bg="black")
        self.canvas.pack(side="left", padx=5, pady=5)

        # Sağ üst: Mod Seçimi
        mode_frame = ttk.LabelFrame(root, text="Modlar")
        mode_frame.place(x=660, y=20)
        for m in ["Mod 1", "Mod 2", "Mod 3"]:
            ttk.Radiobutton(
                mode_frame, text=m, variable=self.mode, value=m
            ).pack(anchor="w", padx=5, pady=2)

        # Alt: Başlat / Durdur Butonları
        control_frame = ttk.Frame(root)
        control_frame.pack(side="bottom", fill="x", pady=5)
        ttk.Button(control_frame, text="Başlat", command=self.start).pack(side="left", padx=10)
        ttk.Button(control_frame, text="Durdur", command=self.stop).pack(side="left")

        # Klavyede '0' tuşu ile uyarı efekti tetikleme
        root.bind("0", self.trigger_warning)

        # YOLOv8 nano modelini yükle
        self.model = YOLO("best2.pt")

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.video_loop, daemon=True).start()

    def stop(self):
        self.running = False

    def trigger_warning(self, event=None):
        self.warning = True

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
                results = self.model(frame, imgsz=640)[0]
                annotated_frame = frame.copy()

                labels = []

                for box, cls in zip(results.boxes.xyxy, results.boxes.cls):
                    x1, y1, x2, y2 = map(int, box.cpu().numpy())
                    class_id = int(cls)
                    class_name = results.names[class_id]

                    if class_name != "balloon":
                        continue

                    labels.append(class_name)

                    if self.mode.get() == "Mod 1":
                        # Sadece balonu yaz
                        label_text = class_name
                    elif self.mode.get() == "Mod 2":
                        # Renk tespiti yap
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
                            color_name = "beyaz"
                        elif avg_val < 50:
                            color_name = "siyah"
                        elif avg_sat < 50:
                            color_name = "gri"
                        elif (0 <= avg_hue <= 10) or (160 <= avg_hue <= 180):
                            color_name = "kirmizi"
                        elif 11 <= avg_hue <= 25:
                            color_name = "turuncu"
                        elif 26 <= avg_hue <= 35:
                            color_name = "sari"
                        elif 36 <= avg_hue <= 85:
                            color_name = "yesil"
                        elif 86 <= avg_hue <= 125:
                            color_name = "mavi"
                        elif 126 <= avg_hue <= 159:
                            color_name = "mor"
                        else:
                            color_name = "belirsiz"

                        label_text = f"{class_name} ({color_name})"
                    else:
                        label_text = class_name  # Mod 3 için sadece isim

                    # Görselde kutu ve etiket çiz
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
