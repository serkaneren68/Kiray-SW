# gui.py

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
import threading
import numpy as np  # Renk analizi için eklendi

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
        self.model = YOLO("best.pt")

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
                results = self.model(frame, imgsz=160)[0]
                annotated_frame = frame.copy()

                for box, cls in zip(results.boxes.xyxy, results.boxes.cls):
                    x1, y1, x2, y2 = map(int, box.cpu().numpy())
                    class_id = int(cls)
                    class_name = results.names[class_id]

                    # ROI: kutu içi alan
                    roi = frame[y1:y2, x1:x2]
                    if roi.size == 0:
                        continue
                    avg_color = roi.mean(axis=(0, 1))  # BGR ortalama renk
                    b, g, r = avg_color

                    # Gelişmiş renk tespiti
                    if r > 180 and g < 100 and b < 100:
                        color_name = "kirmizi"
                    elif r > 180 and g > 180 and b < 100:
                        color_name = "sari"
                    elif r > 180 and g > 100 and b < 50:
                        color_name = "turuncu"
                    elif g > 160 and r < 100 and b < 100:
                        color_name = "yesil"
                    elif b > 160 and r < 100 and g < 100:
                        color_name = "mavi"
                    elif r > 150 and b > 150 and g < 100:
                        color_name = "mor"
                    elif r > 200 and g > 200 and b > 200:
                        color_name = "beyaz"
                    elif r < 50 and g < 50 and b < 50:
                        color_name = "siyah"
                    elif abs(r - g) < 15 and abs(g - b) < 15 and r < 180:
                        color_name = "gri"
                    else:
                        color_name = "belirsiz"

                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(
                        annotated_frame,
                        f"{class_name} ({color_name})",
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

            labels = [
                results.names[int(cls)] for cls in results.boxes.cls.cpu().numpy()
            ]
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