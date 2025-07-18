import sys, os
import tkinter as tk
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
import threading
import numpy as np
import math
from tkinter import messagebox
import signal
import serial
import time

# Bu betik dosyasının bulunduğu klasör
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ByteTrack klasör yolu
BT_DIR = os.path.join(BASE_DIR, "ByteTrack")
if BT_DIR not in sys.path:
    sys.path.insert(0, BT_DIR)

from yolox.tracker.byte_tracker import BYTETracker

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
        # Ortam değişkenleri (Windows için)
        os.environ["OPENCV_VIDEOIO_PRIORITY_DSHOW"] = "1"
        
        self.video_thread = None
        self.cap = None
        self.detected_shape = None
        self.confirmed_shape = None
        self.awaiting_confirmation = False
        self.detected_letter = None
        self.confirmed_letter = None
        self.last_command_time = 0
        self.command_delay = 0.1
        self.restricted_angle = None
        self.tracked_object = None
        self.tracking_enabled = False
        self.camera_index = 0  # Varsayılan kamera indeksi

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

        # Kamera seçim frame'i ekle
        self._create_camera_selection_frame()

        # Arduino bağlantısı (DÜZELTME: Büyük S ile Serial)
        try:
            # Pyserial'ın doğru import edildiğinden emin olun
            self.arduino = serial.Serial('COM5', 9600, timeout=1)
            time.sleep(2)
            print("Arduino'ya bağlandı")
        except Exception as e:
            print(f"[HATA] Arduino bağlantısı kurulamadı: {e}")
            self.arduino = None

        # QR ve YOLO detector
        self.qr_detector = cv2.QRCodeDetector()
        try:
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        except:
            pass
        
        try:
            self.model = YOLO("best2.pt")
        except Exception as e:
            print(f"YOLO model yükleme hatası: {e}")
            self.model = None

        self._create_manual_controls()
        self._create_restricted_area_frame()
        self._create_tracking_controls()

    def _create_camera_selection_frame(self):
        frame = tk.LabelFrame(self.root, text="Kamera Seçimi", bg="black", fg="yellow", bd=1)
        frame.place(x=600, y=580, width=300, height=100)
        
        lbl = tk.Label(frame, text="Kamera İndeksi:", bg="black", fg="white")
        lbl.pack(side=tk.LEFT, padx=5)
        
        self.camera_var = tk.StringVar(value="0")
        camera_entry = tk.Entry(frame, textvariable=self.camera_var, width=5)
        camera_entry.pack(side=tk.LEFT, padx=5)
        
        btn_apply = tk.Button(frame, text="Uygula", command=self.apply_camera_index)
        btn_apply.pack(side=tk.LEFT, padx=5)
        
        self.camera_frame = frame

    def apply_camera_index(self):
        try:
            new_index = int(self.camera_var.get())
            self.camera_index = new_index
            messagebox.showinfo("Bilgi", f"Kamera indeksi {new_index} olarak ayarlandı")
            
            # Eğer video döngüsü çalışıyorsa yeniden başlat
            if self.running:
                self.stop()
                time.sleep(1)
                self.start()
                
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir sayı giriniz")

    def _create_tracking_controls(self):
        frame = tk.LabelFrame(self.root, text="Otomatik Takip", bg="black", fg="cyan", bd=1)
        self.tracking_btn = tk.Button(
            frame, 
            text="TAKİBİ BAŞLAT", 
            font=("Arial", 14),
            command=self.toggle_tracking
        )
        self.tracking_btn.pack(pady=10, padx=20)
        frame.place(x=1000, y=700, width=200, height=100)
        
    def toggle_tracking(self):
        self.tracking_enabled = not self.tracking_enabled
        if self.tracking_enabled:
            self.tracking_btn.config(text="TAKİBİ DURDUR", bg="red")
            print("Otomatik takip başlatıldı")
        else:
            self.tracking_btn.config(text="TAKİBİ BAŞLAT", bg="SystemButtonFace")
            print("Otomatik takip durduruldu")

    def crosshair_ekle(self, frame):
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
        current_time = time.time()
        if current_time - self.last_command_time < self.command_delay:
            return
            
        self.last_command_time = current_time
        
        if self.arduino:
            try:
                # DÜZELTME: Direkt byte string gönder
                if direction == "up":
                    self.arduino.write(b'U')
                    print("Yukarı komutu gönderildi")
                elif direction == "down":
                    self.arduino.write(b'D')
                    print("Aşağı komutu gönderildi")
                elif direction == "left":
                    self.arduino.write(b'L')
                    print("Sola komutu gönderildi")
                elif direction == "right":
                    self.arduino.write(b'R')
                    print("Sağa komutu gönderildi")
                elif direction == "shot":
                    self.arduino.write(b'S')
                    print("Atış komutu gönderildi")
                elif direction == "stop":
                    self.arduino.write(b'X')
                    print("Durdurma komutu gönderildi")
            except Exception as e:
                print(f"Komut gönderme hatası: {e}")

    def _create_manual_controls(self):
        frame = tk.LabelFrame(self.root, text="Manuel Kontroller", bg="black", fg="yellow", bd=1)
        
        btn_up = tk.Button(frame, text="↑", font=("Arial", 28), width=3, height=1, 
                          command=lambda: self.manual_command("up"))
        btn_down = tk.Button(frame, text="↓", font=("Arial", 28), width=3, height=1, 
                            command=lambda: self.manual_command("down"))
        btn_left = tk.Button(frame, text="←", font=("Arial", 28), width=3, height=1, 
                            command=lambda: self.manual_command("left"))
        btn_right = tk.Button(frame, text="→", font=("Arial", 28), width=3, height=1, 
                             command=lambda: self.manual_command("right"))
        btn_shot = tk.Button(frame, text="ATIŞ", font=("Arial", 16), width=5, height=1, 
                            command=lambda: self.manual_command("shot"))
        btn_stop = tk.Button(frame, text="DUR", font=("Arial", 16), width=5, height=1, 
                            command=lambda: self.manual_command("stop"))
        
        btn_up.grid(row=0, column=1, pady=5)
        btn_left.grid(row=1, column=0, padx=5)
        btn_right.grid(row=1, column=2, padx=5)
        btn_down.grid(row=2, column=1, pady=5)
        btn_shot.grid(row=1, column=1, pady=5)
        btn_stop.grid(row=3, column=1, pady=5)
        
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
        self.manual_control_frame.place_forget()
        self.restricted_area_frame.place_forget()

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
            self.manual_control_frame.place(x=1000, y=200, width=300, height=300)

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
        self.manual_control_frame.place_forget()
        self.restricted_area_frame.place_forget()

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
        if roi.size == 0:
            return None
            
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        counts = {"Kırmızı": 0, "Yeşil": 0, "Mavi": 0}
        
        for renk, araliklar in COLOR_RANGES.items():
            mask = None
            for lo, hi in araliklar:
                m = cv2.inRange(hsv, lo, hi)
                mask = m if mask is None else cv2.bitwise_or(mask, m)
            counts[renk] = cv2.countNonZero(mask)
        
        dominant_color = max(counts, key=counts.get)
        
        if counts[dominant_color] > 20:
            return dominant_color
        else:
            return None

    def detect_shape(self, mask):
        if mask.size == 0:
            return None
            
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

        if circularity >= 0.80:
            return "Daire"
        elif len(approx) == 3:
            return "Üçgen"
        elif len(approx) == 4:
            return "Kare"
        else:
            return None

    def detect_color_shape(self, frame):
        if frame is None or frame.size == 0:
            return frame, (None, None, None)
            
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        best_area = 0
        best_color = None
        best_shape = None
        best_cnt = None

        for renk, araliklar in COLOR_RANGES.items():
            mask_full = None
            for lo, hi in araliklar:
                m = cv2.inRange(hsv, lo, hi)
                mask_full = m if mask_full is None else cv2.bitwise_or(mask_full, m)
            kernel = np.ones((5,5), np.uint8)
            mask_full = cv2.morphologyEx(mask_full, cv2.MORPH_OPEN, kernel)

            shape = self.detect_shape(mask_full)
            if not shape:
                continue

            cnts, _ = cv2.findContours(mask_full, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in cnts:
                area = cv2.contourArea(c)
                if area >= 1500 and area > best_area:
                    best_area = area
                    best_color = renk
                    best_shape = shape
                    best_cnt = c

        if best_cnt is not None:
            x, y, w, h = cv2.boundingRect(best_cnt)
            label = f"{best_color} {best_shape}"
            cv2.drawContours(frame, [best_cnt], -1, (0,255,0), 2)
            cv2.putText(frame, label, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
            return frame, (best_color, best_shape, (x, y, w, h))

        return frame, (None, None, None)

    def track_object(self, frame, box):
        if not self.arduino or not self.tracking_enabled:
            return
        
        if box is None or len(box) != 4:
            return
        
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        x1, y1, x2, y2 = box
        obj_x = (x1 + x2) // 2  # Nesnenin merkez x koordinatı
        obj_y = (y1 + y2) // 2  # Nesnenin merkez y koordinatı
        
        # Yatay hata hesapla (nesne merkezi ile görüntü merkezi arasındaki fark)
        hata_x = obj_x - center_x
        
        # Hata eşik değerini aşıyorsa hareket komutu gönder
        if abs(hata_x) > 20:  # 20 piksel eşik değeri
            if hata_x < 0:    # Nesne sola kaymış
                self.arduino.write(b'L')
                print(f"Nesne sola kaymış, sola dön: {hata_x}")
            else:             # Nesne sağa kaymış
                self.arduino.write(b'R')
                print(f"Nesne sağa kaymış, sağa dön: {hata_x}")

    def start(self):
        if not self.running:
            self.running = True
            self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
            self.video_thread.start()

    def stop(self):
        self.running = False
        if self.arduino:
            try:
                self.arduino.close()
            except:
                pass
        if self.cap and self.cap.isOpened():
            self.cap.release()
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join(timeout=2)
        print("Program durduruluyor...")
        self.root.after(0, self.root.destroy)

    def video_loop(self):
        # Kamera başlatma (orijinal kodunuz aynen kaldı)
        try:
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                backends = [cv2.CAP_MSMF, cv2.CAP_ANY, 0]
                for backend in backends:
                    self.cap = cv2.VideoCapture(self.camera_index, backend)
                    if self.cap.isOpened():
                        print(f"Kamera {backend} backend'i ile açıldı")
                        break
            
            if not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.camera_index)
                
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 780)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
        except Exception as e:
            print(f"Kamera açma hatası: {e}")
            messagebox.showerror("Hata", f"Kamera açılamadı: {e}")
            self.running = False
            return

        if not self.cap.isOpened():
            messagebox.showerror("Hata", "Kamera açılamadı! Lütfen bağlantıyı kontrol edin.")
            self.running = False
            return

        # Kamera buffer'ını temizle
        for _ in range(5):
            self.cap.read()

        image_id = None
        last_command_time = time.time()
        command_delay = 0.1  # Komutlar arası minimum bekleme süresi (saniye)
        merkez_toleransi = 50  # Yaklaşık merkezleme için tolerans pikseli
        hareket_durumu = "DUR"  # DUR, SOL, SAĞ

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("Kare alınamadı. Tekrar deniyor...")
                time.sleep(0.1)
                continue

            mode = self.confirmed_mode
            ann = frame.copy()
            current_time = time.time()

            if mode == "Manuel":
                ann = frame.copy()
            elif (mode == "Mod 1" or mode == "Mod 2") and self.model:
                try:
                    results = self.model(frame, imgsz=640)[0]
                    for box, cls in zip(results.boxes.xyxy.cpu().numpy(),
                                        results.boxes.cls.cpu().numpy()):
                        if results.names[int(cls)] != "balloon":
                            continue
                        
                        x1, y1, x2, y2 = map(int, box)
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
                                    text = "BİLİNMİYEN"
                            else:
                                text = "BİLİNMİYEN"
                        else:
                            text = "balloon"
                        
                        # Görselleştirme
                        cv2.rectangle(ann, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(ann, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.8, (255, 255, 255), 2)
                        
                        # Takip aktifse ve yeterli zaman geçmişse merkezleme yap
                        if self.tracking_enabled and (current_time - last_command_time) > command_delay:
                            h, w = frame.shape[:2]
                            center_x, center_y = w // 2, h // 2
                            obj_x = (x1 + x2) // 2
                            obj_y = (y1 + y2) // 2
                            
                            # Yatay merkezleme - YENİ MANTIK
                            hata_x = obj_x - center_x
                            
                            # Nesneyi merkeze getirmek için hareket kontrolü
                            if abs(hata_x) > merkez_toleransi:
                                if hata_x < 0:
                                    if hareket_durumu != "SOL":
                                        if self.arduino:
                                            self.arduino.write(b'L')
                                            print("SOLA DÖN")
                                        hareket_durumu = "SOL"
                                else:
                                    if hareket_durumu != "SAĞ":
                                        if self.arduino:
                                            self.arduino.write(b'R')
                                            print("SAĞA DÖN")
                                        hareket_durumu = "SAĞ"
                            else:
                                if hareket_durumu != "DUR":
                                    if self.arduino:
                                        self.arduino.write(b'S')  # DUR komutu
                                        print("MERKEZE ULAŞILDI - DUR")
                                    hareket_durumu = "DUR"
                            
                            last_command_time = current_time

                except Exception as e:
                    print(f"Model işleme hatası: {e}")
            elif mode == "Mod 3":
                if not self.awaiting_confirmation:
                    try:
                        data, pts, _ = self.qr_detector.detectAndDecode(frame)
                        if data in ("A","B"):
                            self.detected_letter = data
                            self.confirmed_letter = data
                            self.letter_label.config(text=f"Harf: {data}")
                    except:
                        pass
                    try:
                        processed_frame, result = self.detect_color_shape(frame)
                        color, shape, box = result
                        if color and shape:
                            self.detected_shape = f"{color} {shape}"
                            self.confirmed_shape = f"{color} {shape}"
                            self.shape_label.config(text=f"Şekil: {color} {shape}")
                        ann = processed_frame
                    except Exception as e:
                        print(f"Şekil tanıma hatası: {e}")
                else:
                    ann = frame.copy()

            # Çapraz çizgi ekleme
            ann = self.crosshair_ekle(ann)

            # Görüntüyü göster
            try:
                image = cv2.cvtColor(ann, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                if image_id is None:
                    image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=image)
                else:
                    self.canvas.itemconfig(image_id, image=image)

                self.canvas.image = image
            except Exception as e:
                print(f"Görüntü işleme hatası: {e}")

        if self.cap.isOpened():
            self.cap.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)

    def signal_handler(sig, frame):
        print("CTRL+C algılandı. Program kapatılıyor...")
        app.stop()

    signal.signal(signal.SIGINT, signal_handler)

    root.mainloop()