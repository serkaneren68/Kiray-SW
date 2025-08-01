import tkinter as tk
from tkinter import messagebox


class ModeFrame:
    def __init__(self, parent, mode_var, on_mode_change, confirm_callback, reject_callback):
        self.frame = tk.Frame(parent, bg="#091009", highlightthickness=0, bd=0, width=904, height=80)
        self.mode_var = mode_var
        self.confirm_callback = confirm_callback
        self.reject_callback = reject_callback
        
        # Radio buttons
        for i, m in enumerate(["MANUEL", "MOD 1", "MOD 2", "MOD 3"]):
            tk.Radiobutton(
                self.frame,
                text=m,
                variable=self.mode_var,
                value=m,
                font=("Army Rust", 25),
                bg="#091009",
                fg="#8a7b55",
                selectcolor="#211e10"
            ).place(x=10 + i*235, y=5, width=180, height=35)
        
        # Onay butonları
        self.btn_ok = tk.Button(self.frame, text="✔", fg="green", bg="#8a7b55", font=("Arial",13), 
                               command=self.confirm_callback)
        self.btn_no = tk.Button(self.frame, text="✖", fg="red", bg="#8a7b55",  font=("Arial",13), 
                               command=self.reject_callback)
        self.btn_ok.place_forget()
        self.btn_no.place_forget()
        
        self.mode_var.trace_add("write", on_mode_change)
    
    def place(self, x, y):
        self.frame.place(x=x, y=y+5)
    
    def show_confirm_buttons(self, index):
        x0 = 35 + index * 236
        self.btn_ok.place(in_=self.frame, x=x0, y=45, width=60, height=20)
        self.btn_no.place(in_=self.frame, x=x0+65, y=45, width=60, height=20)
    
    def hide_confirm_buttons(self):
        self.btn_ok.place_forget()
        self.btn_no.place_forget()


class FriendEnemyFrame:
    def __init__(self, parent):
        self.frame = tk.LabelFrame(parent, text="", 
                                  bg="black", fg="limegreen", bd=0)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        lbl_friend = tk.Label(self.frame, text="ALLY COLOR: BLUE", 
                             font=("Army Rust",25), bg="black", fg="blue")
        lbl_enemy = tk.Label(self.frame, text="ENEMY COLOR: RED", 
                            font=("Army Rust",25), bg="black", fg="red")
        lbl_friend.grid(row=0, column=0, padx=30, pady=10, sticky="w")
        lbl_enemy.grid(row=0, column=1, padx=0, pady=10, sticky="w")

    
    def place(self, x, y, width, height):
        self.frame.place(x=x, y=y+250, width=width+275, height=height-65)
    
    def place_forget(self):
        self.frame.place_forget()


class LetterFrame:
    def __init__(self, parent, accept_callback):
        self.frame = tk.LabelFrame(parent, text="", 
                                  bg="black", fg="dodgerblue", bd=0)
        self.letter_label = tk.Label(self.frame, text="LETTER: —", 
                                   font=("Army Rust",30), fg="cyan", bg="black")
        self.shape_label = tk.Label(self.frame, text="SHAPE: —", 
                                   font=("Army Rust",30), fg="orange", bg="black")
        self.btn_accept = tk.Button(self.frame, text="APPLY", 
                                   font=("Army Rust",20), command=accept_callback)
        self.letter_label.pack(pady=5)
        self.shape_label.pack(pady=5)
        self.btn_accept.pack(pady=8)
    
    def update_letter(self, letter):
        self.letter_label.config(text=f"Harf: {letter}")
    
    def update_shape(self, shape):
        self.shape_label.config(text=f"Şekil: {shape}")
    
    def place(self, x, y, width, height):
        self.frame.place(x=x, y=y+145, width=width+280, height=height)
    
    def place_forget(self):
        self.frame.place_forget()


class RestrictedAreaFrame:
    def __init__(self, parent, set_ref_callback, confirm_callback):
        self.frame = tk.LabelFrame(parent, text="", 
                                  bg="black", fg="red", bd=0)
        
        # Referans noktası butonu
        self.btn_set_ref = tk.Button(self.frame, text="SET REFERENCE \nPOINT", 
                                    font=("Army Rust", 13), bg="blue", fg="white",
                                    command=set_ref_callback)
        self.btn_set_ref.place(x=420,y=50,width=120, height=50)
        
        # Mevcut açı göstergesi
        self.angle_label = tk.Label(self.frame, text="CURRENT ANGLE: 0°", 
                                   font=("Army Rust", 15), bg="black", fg="yellow")
        self.angle_label.place(x=10,y=60)
        
        # Yasaklı alan açı girişi
        input_frame = tk.Frame(self.frame, bg="black")
        input_frame.place(x=0, y=110, width=300, height=200)

        tk.Label(input_frame, text="RESTRICTED AREA", font=("Army Rust", 15), 
                bg="black", fg="white").place(x=15,y=0)
        
        # Min ve Max açı aynı satırda
        tk.Label(input_frame, text="Min:", font=("Army Rust", 12), 
                bg="black", fg="white").place(x=10,y=30)
        self.min_angle_var = tk.StringVar(value="-15")
        self.min_entry = tk.Entry(input_frame, textvariable=self.min_angle_var, 
                                 width=3, font=("Army Rust", 12))
        self.min_entry.place(x=40,y=30)
        tk.Label(input_frame, text="°", font=("Army Rust", 12), 
                bg="black", fg="white").place(x=60,y=30)
        
        tk.Label(input_frame, text="Max:", font=("Army Rust", 12), 
                bg="black", fg="white").place(x=90,y=30)
        self.max_angle_var = tk.StringVar(value="15")
        self.max_entry = tk.Entry(input_frame, textvariable=self.max_angle_var, 
                                 width=3, font=("Army Rust", 12))
        self.max_entry.place(x=120,y=30)
        tk.Label(input_frame, text="°", font=("Army Rust", 12), 
                bg="black", fg="white").place(x=140,y=30)
        
        # Onay butonu
        self.btn_confirm = tk.Button(self.frame, text="SET RESTRICTED \nAREA", 
                                    font=("Army Rust", 13), bg="red", fg="white",
                                    command=confirm_callback)
        self.btn_confirm.place(x=420,y=120,width=120, height=50)
        
        # Durum göstergesi
        self.status_label = tk.Label(self.frame, text="restricted Area: OFF", 
                                    font=("Army Rust", 9), bg="black", fg="orange")
        self.status_label.place(x=180,y=200)
        
        # Atış durumu göstergesi
        self.shot_status = tk.Label(self.frame, text="Fire not permitted!", 
                                   font=("Army Rust", 9), bg="black", fg="white")
        self.shot_status.place(x=300,y=200)
    
    def update_angle(self, angle):
        """Mevcut açıyı güncelle"""
        self.angle_label.config(text=f"CURRENT ANGLE: {angle:.1f}°")
        
    def update_shot_status(self, allowed, min_angle, max_angle):
        """Atış durumunu güncelle"""
        if allowed:
            self.shot_status.config(text="Fire permitted", fg="green")
        else:
            self.shot_status.config(text="Fire not permitted!", fg="red")
    
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
        self.frame.place(x=x, y=y-25, width=width+275, height=height-55)
    
    def place_forget(self):
        self.frame.place_forget()


