import tkinter as tk
from tkinter import messagebox


class ModeFrame:
    def __init__(self, parent, mode_var, on_mode_change, confirm_callback, reject_callback):
        self.frame = tk.Frame(parent, bg="black", width=900, height=140)
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
                font=("Arial", 16),
                bg="black",
                fg="white",
                selectcolor="black"
            ).place(x=0 + i*175, y=5, width=150, height=40)
        
        # Onay butonları
        self.btn_ok = tk.Button(self.frame, text="✔", fg="green", font=("Arial",20), 
                               command=self.confirm_callback)
        self.btn_no = tk.Button(self.frame, text="✖", fg="red", font=("Arial",20), 
                               command=self.reject_callback)
        self.btn_ok.place_forget()
        self.btn_no.place_forget()
        
        self.mode_var.trace_add("write", on_mode_change)
    
    def place(self, x, y):
        self.frame.place(x=x, y=y)
    
    def show_confirm_buttons(self, index):
        x0 = index * 175
        self.btn_ok.place(in_=self.frame, x=x0, y=60, width=70, height=30)
        self.btn_no.place(in_=self.frame, x=x0+80, y=60, width=70, height=30)
    
    def hide_confirm_buttons(self):
        self.btn_ok.place_forget()
        self.btn_no.place_forget()


class FriendEnemyFrame:
    def __init__(self, parent):
        self.frame = tk.LabelFrame(parent, text="Renk Bazlı Sınıflandırma", 
                                  bg="black", fg="limegreen", bd=2)
        lbl_friend = tk.Label(self.frame, text="Dost Rengi: MAVİ", 
                             font=("Arial",25), bg="black", fg="blue")
        lbl_enemy = tk.Label(self.frame, text="Düşman Rengi: KIRMIZI", 
                            font=("Arial",25), bg="black", fg="red")
        lbl_friend.pack(anchor="w", pady=5, padx=10)
        lbl_enemy.pack(anchor="w", pady=5, padx=10)
    
    def place(self, x, y, width, height):
        self.frame.place(x=x, y=y, width=width, height=height)
    
    def place_forget(self):
        self.frame.place_forget()


class LetterFrame:
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
    
    def update_letter(self, letter):
        self.letter_label.config(text=f"Harf: {letter}")
    
    def update_shape(self, shape):
        self.shape_label.config(text=f"Şekil: {shape}")
    
    def place(self, x, y, width, height):
        self.frame.place(x=x, y=y, width=width, height=height)
    
    def place_forget(self):
        self.frame.place_forget()


class RestrictedAreaFrame:
    def __init__(self, parent, confirm_callback):
        self.frame = tk.LabelFrame(parent, text="Atışa Yasaklı Alan", 
                                  bg="black", fg="orange", bd=2)
        lbl = tk.Label(self.frame, text="Açı (0-360):", 
                      font=("Arial", 14), bg="black", fg="white")
        lbl.pack(pady=5)

        self.restricted_angle_var = tk.StringVar()
        entry = tk.Entry(self.frame, textvariable=self.restricted_angle_var, 
                        font=("Arial", 14), width=10)
        entry.pack(pady=5)

        btn = tk.Button(self.frame, text="ONAYLA", font=("Arial", 12), 
                       command=confirm_callback)
        btn.pack(pady=5)
    
    def get_angle(self):
        return self.restricted_angle_var.get()
    
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
        index_frame.pack(pady=5)
        
        lbl = tk.Label(index_frame, text="Kamera İndeksi:", bg="black", fg="white")
        lbl.pack(side=tk.LEFT, padx=5)
        
        self.camera_var = tk.StringVar(value="0")
        camera_entry = tk.Entry(index_frame, textvariable=self.camera_var, width=5)
        camera_entry.pack(side=tk.LEFT, padx=5)
        
        # Dönüşüm kontrolleri
        transform_frame = tk.Frame(self.frame, bg="black")
        transform_frame.pack(pady=5)
        
        # 90 derece döndürme checkbox
        self.rotate_var = tk.BooleanVar(value=False)
        self.rotate_check = tk.Checkbutton(
            transform_frame, 
            text="90° Döndür", 
            variable=self.rotate_var,
            bg="black", 
            fg="white",
            selectcolor="black",
            command=apply_callback
        )
        self.rotate_check.grid(row=0, column=0, padx=5, pady=2)
        
        # Yatay aynalama checkbox
        self.flip_h_var = tk.BooleanVar(value=False)
        self.flip_h_check = tk.Checkbutton(
            transform_frame, 
            text="Yatay Aynala", 
            variable=self.flip_h_var,
            bg="black", 
            fg="white",
            selectcolor="black",
            command=apply_callback
        )
        self.flip_h_check.grid(row=0, column=1, padx=5, pady=2)
        
        # Dikey aynalama checkbox
        self.flip_v_var = tk.BooleanVar(value=False)
        self.flip_v_check = tk.Checkbutton(
            transform_frame, 
            text="Dikey Aynala", 
            variable=self.flip_v_var,
            bg="black", 
            fg="white",
            selectcolor="black",
            command=apply_callback
        )
        self.flip_v_check.grid(row=1, column=0, padx=5, pady=2)
        
        # 180 derece döndürme kısayolu
        self.rotate_180_btn = tk.Button(
            transform_frame,
            text="180° Döndür",
            command=self.rotate_180,
            bg="gray20",
            fg="white",
            font=("Arial", 9)
        )
        self.rotate_180_btn.grid(row=1, column=1, padx=5, pady=2)
        
        # Uygula butonu
        btn_apply = tk.Button(self.frame, text="Uygula", command=apply_callback, 
                             bg="green", fg="white", font=("Arial", 10, "bold"))
        btn_apply.pack(pady=5)
    
    def rotate_180(self):
        """180 derece döndürme = hem yatay hem dikey aynalama"""
        current_h = self.flip_h_var.get()
        current_v = self.flip_v_var.get()
        
        # Her ikisi de kapalıysa veya sadece biri açıksa, her ikisini de aç
        if not (current_h and current_v):
            self.flip_h_var.set(True)
            self.flip_v_var.set(True)
        else:
            # Her ikisi de açıksa, kapat
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