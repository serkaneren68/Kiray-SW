import tkinter as tk
from tkinter import ttk

class ManualControls:
    def __init__(self, parent, command_callback):
        self.frame = tk.LabelFrame(parent, text="", 
                                  bg="black", fg="yellow", bd=0)
        self.command_callback = command_callback
        self.continuous_movement = False
        self.current_direction = None
        
        # Hareket kontrolleri
        self.create_movement_controls()
        
        # Hız kontrolü
        # self.create_speed_control()
        
        # Pozisyon göstergesi
        self.create_position_display()
        
        # Hareket modu seçimi
        self.create_movement_mode()
    
    def create_movement_controls(self):
        # Hareket butonları frame'i
        move_frame = tk.Frame(self.frame, bg="black")
        move_frame.grid(row=0, column=0, columnspan=3, pady=5, sticky="ew")
        
        # Klavye kısayolları etiketi
        info_label = tk.Label(move_frame, text="Klavye: Yön tuşları | Space: Atış | ESC: Dur | Home: Başlangıç", 
                            bg="black", fg="yellow", font=("Arial", 9))
        info_label.grid(row=0, column=0, columnspan=4, pady=5, sticky="w")
        
        # Butonlar için sağa hizalı frame
        buttons_container = tk.Frame(move_frame, bg="black")
        buttons_container.grid(row=1, column=0, columnspan=4, sticky="e")
        
        # Yukarı butonu
        self.btn_up = tk.Button(buttons_container, text="↑", font=("Arial", 28), 
                            width=3, height=1)
        self.btn_up.grid(row=0, column=1, pady=2)
        
        # Sol butonu
        self.btn_left = tk.Button(buttons_container, text="←", font=("Arial", 28), 
                                width=3, height=1)
        self.btn_left.grid(row=1, column=0, padx=2)
        
        # Atış butonu (ortada)
        self.btn_shot = tk.Button(buttons_container, text="ATIŞ", font=("Arial", 16), 
                                width=5, height=1, bg="red", fg="white",
                                command=lambda: self.command_callback("shot"))
        self.btn_shot.grid(row=1, column=1, pady=2)
        
        # Sağ butonu
        self.btn_right = tk.Button(buttons_container, text="→", font=("Arial", 28), 
                                width=3, height=1)
        self.btn_right.grid(row=1, column=2, padx=10)
        
        # Aşağı butonu
        self.btn_down = tk.Button(buttons_container, text="↓", font=("Arial", 28), 
                                width=3, height=1)
        self.btn_down.grid(row=2, column=1, pady=2)
        
        # Dur butonu
        self.btn_stop = tk.Button(buttons_container, text="DUR", font=("Arial", 16), 
                                width=5, height=1, bg="orange",
                                command=self.stop_all)
        self.btn_stop.grid(row=3, column=1, pady=5)
        
        # Buton event'lerini bağla
        self.bind_button_events()
        
        # Sağa hizala
        buttons_container.columnconfigure(0, weight=1)
        move_frame.columnconfigure(0, weight=1)

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
        mode_frame.grid(row=3, column=0, columnspan=3, pady=5, padx=5, sticky="ew")
        
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
    
    def continuous_move(self):
        if self.continuous_movement and self.current_direction:
            self.command_callback(self.current_direction)
            # Daha sık komut gönder (50ms yerine)
            self.frame.after(50, self.continuous_move)
    
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
    
    def update_position(self, yaw, pitch):
        """Pozisyon güncellemesi için dışarıdan çağrılabilir"""
        # Yaw değeri artık referans noktasına göre gösteriliyor
        self.yaw_pos_label.config(text=f"{yaw:.1f}°")
        self.pitch_pos_label.config(text=f"{pitch:.1f}°")
    
    def place(self, x, y, width, height):
        # Frame'i yerleştir
        self.frame.place(x=940, y=y, width=572, height=300)
        
        # Kompakt yerleşim için iç elemanları yeniden düzenle
        # Hareket kontrolleri frame'i
        move_frame = self.frame.winfo_children()[0]  # İlk child hareket frame'i
        move_frame.place(x=5, y=5, width=570, height=300)
        
        # Pozisyon göstergesi frame'i
        pos_frame = None
        for child in self.frame.winfo_children():
            if isinstance(child, tk.LabelFrame) and "Mevcut Pozisyon" in child.cget("text"):
                pos_frame = child
                break
        
        if pos_frame:
            pos_frame.place(x=5, y=195, width=width-10, height=80)
        
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
        self.frame = tk.LabelFrame(parent, text="", 
                                  bg="#091009", fg="cyan", bd=0)
        self.tracking_btn = tk.Button(
            self.frame, 
            text="Start Tracking", 
            highlightthickness=1,
            bd=1,
            relief="raised",
            bg="#091009",
            fg="white",
            font=("Army Rust", 14),
            command=toggle_callback
        )
        self.tracking_btn.place(x=20, y=25, width=140, height=80)
    
    def update_button(self, enabled):
        if enabled:
            self.tracking_btn.config(text="Stop Tracking", bg="#41210f")
        else:
            self.tracking_btn.config(text="Start Tracking", bg="#091009")
    
    def place(self, x, y, width, height):
        self.frame.place(x=x-30, y=y+20, width=width-120, height=height+22)


class MainControls:
    def __init__(self, parent, start_callback, stop_callback, reset_callback):
        self.panel_frame = tk.Frame(parent, bg="#091009", width=270, height=120, bd=2, relief="sunken")
        self.canvas = tk.Canvas(parent, width=270, height=120, bg="#091009", highlightthickness=0)

        self.btn_start_oval = self.canvas.create_oval(20, 20, 100, 100, fill="#091009", outline="white")
        self.btn_start_text = self.canvas.create_text(60, 60, text="START", fill="white", font=("Army Rust", 20))
        self.canvas.tag_bind(self.btn_start_oval, "<Button-1>", lambda e: start_callback())
        self.canvas.tag_bind(self.btn_start_text, "<Button-1>", lambda e: start_callback())

        self.btn_stop_oval = self.canvas.create_oval(160, 20, 240, 100, fill="#41210f", outline="white")
        self.btn_stop_text = self.canvas.create_text(200, 60, text="STOP", fill="white", font=("Army Rust", 20))
        self.canvas.tag_bind(self.btn_stop_oval, "<Button-1>", lambda e: stop_callback())
        self.canvas.tag_bind(self.btn_stop_text, "<Button-1>", lambda e: stop_callback())

        # RESET köşeleri yuvarlatılmış dikdörtgen
        self.btn_reset_rect = round_rectangle(self.canvas, 100, 90, 160, 110, radius=15, fill="purple", outline="white")
        self.btn_reset_text = self.canvas.create_text(130, 100, text="RESET", fill="white", font=("Army Rust", 15))
        self.canvas.tag_bind(self.btn_reset_rect, "<Button-1>", lambda e: reset_callback())
        self.canvas.tag_bind(self.btn_reset_text, "<Button-1>", lambda e: reset_callback())

    def place(self, x, y):
        self.panel_frame.place(x=x, y=y-30)
        self.canvas.place(x=x, y=y-30)

def round_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    points = [
        x1+radius, y1,
        x2-radius, y1,
        x2, y1,
        x2, y1+radius,
        x2, y2-radius,
        x2, y2,
        x2-radius, y2,
        x1+radius, y2,
        x1, y2,
        x1, y2-radius,
        x1, y1+radius,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

