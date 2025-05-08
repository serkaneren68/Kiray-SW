import tkinter as tk
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
import threading
import numpy as np
import pytesseract
import math
from tkinter import messagebox

import signal
import sys


# Renk aralıkları tanımı
COLOR_RANGES = {
    "Kırmızı": [
        (np.array([0, 100, 100]), np.array([10, 255, 255])),
        (np.array([160, 100, 100]), np.array([179, 255, 255]))
    ],
    "Yeşil": [
        (np.array([35, 100, 100]), np.array([85, 255, 255]))
    ],
    "Mavi": [
        (np.array([100, 100, 100]), np.array([135, 255, 255]))
    ]
}

class App:
    def __init__(self, root):
        self.video_thread = None
        self.cap = None
        self.detected_shape = None
        self.confirmed_shape = None
        self.awaiting_confirmation = False
        self.detected_letter = None
        self.confirmed_letter = None

        self.root = root
        self.root.title("Hava Savunma Kontrol Paneli")
        self.root.configure(bg="black")
        self.root.geometry("1920x1080")
        self.running = False

        # Mod durumu
        self.mode = tk.StringVar(value="Manuel")
        self.confirmed_mode = "Mod 1"

        # UI bileşenleri
        self._create_canvas()
        self._create_mode_frame()
        self._create_fe_frame()
        self._create_letter_frame()
        self._create_controls()

        # QR ve YOLO detector
        self.qr_detector = cv2.QRCodeDetector()
        try:
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        except:
            pass
        self.model = YOLO("best2.pt")

        self._create_manual_controls()
        self._create_restricted_area_frame()


    def crosshair_ekle(self,frame):
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2

        # Yatay ve dikey sarı çizgi çiz
        cv2.line(frame, (center_x - 20, center_y), (center_x + 20, center_y), (0, 255, 0), 2)
        cv2.line(frame, (center_x, center_y - 20), (center_x, center_y + 20), (0, 255, 0), 2)

        return frame


    def _create_restricted_area_frame(self):
        frame = tk.LabelFrame(self.root, text="Atışa Yasaklı Alan", bg="black", fg="orange", bd=2)
        lbl = tk.Label(frame, text="Açı (0-360):", font=("Arial", 14), bg="black", fg="white")
        lbl.pack(pady=5)

        self.restricted_angle_var = tk.StringVar()
        entry = tk.Entry(frame, textvariable=self.restricted_angle_var, font=("Arial", 14), width=10)
        entry.pack(pady=5)

        btn = tk.Button(frame, text="ONAYLA", font=("Arial", 12), command=self.confirm_restricted_angle)
        btn.pack(pady=5)

        self.restricted_area_frame = frame

    def confirm_restricted_angle(self):
        angle_str = self.restricted_angle_var.get()
        try:
            angle = float(angle_str)
            if 0 <= angle <= 360:
                self.restricted_angle = angle
                messagebox.showinfo("Onay", f"Atışa Yasaklı Alan: {angle} Derece olarak ayarlandı.")
            else:
                messagebox.showerror("Hata", "Lütfen 0 ile 360 arasında bir değer giriniz.")
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir sayı giriniz.")

    def manual_command(self, direction):
        if direction == "up":
            print("Yukarı hareket et")
            # Buraya yukarı hareket için yapılacak işlemi ekleyebilirsin
        elif direction == "down":
            print("Aşağı hareket et")
            # Buraya aşağı hareket için yapılacak işlemi ekleyebilirsin
        elif direction == "left":
            print("Sola hareket et")
            # Buraya sola hareket için yapılacak işlemi ekleyebilirsin
        elif direction == "right":
            print("Sağa hareket et")
            # Buraya sağa hareket için yapılacak işlemi ekleyebilirsin
        elif direction == "shot":
            print("Atış yap")
            # Buraya atış yapma işlemini ekleyebilirsin 

    def _create_manual_controls(self):
        frame = tk.LabelFrame(self.root, text="Manuel Kontroller", bg="black", fg="yellow", bd=1)
        
        btn_up = tk.Button(frame, text="↑", font=("Arial", 28), width=3, height=1, command=lambda: self.manual_command("up"))
        btn_down = tk.Button(frame, text="↓", font=("Arial", 28), width=3, height=1, command=lambda: self.manual_command("down"))
        btn_left = tk.Button(frame, text="←", font=("Arial", 28), width=3, height=1, command=lambda: self.manual_command("left"))
        btn_right = tk.Button(frame, text="→", font=("Arial", 28), width=3, height=1, command=lambda: self.manual_command("right"))

        btn_shot = tk.Button(frame, text="atıs", font=("Arial", 28),  width=3, height=1, command=lambda: self.manual_command("shot"))
        
        btn_up.grid(row=0, column=1, pady=10)
        btn_left.grid(row=1, column=0, padx=10)
        btn_right.grid(row=1, column=3, padx=10)
        btn_down.grid(row=2, column=1, pady=10)
        btn_shot.grid(row=1, column=1, pady=10)
        
        self.manual_control_frame = frame


    def _create_canvas(self):
        self.canvas = tk.Canvas(self.root, bg="black", width=780, height=475,
                                highlightthickness=2, highlightbackground="gray")
        self.canvas.place(x=30, y=30)

    def _create_mode_frame(self):
        frame = tk.Frame(self.root, bg="black", width=900, height=140)
        frame.place(x=30, y=580)
        for i, m in enumerate(["Manuel", "Mod 1", "Mod 2", "Mod 3"]):
            tk.Radiobutton(
                frame,
                text=m,
                variable=self.mode,
                value=m,
                font=("Arial", 16),
                bg="black",
                fg="white",
                selectcolor="black"
            ).place(x=0 + i*175, y=5, width=150, height=40)
        self.btn_ok = tk.Button(frame, text="✔", fg="green", font=("Arial",20), command=self.confirm_mode)
        self.btn_no = tk.Button(frame, text="✖", fg="red", font=("Arial",20), command=self.reject_mode)
        self.btn_ok.place_forget()
        self.btn_no.place_forget()
        self.mode_frame = frame
        self.mode.trace_add("write", self.on_mode_change)

    def _create_fe_frame(self):
        frame = tk.LabelFrame(self.root, text="Renk Bazlı Sınıflandırma", bg="black", fg="limegreen", bd=2)
        lbl_friend = tk.Label(frame, text="Dost Rengi: MAVİ", font=("Arial",25), bg="black", fg="blue")
        lbl_enemy  = tk.Label(frame, text="Düşman Rengi: KIRMIZI", font=("Arial",25), bg="black", fg="red")
        lbl_friend.pack(anchor="w", pady=5, padx=10)
        lbl_enemy.pack(anchor="w", pady=5, padx=10)
        self.fe_frame = frame

    def _create_letter_frame(self):
        frame = tk.LabelFrame(self.root, text="Angajman Onay", bg="black", fg="dodgerblue", bd=2)
        self.letter_label = tk.Label(frame, text="Harf: —", font=("Arial",28), fg="cyan", bg="black")
        self.shape_label  = tk.Label(frame, text="Şekil: —", font=("Arial",28), fg="orange", bg="black")
        self.btn_accept  = tk.Button(frame, text="Angajmanı Kabul Et", font=("Arial",16), command=self.accept_engagement)
        self.letter_label.pack(pady=5)
        self.shape_label.pack(pady=5)
        self.btn_accept.pack(pady=10)
        self.letter_frame = frame

    def _create_controls(self):
        y = 700
        self.btn_start = tk.Button(self.root, text="BAŞLAT", font=("Arial",14), command=self.start)
        self.btn_stop  = tk.Button(self.root, text="DURDUR", font=("Arial",14), command=self.stop)
        self.btn_reset = tk.Button(self.root, text="RESET",  font=("Arial",14), bg="purple", fg="white", command=self.reset_system)
        self.btn_start.place(x=30, y=y, width=150, height=40)
        self.btn_stop.place(x=205, y=y, width=150, height=40)
        self.btn_reset.place(x=380, y=y, width=150, height=40)

    def on_mode_change(self, *args):
        idx = ["Manuel","Mod 1","Mod 2","Mod 3"].index(self.mode.get())
        x0 = idx * 175
        self.btn_ok.place(in_=self.mode_frame, x=x0, y=60, width=70, height=30)
        self.btn_no.place(in_=self.mode_frame, x=x0+80, y=60, width=70, height=30)

    def confirm_mode(self):
        self.confirmed_mode = self.mode.get()
        self.btn_ok.place_forget()
        self.btn_no.place_forget()
        self.fe_frame.place_forget()
        self.letter_frame.place_forget()
        self.manual_control_frame.place_forget()  # <--- Yön tuşlarını gizle

        if self.confirmed_mode == "Mod 2":
            self.fe_frame.place(x=1000, y=50, width=500, height=150)
        elif self.confirmed_mode == "Mod 3":
            self.letter_frame.place(x=1000, y=300, width=450, height=180)
            self.restricted_area_frame.place(x=1000, y=500, width=300, height=150)
            self.awaiting_confirmation = False
            self.detected_letter = None
            self.confirmed_letter = None
            self.detected_shape = None
            self.confirmed_shape = None
        elif self.confirmed_mode == "Manuel":
            self.manual_control_frame.place(x=1000, y=200, width=300, height=300)  # <--- Yön tuşlarını göster


    def reject_mode(self):
        self.mode.set(self.confirmed_mode)
        self.btn_ok.place_forget()
        self.btn_no.place_forget()

    def reset_system(self):
        self.mode.set("Mod 1")
        self.confirmed_mode = "Mod 1"
        self.btn_ok.place_forget()
        self.btn_no.place_forget()
        self.fe_frame.place_forget()
        self.letter_frame.place_forget()

    def accept_engagement(self):
        if self.awaiting_confirmation:
            self.letter_label.config(text=f"Harf: {self.confirmed_letter}")
            self.shape_label.config(text=f"Şekil: {self.confirmed_shape}")
            messagebox.showinfo(
                "Onay",
                f"Angajman: Harf:{self.confirmed_letter} Şekil:{self.confirmed_shape} KABUL EDİLDİ"
            )
            self.awaiting_confirmation = False

    def detect_color(self, roi):
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        counts = {"KIRMIZI": 0, "YEŞİL": 0, "MAVI": 0}
        
        for renk, araliklar in COLOR_RANGES.items():
            mask = None
            for lo, hi in araliklar:
                m = cv2.inRange(hsv, lo, hi)
                mask = m if mask is None else cv2.bitwise_or(mask, m)
            counts[renk] = cv2.countNonZero(mask)
        
        dominant_color = max(counts, key=counts.get)
        
        if counts[dominant_color] > 20:  # 50 pikselden fazlaysa güven
            return dominant_color
        else:
            return None


    def detect_shape(self, mask):
        """
        Mask üzerinden kontur bulup üçgen/kare/daire tespiti yapar.
        """
        cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not cnts:
            return None
        c = max(cnts, key=cv2.contourArea)
        peri = cv2.arcLength(c, True)
        if peri == 0:
            return None
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        area = cv2.contourArea(c)
        circularity = 4 * math.pi * (area / (peri * peri))

        print(f"[Mod3] approx len: {len(approx)}, circularity: {circularity:.2f}", flush=True)

        if circularity >= 0.80:
            return "Daire"
        elif len(approx) == 3:
            return "Üçgen"
        elif len(approx) == 4:
            # istenirse kare/dikdörtgen ayrımı eklenebilir, ama biz hep "Kare" diyoruz
            return "Kare"
        else:
            return None

    def detect_color_shape(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        best_area = 0
        best_color = None
        best_shape = None
        best_cnt = None

        # her renk aralığı için maske oluştur
        for renk, araliklar in COLOR_RANGES.items():
            # her alt aralığı birleştir
            mask_full = None
            for lo, hi in araliklar:
                m = cv2.inRange(hsv, lo, hi)
                mask_full = m if mask_full is None else cv2.bitwise_or(mask_full, m)
            # gürültüyü temizle
            kernel = np.ones((5,5), np.uint8)
            mask_full = cv2.morphologyEx(mask_full, cv2.MORPH_OPEN, kernel)

            # bu maskeden şekil tespit et
            shape = self.detect_shape(mask_full)
            if not shape:
                continue

            # maskeden konturları al, en büyüğünü seç
            cnts, _ = cv2.findContours(mask_full, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in cnts:
                area = cv2.contourArea(c)
                if area >= 1500 and area > best_area:
                    best_area = area
                    best_color = renk
                    best_shape = shape
                    best_cnt = c

        # bulduysak çiz ve label
        if best_cnt is not None:
            x, y, w, h = cv2.boundingRect(best_cnt)
            label = f"{best_color} {best_shape}"
            cv2.drawContours(frame, [best_cnt], -1, (0,255,0), 2)
            cv2.putText(frame, label, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
            print(f"[Mod3] Tespit: {label}", flush=True)
            return frame, (best_color, best_shape)

        # hiçbir şey tespit edilemediyse
        return frame, (None, None)


    def start(self):
        if not self.running:
            self.running = True
            self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
            self.video_thread.start()


    def stop(self):
        self.running = False
        if hasattr(self, "cap") and self.cap.isOpened():
            self.cap.release()
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join(timeout=2)  # thread kapanmasını bekle
        print("Program durduruluyor...")
        self.root.after(0, self.root.destroy)



    def video_loop(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 780)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            mode = self.confirmed_mode
            ann = frame.copy()

            if mode == "Manuel":
                ann = frame.copy()
            elif mode == "Mod 1" or mode == "Mod 2":
                results = self.model(frame, imgsz=640)[0]
                for box, cls in zip(results.boxes.xyxy.cpu().numpy(),
                                    results.boxes.cls.cpu().numpy()):
                    if results.names[int(cls)] != "balloon":
                        continue
                    x1,y1,x2,y2 = map(int, box)
                    roi = frame[y1:y2, x1:x2]
                    if mode == "Mod 2":
                        clr = self.detect_color(roi)
                        if clr:
                            clr_upper = clr.upper()
                            if clr_upper == "MAVI":
                                text = "dost"
                            elif clr_upper == "KIRMIZI":
                                text = "dusman"
                            else:
                                text = "BİLİNMİYOR"
                        else:
                            text = "BİLİNMİYOR"
                    else:
                        text = "balloon"
                    cv2.rectangle(ann, (x1,y1),(x2,y2),(0,255,0),2)
                    cv2.putText(ann, text, (x1,y1-10), cv2.FONT_HERSHEY_SIMPLEX,
                                0.8, (255,255,255),2)
            else:
                if not self.awaiting_confirmation:
                    data, pts, _ = self.qr_detector.detectAndDecode(frame)
                    if data in ("A","B"):
                        self.detected_letter = data
                        self.confirmed_letter = data
                        self.letter_label.config(text=f"Harf: {data}")
                    processed_frame, result = self.detect_color_shape(frame)
                    color, shape = result
                    if color and shape:
                        self.detected_shape = f"{color} {shape}"
                        self.confirmed_shape = f"{color} {shape}"
                        self.shape_label.config(text=f"Şekil: {color} {shape}")
                    ann = processed_frame
                else:
                    ann = frame.copy()

            # ⬇️ Crosshair'ı ekle
            ann = self.crosshair_ekle(ann)

            # ⬇️ Tkinter'de gösterim
            image = cv2.cvtColor(ann, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=image)
            self.canvas.image = image

        self.cap.release()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)

    def signal_handler(sig, frame):
        print("CTRL+C algılandı. Program kapatılıyor...")
        app.stop()

    signal.signal(signal.SIGINT, signal_handler)

    root.mainloop()

