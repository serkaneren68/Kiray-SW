import tkinter as tk
from tkinter import ttk


class ManualControls:
    def __init__(self, parent, command_callback):
        self.frame = tk.LabelFrame(parent, text="Manuel Kontroller", 
                                  bg="black", fg="yellow", bd=1)
        self.command_callback = command_callback
        self.continuous_movement = False
        self.current_direction = None
        
        # Hareket kontrolleri
        self.create_movement_controls()
        
        # Pozisyon göstergesi
        self.create_position_display()
        
        # Hareket modu seçimi
        self.create_movement_mode()
    
        #create_movement_controls metodunu güncelleyin
    def create_movement_controls(self):
        # Hareket butonları frame'i
        move_frame = tk.Frame(self.frame, bg="black")
        move_frame.grid(row=0, column=0, columnspan=3, pady=5)
        
        # Klavye kısayolları etiketi
        info_label = tk.Label(move_frame, text="Klavye: Yön tuşları | Space: Atış | ESC: Dur | Home: Başlangıç", 
                            bg="black", fg="yellow", font=("Arial", 9))
        info_label.grid(row=0, column=0, columnspan=3, pady=5)
        
        # Yukarı butonu (row değerlerini 1 artır)
        self.btn_up = tk.Button(move_frame, text="↑", font=("Arial", 28), 
                            width=3, height=1)
        self.btn_up.grid(row=1, column=1, pady=2)  # row=0 yerine row=1
        
        # Sol butonu
        self.btn_left = tk.Button(move_frame, text="←", font=("Arial", 28), 
                                width=3, height=1)
        self.btn_left.grid(row=2, column=0, padx=2)  # row=1 yerine row=2
        
        # Atış butonu (ortada)
        self.btn_shot = tk.Button(move_frame, text="ATIŞ", font=("Arial", 16), 
                                width=5, height=1, bg="red", fg="white",
                                command=lambda: self.command_callback("shot"))
        self.btn_shot.grid(row=2, column=1, pady=2)  # row=1 yerine row=2
        
        # Sağ butonu
        self.btn_right = tk.Button(move_frame, text="→", font=("Arial", 28), 
                                width=3, height=1)
        self.btn_right.grid(row=2, column=2, padx=2)  # row=1 yerine row=2
        
        # Aşağı butonu
        self.btn_down = tk.Button(move_frame, text="↓", font=("Arial", 28), 
                                width=3, height=1)
        self.btn_down.grid(row=3, column=1, pady=2)  # row=2 yerine row=3
        
        # Dur butonu
        self.btn_stop = tk.Button(move_frame, text="DUR", font=("Arial", 16), 
                                width=5, height=1, bg="orange",
                                command=self.stop_all)
        self.btn_stop.grid(row=4, column=1, pady=5)  # row=3 yerine row=4
        
        # Buton event'lerini bağla
        self.bind_button_events()
    
    
    def create_position_display(self):
        # Pozisyon göstergesi frame'i
        pos_frame = tk.LabelFrame(self.frame, text="Mevcut Pozisyon", 
                                 bg="black", fg="lime", bd=1)
        pos_frame.grid(row=2, column=0, columnspan=3, pady=5, padx=5, sticky="ew")
        
        # Yaw (Yatay) pozisyon
        tk.Label(pos_frame, text="Yatay:", bg="black", fg="white", 
                font=("Arial", 10)).grid(row=0, column=0, padx=5)
        self.yaw_pos_label = tk.Label(pos_frame, text="0°", bg="black", 
                                     fg="cyan", font=("Arial", 11, "bold"))
        self.yaw_pos_label.grid(row=0, column=1, padx=5)
        
        # Pitch (Dikey) pozisyon
        tk.Label(pos_frame, text="Dikey:", bg="black", fg="white", 
                font=("Arial", 10)).grid(row=1, column=0, padx=5)
        self.pitch_pos_label = tk.Label(pos_frame, text="0°", bg="black", 
                                       fg="cyan", font=("Arial", 11, "bold"))
        self.pitch_pos_label.grid(row=1, column=1, padx=5)
        
        # Home butonu
        self.btn_home = tk.Button(pos_frame, text="HOME", font=("Arial", 10), 
                                 bg="green", fg="white", width=8,
                                 command=self.go_home)
        self.btn_home.grid(row=0, column=2, rowspan=2, padx=10)
    
    def create_movement_mode(self):
        # Hareket modu frame'i
        mode_frame = tk.LabelFrame(self.frame, text="Hareket Modu", 
                                  bg="black", fg="yellow", bd=1)
        mode_frame.grid(row=3, column=0, columnspan=3, pady=10, padx=5, sticky="ew")
        
        self.movement_mode = tk.StringVar(value="step")
        
        # Adım adım hareket
        tk.Radiobutton(mode_frame, text="Adım", variable=self.movement_mode, 
                      value="step", bg="black", fg="white", 
                      selectcolor="black").grid(row=0, column=0, padx=5)
        
        # Sürekli hareket
        tk.Radiobutton(mode_frame, text="Sürekli", variable=self.movement_mode, 
                      value="continuous", bg="black", fg="white", 
                      selectcolor="black").grid(row=0, column=1, padx=5)
        
        # Adım büyüklüğü
        tk.Label(mode_frame, text="Adım:", bg="black", fg="white", 
                font=("Arial", 10)).grid(row=1, column=0, padx=5)
        
        self.step_size = tk.StringVar(value="10")
        step_entry = tk.Entry(mode_frame, textvariable=self.step_size, 
                             width=5, font=("Arial", 10))
        step_entry.grid(row=1, column=1, padx=5)
        
        tk.Label(mode_frame, text="derece", bg="black", fg="white", 
                font=("Arial", 10)).grid(row=1, column=2, padx=2)
    
    def bind_button_events(self):
        # Hareket butonlarına event bağla
        buttons = {
            self.btn_up: "up",
            self.btn_down: "down",
            self.btn_left: "left",
            self.btn_right: "right"
        }
        
        for btn, direction in buttons.items():
            btn.bind('<ButtonPress-1>', lambda e, d=direction: self.start_movement(d))
            btn.bind('<ButtonRelease-1>', lambda e, d=direction: self.stop_movement(d))
    
    # start_movement metodunu güncelleyin
    def start_movement(self, direction):
        # Butonu vurgula
        button_map = {
            'up': self.btn_up,
            'down': self.btn_down,
            'left': self.btn_left,
            'right': self.btn_right
        }
        
        if direction in button_map:
            button_map[direction].config(relief=tk.SUNKEN, bg="lightgreen")
        
        if self.movement_mode.get() == "continuous":
            self.continuous_movement = True
            self.current_direction = direction
            self.continuous_move()
        else:
            # Adım adım hareket
            self.send_step_command(direction)

    # stop_movement metodunu güncelleyin
    def stop_movement(self, direction):
        # Buton vurgusunu kaldır
        button_map = {
            'up': self.btn_up,
            'down': self.btn_down,
            'left': self.btn_left,
            'right': self.btn_right
        }
        
        if direction in button_map:
            button_map[direction].config(relief=tk.RAISED, bg="SystemButtonFace")
        
        if self.movement_mode.get() == "continuous":
            self.continuous_movement = False
            self.command_callback("stop")
    
    def continuous_move(self):
        if self.continuous_movement and self.current_direction:
            self.command_callback(self.current_direction)
            # Daha sık komut gönder (50ms yerine)
            self.frame.after(50, self.continuous_move)

    def stop_movement(self, direction):
        # Buton vurgusunu kaldır
        button_map = {
            'up': self.btn_up,
            'down': self.btn_down,
            'left': self.btn_left,
            'right': self.btn_right
        }
        
        if direction in button_map:
            button_map[direction].config(relief=tk.RAISED, bg="SystemButtonFace")
        
        # Her zaman dur komutu gönder
        self.continuous_movement = False
        self.command_callback("stop")
    
    def send_step_command(self, direction):
        # Adım büyüklüğü ile birlikte komut gönder
        step_size = self.step_size.get()
        command = f"{direction}:{step_size}"  # Örn: "right:50"
        print(f"[KONTROL] Gönderilen komut: {command}")  # Debug için ekleyin
        self.command_callback(command)
    
    def stop_all(self):
        self.continuous_movement = False
        self.command_callback("stop")
    
    def update_speed(self, value):
        speed = int(float(value))
        self.speed_label.config(text=f"{speed}%")
        # Hız bilgisini gönder
        self.command_callback(f"speed:{speed}")
    
    def go_home(self):
        self.command_callback("home")
        self.yaw_pos_label.config(text="0°")
        self.pitch_pos_label.config(text="0°")
    
    # ManualControls sınıfında update_position metodunu güncelleyin:
    def update_position(self, yaw, pitch):
        """Pozisyon güncellemesi için dışarıdan çağrılabilir"""
        # Yaw değeri artık referans noktasına göre gösteriliyor
        self.yaw_pos_label.config(text=f"{yaw:.1f}°")
        self.pitch_pos_label.config(text=f"{pitch:.1f}°")
    
    def place(self, x, y, width, height):
        # Frame'i yerleştir
        self.frame.place(x=x+320, y=y+220, width=width+60, height=height+200)
        
        # Kompakt yerleşim için iç elemanları yeniden düzenle
        # Hareket kontrolleri frame'i
        move_frame = self.frame.winfo_children()[0]  # İlk child hareket frame'i
        move_frame.place(x=5, y=5, width=width+80, height=580)

        # Pozisyon göstergesi frame'i
        pos_frame = None
        for child in self.frame.winfo_children():
            if isinstance(child, tk.LabelFrame) and "Mevcut Pozisyon" in child.cget("text"):
                pos_frame = child
                break
        
        if pos_frame:
            pos_frame.place(x=5, y=805, width=width-10, height=80)
        
        # Hareket modu frame'i (varsa)
        mode_frame = None
        for child in self.frame.winfo_children():
            if isinstance(child, tk.LabelFrame) and "Hareket Modu" in child.cget("text"):
                mode_frame = child
                break
        
        if mode_frame:
            # Eğer height yeterli değilse bu frame'i gizle
            if height > 350:
                mode_frame.place(x=5, y=280, width=width-10, height=70)
            else:
                mode_frame.place_forget()

    def place_forget(self):
        self.continuous_movement = False  # Gizlerken hareketi durdur
        self.frame.place_forget()


