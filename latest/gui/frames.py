import tkinter as tk
from tkinter import messagebox


class ModeFrame:
    def __init__(self, parent, mode_var, on_mode_change, confirm_callback, reject_callback):
        self.frame = tk.Frame(parent, bg="black", width=800, height=120)
        self.mode_var = mode_var
        self.confirm_callback = confirm_callback
        self.reject_callback = reject_callback
        
        # Radio buttons
        for i, m in enumerate(["Manuel", "Mod 1", "Mod 2", "Mod 3"]):
            tk.Radiobutton(
                self.frame,
                text=m,
                variable=self.mode_var,
                value=m,
                font=("Arial", 14),
                bg="black",
                fg="white",
                selectcolor="black"
            ).place(x=10 + i*195, y=5, width=180, height=35)
        
        # Onay butonları
        self.btn_ok = tk.Button(self.frame, text="✔", fg="green", font=("Arial",18), 
                               command=self.confirm_callback)
        self.btn_no = tk.Button(self.frame, text="✖", fg="red", font=("Arial",18), 
                               command=self.reject_callback)
        self.btn_ok.place_forget()
        self.btn_no.place_forget()
        
        self.mode_var.trace_add("write", on_mode_change)
    
    def place(self, x, y):
        self.frame.place(x=x, y=y)
    
    def show_confirm_buttons(self, index):
        x0 = 10 + index * 195
        self.btn_ok.place(in_=self.frame, x=x0, y=50, width=85, height=30)
        self.btn_no.place(in_=self.frame, x=x0+95, y=50, width=85, height=30)
    
    def hide_confirm_buttons(self):
        self.btn_ok.place_forget()
        self.btn_no.place_forget()


class FriendEnemyFrame:
    def __init__(self, parent):
        self.frame = tk.LabelFrame(parent, text="Renk Bazlı Sınıflandırma", 
                                  bg="black", fg="limegreen", bd=2)
        lbl_friend = tk.Label(self.frame, text="Dost Rengi: MAVİ", 
                             font=("Arial",20), bg="black", fg="blue")
        lbl_enemy = tk.Label(self.frame, text="Düşman Rengi: KIRMIZI", 
                            font=("Arial",20), bg="black", fg="red")
        lbl_friend.pack(anchor="w", pady=8, padx=10)
        lbl_enemy.pack(anchor="w", pady=8, padx=10)
    
    def place(self, x, y, width, height):
        self.frame.place(x=x, y=y, width=width, height=height)
    
    def place_forget(self):
        self.frame.place_forget()


class LetterFrame:
    def __init__(self, parent, accept_callback):
        self.frame = tk.LabelFrame(parent, text="Angajman Onay", 
                                  bg="black", fg="dodgerblue", bd=2)
        self.letter_label = tk.Label(self.frame, text="Harf: —", 
                                   font=("Arial",22), fg="cyan", bg="black")
        self.shape_label = tk.Label(self.frame, text="Şekil: —", 
                                   font=("Arial",22), fg="orange", bg="black")
        self.btn_accept = tk.Button(self.frame, text="Angajmanı Kabul Et", 
                                   font=("Arial",14), command=accept_callback)
        self.letter_label.pack(pady=5)
        self.shape_label.pack(pady=5)
        self.btn_accept.pack(pady=8)
    
    def update_letter(self, letter):
        self.letter_label.config(text=f"Harf: {letter}")
    
    def update_shape(self, shape):
        self.shape_label.config(text=f"Şekil: {shape}")
    
    def place(self, x, y, width, height):
        self.frame.place(x=x, y=y, width=width, height=height)
    
    def place_forget(self):
        self.frame.place_forget()


