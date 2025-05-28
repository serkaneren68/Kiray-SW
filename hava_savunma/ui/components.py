"""
UI bileşenleri
"""
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2

class CanvasComponent:
    """Ana görüntü canvas'ı"""
    def __init__(self, parent):
        self.canvas = tk.Canvas(
            parent, bg="black", width=780, height=475,
            highlightthickness=2, highlightbackground="gray"
        )
        self.canvas.place(x=30, y=30)
        
    def update_frame(self, frame):
        """Frame'i canvas'ta göster"""
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        image = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=image)
        self.canvas.image = image  # Referansı sakla

class ModeFrame:
    """Mod seçim frame'i"""
    def __init__(self, parent, mode_var, confirm_callback, reject_callback):
        self.frame = tk.Frame(parent, bg="black", width=900, height=140)
        self.frame.place(x=30, y=580)
        self.mode_var = mode_var
        
        # Mod butonları
        modes = ["Manuel", "Mod 1", "Mod 2", "Mod 3"]
        for i, m in enumerate(modes):
            tk.Radiobutton(
                self.frame, text=m, variable=self.mode_var, value=m,
                font=("Arial", 16), bg="black", fg="white", selectcolor="black"
            ).place(x=0 + i*175, y=5, width=150, height=40)
            
        # Onay/red butonları
        self.btn_ok = tk.Button(self.frame, text="✔", fg="green", font=("Arial",20), 
                               command=confirm_callback)
        self.btn_no = tk.Button(self.frame, text="✖", fg="red", font=("Arial",20), 
                               command=reject_callback)
        self.btn_ok.place_forget()
        self.btn_no.place_forget()
        
        # Mod değişikliğini izle
        self.mode_var.trace_add("write", self.on_mode_change)
        
    def on_mode_change(self, *args):
        """Mod değiştiğinde onay butonlarını göster"""
        idx = ["Manuel","Mod 1","Mod 2","Mod 3"].index(self.mode_var.get())
        x0 = idx * 175
        self.btn_ok.place(in_=self.frame, x=x0, y=60, width=70, height=30)
        self.btn_no.place(in_=self.frame, x=x0+80, y=60, width=70, height=30)
        
    def hide_buttons(self):
        """Onay butonlarını gizle"""
        self.btn_ok.place_forget()
        self.btn_no.place_forget()

class ControlButtons:
    """Kontrol butonları"""
    def __init__(self, parent, start_callback, stop_callback, reset_callback):
        y = 700
        self.btn_start = tk.Button(parent, text="BAŞLAT", font=("Arial",14), 
                                  command=start_callback)
        self.btn_stop = tk.Button(parent, text="DURDUR", font=("Arial",14), 
                                 command=stop_callback)
        self.btn_reset = tk.Button(parent, text="RESET", font=("Arial",14), 
                                  bg="purple", fg="white", command=reset_callback)
        
        self.btn_start.place(x=30, y=y, width=150, height=40)
        self.btn_stop.place(x=205, y=y, width=150, height=40)
        self.btn_reset.place(x=380, y=y, width=150, height=40)

class ManualControls:
    """Manuel kontrol butonları"""
    def __init__(self, parent, command_callback):
        self.frame = tk.LabelFrame(parent, text="Manuel Kontroller", 
                                  bg="black", fg="yellow", bd=1)
        self.command_callback = command_callback
        
        # Yön butonları
        btn_up = tk.Button(self.frame, text="↑", font=("Arial", 28), width=3, height=1,
                          command=lambda: command_callback("up"))
        btn_down = tk.Button(self.frame, text="↓", font=("Arial", 28), width=3, height=1,
                            command=lambda: command_callback("down"))
        btn_left = tk.Button(self.frame, text="←", font=("Arial", 28), width=3, height=1,
                            command=lambda: command_callback("left"))
        btn_right = tk.Button(self.frame, text="→", font=("Arial", 28), width=3, height=1,
                             command=lambda: command_callback("right"))
        btn_shot = tk.Button(self.frame, text="atış", font=("Arial", 28), width=3, height=1,
                            command=lambda: command_callback("shot"))
        
        # Grid yerleşimi
        btn_up.grid(row=0, column=1, pady=10)
        btn_left.grid(row=1, column=0, padx=10)
        btn_shot.grid(row=1, column=1, pady=10)
        btn_right.grid(row=1, column=2, padx=10)
        btn_down.grid(row=2, column=1, pady=10)
        
    def show(self):
        self.frame.place(x=1000, y=200, width=300, height=300)
        
    def hide(self):
        self.frame.place_forget()