class TrackingControls:
    def __init__(self, parent, toggle_callback):
        self.frame = tk.LabelFrame(parent, text="Otomatik Takip", 
                                  bg="black", fg="cyan", bd=1)
        self.tracking_btn = tk.Button(
            self.frame, 
            text="TAKİBİ BAŞLAT", 
            font=("Arial", 14),
            command=toggle_callback
        )
        self.tracking_btn.pack(pady=10, padx=20)
    
    def update_button(self, enabled):
        if enabled:
            self.tracking_btn.config(text="TAKİBİ DURDUR", bg="red")
        else:
            self.tracking_btn.config(text="TAKİBİ BAŞLAT", bg="SystemButtonFace")
    
    def place(self, x, y, width, height):
        self.frame.place(x=x-600, y=y+175, width=width, height=height)


class MainControls:
    def __init__(self, parent, start_callback, stop_callback, reset_callback):
        self.btn_start = tk.Button(parent, text="BAŞLAT", font=("Arial",14), 
                                  command=start_callback)
        self.btn_stop = tk.Button(parent, text="DURDUR", font=("Arial",14), 
                                 command=stop_callback)
        self.btn_reset = tk.Button(parent, text="RESET", font=("Arial",14), 
                                  bg="purple", fg="white", command=reset_callback)
    
    def place(self, x, y):
        self.btn_start.place(x=x, y=y-20, width=150, height=40)
        self.btn_stop.place(x=x, y=y+35, width=150, height=40)
        self.btn_reset.place(x=x, y=y+90, width=150, height=40)