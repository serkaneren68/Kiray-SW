import tkinter as tk
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
import threading
import numpy as np
import pytesseract
import time

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Hava Savunma Kontrol Paneli")
        self.root.geometry("1920x1080")
        self.root.configure(bg='black')  # Arka planı siyah yap
        self.running = False

        # Mode state
        self.mode = tk.StringVar(value="Manuel")
        self.confirmed_mode = "Mod 1"
        self.awaiting_letter = False
        self.detected_letter = None
        self.confirmed_letter = None

        # Color state
        self.friend_color = tk.StringVar(value="yesil")
        self.enemy_color  = tk.StringVar(value="kirmizi")

        # Tesseract config
        try:
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        except:
            pass

        # 1) Live view canvas
        self.canvas = tk.Canvas(root, bg="black", width=1280, height=720,
                               highlightthickness=0)  # Çerçeve kaldırıldı
        self.canvas.place(x=50, y=20)

        # 2) Mode selection frames
        self.mode_frames = []
        modes = ["Manuel","Mod 1","Mod 2","Mod 3"]
        for i, m in enumerate(modes):
            frame = tk.LabelFrame(root, text=m, fg="white", bg="black", 
                                 font=("Arial",14), bd=2, relief="solid")
            frame.place(x=50 + i*300, y=760, width=280, height=120)
            rb = tk.Radiobutton(frame, text=m, variable=self.mode, value=m,
                               font=("Arial",16), bg="black", fg="white", selectcolor="black")
            rb.place(x=20, y=10)
            self.mode_frames.append(frame)

        self.btn_ok = tk.Button(root, text="✔", fg="green", font=("Arial",20),
                               bg="black", activebackground="black")
        self.btn_no = tk.Button(root, text="✖", fg="red", font=("Arial",20),
                              bg="black", activebackground="black")
        self.mode.trace_add("write", self.on_mode_change)

        # 5) Friend/enemy frame
        self.fe_frame = tk.LabelFrame(root, text="Dost/Düşman Renk Seçimi",
                                     fg="limegreen", bg="black", font=("Arial",14))
        # İçerik aynı kalacak...

        # 6) Letter confirm frame
        self.letter_frame = tk.LabelFrame(root, text="Harf Onay",
                                         fg="dodgerblue", bg="black", font=("Arial",14))
        # İçerik aynı kalacak...

        # 3+4) Control buttons
        btn_style = {'font': ("Arial",16), 'bg':'#333333', 'fg':'white', 
                    'width':12, 'height':2}
        self.btn_start = tk.Button(root, text="BAŞLAT", command=self.start, **btn_style)
        self.btn_stop  = tk.Button(root, text="DURDUR", command=self.stop, **btn_style)
        self.btn_reset = tk.Button(root, text="RESET", command=self.reset_system,
                                  bg='purple', fg='white', width=12, height=2)
        
        # Butonları sağ alta yerleştir
        self.btn_start.place(relx=0.95, rely=0.95, anchor='se')
        self.btn_stop.place(relx=0.95, rely=0.85, anchor='se')
        self.btn_reset.place(relx=0.95, rely=0.75, anchor='se')

        # YOLO model & OCR
        self.model = YOLO("best6.pt")
        self.ocr_conf = r"--oem 3 --psm 6"

    def on_mode_change(self, *args):
        # Buton konumlarını güncelle
        current_mode = self.mode.get()
        index = ["Manuel","Mod 1","Mod 2","Mod 3"].index(current_mode)
        x_pos = 50 + index*300 + 140
        self.btn_ok.place(x=x_pos, y=830)
        self.btn_no.place(x=x_pos+60, y=830)

    def confirm_mode(self):
        # Önceki kod aynı kalacak...
        # Boyut ayarlamaları eklendi
        if self.confirmed_mode == "Mod 2":
            self.fe_frame.place(x=1380, y=20, width=500, height=200)
        if self.confirmed_mode == "Mod 3":
            self.letter_frame.place(x=1380, y=250, width=500, height=200)

    # Diğer fonksiyonlar aynı kalacak...
    # Renk teması için gerekli diğer ayarlamalar...

    def video_loop(self):
        # Önceki video loop kodları aynı kalacak...
        # Görsel iyileştirmeler eklenebilir...

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()