class RestrictedAreaFrame:
    def __init__(self, parent, set_ref_callback, confirm_callback):
        self.frame = tk.LabelFrame(parent, text="Yasaklı Alan Kontrolü", 
                                  bg="black", fg="red", bd=2)
        
        # Referans noktası butonu
        self.btn_set_ref = tk.Button(self.frame, text="Referans Noktası\nAyarla (0°)", 
                                    font=("Arial", 10), bg="blue", fg="white",
                                    command=set_ref_callback, width=18, height=2)
        self.btn_set_ref.pack(pady=8, padx=8)
        
        # Mevcut açı göstergesi
        self.angle_label = tk.Label(self.frame, text="Mevcut Açı: 0°", 
                                   font=("Arial", 12, "bold"), bg="black", fg="yellow")
        self.angle_label.pack(pady=5)
        
        # Yasaklı alan açı girişi
        input_frame = tk.Frame(self.frame, bg="black")
        input_frame.pack(pady=5)
        
        tk.Label(input_frame, text="Yasaklı Alan:", font=("Arial", 10), 
                bg="black", fg="white").grid(row=0, column=0, columnspan=3, pady=5)
        
        # Min ve Max açı aynı satırda
        tk.Label(input_frame, text="Min:", font=("Arial", 9), 
                bg="black", fg="white").grid(row=1, column=0, padx=3)
        self.min_angle_var = tk.StringVar(value="-15")
        self.min_entry = tk.Entry(input_frame, textvariable=self.min_angle_var, 
                                 width=5, font=("Arial", 9))
        self.min_entry.grid(row=1, column=1)
        tk.Label(input_frame, text="°", font=("Arial", 9), 
                bg="black", fg="white").grid(row=1, column=2)
        
        tk.Label(input_frame, text="Max:", font=("Arial", 9), 
                bg="black", fg="white").grid(row=1, column=3, padx=3)
        self.max_angle_var = tk.StringVar(value="15")
        self.max_entry = tk.Entry(input_frame, textvariable=self.max_angle_var, 
                                 width=5, font=("Arial", 9))
        self.max_entry.grid(row=1, column=4)
        tk.Label(input_frame, text="°", font=("Arial", 9), 
                bg="black", fg="white").grid(row=1, column=5)
        
        # Onay butonu
        self.btn_confirm = tk.Button(self.frame, text="YASAKLI ALANI\nAYARLA", 
                                    font=("Arial", 10), bg="red", fg="white",
                                    command=confirm_callback, width=18, height=2)
        self.btn_confirm.pack(pady=8)
        
        # Durum göstergesi
        self.status_label = tk.Label(self.frame, text="Yasaklı alan: KAPALI", 
                                    font=("Arial", 9), bg="black", fg="orange")
        self.status_label.pack(pady=3)
        
        # Atış durumu göstergesi
        self.shot_status = tk.Label(self.frame, text="", 
                                   font=("Arial", 11, "bold"), bg="black", fg="white")
        self.shot_status.pack(pady=3)
    
    def update_angle(self, angle):
        """Mevcut açıyı güncelle"""
        self.angle_label.config(text=f"Mevcut Açı: {angle:.1f}°")
        
    def update_shot_status(self, allowed, min_angle, max_angle):
        """Atış durumunu güncelle"""
        if allowed:
            self.shot_status.config(text="ATIŞ İZNİ VAR", fg="green")
        else:
            self.shot_status.config(text="ATIŞ YASAK!", fg="red")
    
    def update_status(self, enabled, min_angle, max_angle):
        """Yasaklı alan durumunu güncelle"""
        if enabled:
            self.status_label.config(
                text=f"Yasaklı alan: AÇIK ({min_angle}° - {max_angle}°)", 
                fg="red"
            )
        else:
            self.status_label.config(text="Yasaklı alan: KAPALI", fg="orange")
    
    def get_angles(self):
        """Girilen açı değerlerini döndür"""
        try:
            min_angle = float(self.min_angle_var.get())
            max_angle = float(self.max_angle_var.get())
            return min_angle, max_angle
        except ValueError:
            return None, None
    
    def place(self, x, y, width, height):
        self.frame.place(x=x, y=y, width=width, height=height)
    
    def place_forget(self):
        self.frame.place_forget()


class CameraSelectionFrame:
    def __init__(self, parent, apply_callback):
        self.frame = tk.LabelFrame(parent, text="Kamera Ayarları", 
                                  bg="black", fg="yellow", bd=1)
        
        # Kamera indeksi
        index_frame = tk.Frame(self.frame, bg="black")
        index_frame.pack(pady=3)
        
        lbl = tk.Label(index_frame, text="Kamera:", bg="black", fg="white", font=("Arial", 9))
        lbl.pack(side=tk.LEFT, padx=3)
        
        self.camera_var = tk.StringVar(value="0")
        camera_entry = tk.Entry(index_frame, textvariable=self.camera_var, width=3, font=("Arial", 9))
        camera_entry.pack(side=tk.LEFT, padx=3)
        
        # Dönüşüm kontrolleri - kompakt grid
        transform_frame = tk.Frame(self.frame, bg="black")
        transform_frame.pack(pady=3)
        
        # Checkbox'ları küçült ve yan yana yerleştir
        self.rotate_var = tk.BooleanVar(value=False)
        self.rotate_check = tk.Checkbutton(
            transform_frame, 
            text="90°", 
            variable=self.rotate_var,
            bg="black", 
            fg="white",
            selectcolor="black",
            command=apply_callback,
            font=("Arial", 8)
        )
        self.rotate_check.grid(row=0, column=0, padx=2)
        
        self.flip_h_var = tk.BooleanVar(value=False)
        self.flip_h_check = tk.Checkbutton(
            transform_frame, 
            text="Yatay", 
            variable=self.flip_h_var,
            bg="black", 
            fg="white",
            selectcolor="black",
            command=apply_callback,
            font=("Arial", 8)
        )
        self.flip_h_check.grid(row=0, column=1, padx=2)
        
        self.flip_v_var = tk.BooleanVar(value=False)
        self.flip_v_check = tk.Checkbutton(
            transform_frame, 
            text="Dikey", 
            variable=self.flip_v_var,
            bg="black", 
            fg="white",
            selectcolor="black",
            command=apply_callback,
            font=("Arial", 8)
        )
        self.flip_v_check.grid(row=0, column=2, padx=2)
        
        # 180 derece butonu
        self.rotate_180_btn = tk.Button(
            transform_frame,
            text="180°",
            command=self.rotate_180,
            bg="gray20",
            fg="white",
            font=("Arial", 8),
            width=4
        )
        self.rotate_180_btn.grid(row=1, column=1, pady=3)
        
        # Uygula butonu
        btn_apply = tk.Button(self.frame, text="Uygula", command=apply_callback, 
                             bg="green", fg="white", font=("Arial", 9), width=12)
        btn_apply.pack(pady=3)
    
    def rotate_180(self):
        """180 derece döndürme = hem yatay hem dikey aynalama"""
        current_h = self.flip_h_var.get()
        current_v = self.flip_v_var.get()
        
        if not (current_h and current_v):
            self.flip_h_var.set(True)
            self.flip_v_var.set(True)
        else:
            self.flip_h_var.set(False)
            self.flip_v_var.set(False)
    
    def get_camera_index(self):
        return self.camera_var.get()
    
    def get_rotate_90(self):
        return self.rotate_var.get()
    
    def get_flip_horizontal(self):
        return self.flip_h_var.get()
    
    def get_flip_vertical(self):
        return self.flip_v_var.get()
    
    def place(self, x, y, width, height):
        self.frame.place(x=x, y=y, width=width, height=height)