class RestrictedAreaFrame:
    """Yasaklı alan ayar frame'i"""
    def __init__(self, parent, confirm_callback):
        self.frame = tk.LabelFrame(parent, text="Atışa Yasaklı Alan", 
                                  bg="black", fg="orange", bd=2)
        
        lbl = tk.Label(self.frame, text="Açı (0-360):", font=("Arial", 14), 
                      bg="black", fg="white")
        lbl.pack(pady=5)
        
        self.angle_var = tk.StringVar()
        entry = tk.Entry(self.frame, textvariable=self.angle_var, 
                        font=("Arial", 14), width=10)
        entry.pack(pady=5)
        
        btn = tk.Button(self.frame, text="ONAYLA", font=("Arial", 12), 
                       command=lambda: confirm_callback(self.angle_var.get()))
        btn.pack(pady=5)
        
    def show(self):
        self.frame.place(x=1000, y=500, width=300, height=150)
        
    def hide(self):
        self.frame.place_forget()

class FEFrame:
    """Friend/Enemy (Dost/Düşman) gösterim frame'i"""
    def __init__(self, parent):
        self.frame = tk.LabelFrame(parent, text="Renk Bazlı Sınıflandırma", 
                                  bg="black", fg="limegreen", bd=2)
        
        lbl_friend = tk.Label(self.frame, text="Dost Rengi: MAVİ", 
                             font=("Arial",25), bg="black", fg="blue")
        lbl_enemy = tk.Label(self.frame, text="Düşman Rengi: KIRMIZI", 
                            font=("Arial",25), bg="black", fg="red")
        
        lbl_friend.pack(anchor="w", pady=5, padx=10)
        lbl_enemy.pack(anchor="w", pady=5, padx=10)
        
    def show(self):
        self.frame.place(x=1000, y=50, width=500, height=150)
        
    def hide(self):
        self.frame.place_forget()

class LetterFrame:
    """Angajman onay frame'i"""
    def __init__(self, parent, accept_callback):
        self.frame = tk.LabelFrame(parent, text="Angajman Onay", 
                                  bg="black", fg="dodgerblue", bd=2)
        
        self.letter_label = tk.Label(self.frame, text="Harf: —", 
                                    font=("Arial",28), fg="cyan", bg="black")
        self.shape_label = tk.Label(self.frame, text="Şekil: —", 
                                   font=("Arial",28), fg="orange", bg="black")
        self.btn_accept = tk.Button(self.frame, text="Angajmanı Kabul Et", 
                                   font=("Arial",16), command=accept_callback)
        
        self.letter_label.pack(pady=5)
        self.shape_label.pack(pady=5)
        self.btn_accept.pack(pady=10)
        
    def show(self):
        self.frame.place(x=1000, y=300, width=450, height=180)
        
    def hide(self):
        self.frame.place_forget()
        
    def update_display(self, letter, shape):
        """Harf ve şekil bilgisini güncelle"""
        self.letter_label.config(text=f"Harf: {letter}")
        self.shape_label.config(text=f"Şekil: {shape}")

# Mevcut kodlara ek olarak:

class EngagementPanel:
    """Angajman kontrol paneli"""
    def __init__(self, parent, engagement_controller):
        self.frame = tk.LabelFrame(parent, text="Angajman Kontrolü", 
                                  bg="black", fg="red", bd=2)
        self.controller = engagement_controller
        
        # Mühimmat göstergesi
        self.ammo_label = tk.Label(
            self.frame, text=f"Mühimmat: {self.controller.ammo_count}", 
            font=("Arial", 14), bg="black", fg="yellow"
        )
        self.ammo_label.pack(pady=5)
        
        # Angajman listesi
        self.engagement_list = tk.Listbox(
            self.frame, bg="black", fg="white",
            font=("Arial", 10), height=5
        )
        self.engagement_list.pack(pady=5, padx=5, fill="both")
        
        # Ateş butonu
        self.fire_button = tk.Button(
            self.frame, text="ATEŞ", font=("Arial", 16),
            bg="red", fg="white", command=self.fire_command
        )
        self.fire_button.pack(pady=10)
        
    def update_display(self):
        """Angajman bilgilerini güncelle"""
        self.ammo_label.config(text=f"Mühimmat: {self.controller.ammo_count}")
        
        self.engagement_list.delete(0, tk.END)
        for track_id, info in self.controller.engaged_targets.items():
            if info['status'] == 'active':
                text = f"ID:{track_id} - Atış:{info['shots_fired']}"
                self.engagement_list.insert(tk.END, text)
                
    def fire_command(self):
        """Manuel ateş komutu"""
        # En yüksek öncelikli hedefe ateş et
        # Bu kısım mode handler'da implement edilmeli
        pass
        
    def show(self):
        self.frame.place(x=1500, y=50, width=300, height=250)
        
    def hide(self):
        self.frame.place_forget()