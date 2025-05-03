import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
from detection import DetectionSystem

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Hava Savunma Kontrol Paneli")
        self.detection_system = DetectionSystem(self.update_ui, self.update_engagement)
        self.setup_gui()

    def setup_gui(self):
        # Sol Frame (Listbox)
        left_frame = ttk.Frame(self.root, width=200)
        left_frame.pack(side="left", fill="y", padx=5, pady=5)
        ttk.Label(left_frame, text="Tespit Edilenler:").pack(anchor="nw")
        self.listbox = tk.Listbox(left_frame, height=20)
        self.listbox.pack(fill="both", expand=True)

        # Canvas (Görüntü)
        self.canvas = tk.Canvas(self.root, width=640, height=480, bg="black")
        self.canvas.pack(side="left", padx=5, pady=5)

        # Mod Seçim Bileşenleri
        mode_frame = ttk.LabelFrame(self.root, text="Modlar")
        mode_frame.place(x=660, y=20)
        for m in ["Mod 1", "Mod 2", "Mod 3"]:
            ttk.Radiobutton(
                mode_frame,
                text=m,
                variable=self.detection_system.mode,
                value=m
            ).pack(anchor="w", padx=5, pady=2)

        # Angajman Bileşenleri
        self.engage_info = ttk.Label(self.root, text="Güncel Angajman: Harf: -, Hedef: -", font=("Arial", 10))
        self.engage_info.place(x=660, y=160)
        self.engage_button = ttk.Button(self.root, text="Angajmanı Kabul Et", command=self.detection_system.accept_engagement)
        self.engage_button.place(x=660, y=190)
        self.engage_status = ttk.Label(self.root, text="", font=("Arial", 10))
        self.engage_status.place(x=660, y=230)

        # Kontrol Butonları
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side="bottom", fill="x", pady=5)
        ttk.Button(control_frame, text="Başlat", command=self.detection_system.start).pack(side="left", padx=10)
        ttk.Button(control_frame, text="Durdur", command=self.detection_system.stop).pack(side="left")

        # Klavye Bağlantısı
        self.root.bind("0", self.detection_system.trigger_warning)

    def update_ui(self, frame, labels):
        self.listbox.delete(0, tk.END)
        for lbl in sorted(set(labels)):
            self.listbox.insert(tk.END, lbl)
        
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        tk_img = ImageTk.PhotoImage(pil_img)
        self.canvas.create_image(0, 0, anchor="nw", image=tk_img)
        self.canvas.image = tk_img

    def update_engagement(self, letter, target):
        self.engage_info.config(text=f"Güncel Angajman: Harf: {letter}, Hedef: {target}")
        self.engage_status.config(text=f"Harf: {letter}, Hedef: {target} angajmanı kabul edildi.")