import tkinter as tk

class CameraSelectionFrame:
    def __init__(self, parent, apply_callback):
        self.frame = tk.LabelFrame(parent, text="", 
                                  bg="black", fg="yellow", bd=0)
        self.apply_callback = apply_callback
        # Dönüşüm kontrolleri - sol tarafta
        transform_frame = tk.Frame(self.frame, bg="black")
        # 90° checkbox
        self.rotate_var = tk.BooleanVar(value=False)
        self.rotate_check = tk.Checkbutton(
            transform_frame, text="90°", variable=self.rotate_var,
            bg="black", fg="white", selectcolor="black",
            command=self.apply_callback, font=("Army Rust", 8)
        )
        self.rotate_check.grid(row=0, column=0, padx=2, pady=2)
        # Yatay flip
        self.flip_h_var = tk.BooleanVar(value=False)
        self.flip_h_check = tk.Checkbutton(
            transform_frame, text="HORIZONTAL", variable=self.flip_h_var,
            bg="black", fg="white", selectcolor="black",
            command=self.apply_callback, font=("Army Rust", 8)
        )
        self.flip_h_check.grid(row=1, column=0, padx=2, pady=2)
        # Dikey flip
        self.flip_v_var = tk.BooleanVar(value=False)
        self.flip_v_check = tk.Checkbutton(
            transform_frame, text="VERTICAL", variable=self.flip_v_var,
            bg="black", fg="white", selectcolor="black",
            command=self.apply_callback, font=("Army Rust", 8)
        )
        self.flip_v_check.grid(row=2, column=0, padx=2, pady=2)
        # 180° butonu
        self.rotate_180_btn = tk.Button(
            transform_frame, text="180°", command=self.rotate_180,
            bg="gray20", fg="white", font=("Army Rust", 8), width=4
        )
        self.rotate_180_btn.grid(row=3, column=0, padx=2, pady=6)
        transform_frame.grid(row=0, column=0, rowspan=2, sticky='nw', padx=5, pady=5)

        # Uygula butonu - sağ üst
        self.btn_apply = tk.Button(
            self.frame, text="APPLY", command=self.apply_and_defocus,
            bg="green", fg="white", font=("Army Rust", 9), width=12
        )
        self.btn_apply.grid(row=0, column=1, sticky='ne', padx=5, pady=5)

        # Kamera indeksi - sağ alt
        index_frame = tk.Frame(self.frame, bg="black")
        lbl = tk.Label(index_frame, text="CAMERA:", bg="black", fg="white", font=("Army Rust", 9))
        lbl.pack(side=tk.LEFT, padx=3)
        self.camera_var = tk.StringVar(value="0")
        self.camera_entry = tk.Entry(index_frame, textvariable=self.camera_var, width=3, font=("Army Rust", 9))
        self.camera_entry.pack(side=tk.LEFT, padx=3)
        index_frame.grid(row=1, column=1, sticky='se', padx=5, pady=5)

    def apply_and_defocus(self):
        # Call the original apply callback
        self.apply_callback()
        # Remove focus from the entry by setting it to the frame
        self.frame.focus_set()

    def rotate_180(self):
        """180 derece döndürme = hem yatay hem dikey aynalama"""
        # Toggle both horizontal and vertical flips
        if not (self.flip_h_var.get() and self.flip_v_var.get()):
            self.flip_h_var.set(True)
            self.flip_v_var.set(True)
        else:
            self.flip_h_var.set(False)
            self.flip_v_var.set(False)
        # Apply changes immediately
        self.apply_callback()

    def get_camera_index(self):
        return self.camera_var.get()

    def get_rotate_90(self):
        return self.rotate_var.get()

    def get_flip_horizontal(self):
        return self.flip_h_var.get()

    def get_flip_vertical(self):
        return self.flip_v_var.get()

    def place(self, x, y, width, height):
        self.frame.place(x=x-210, y=y+600, width=width-105, height=height-50)
