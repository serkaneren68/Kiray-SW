import tkinter as tk


class ManualControls:
    def __init__(self, parent, command_callback):
        self.frame = tk.LabelFrame(parent, text="Manuel Kontroller", 
                                  bg="black", fg="yellow", bd=1)
        
        btn_up = tk.Button(self.frame, text="↑", font=("Arial", 28), width=3, height=1, 
                          command=lambda: command_callback("up"))
        btn_down = tk.Button(self.frame, text="↓", font=("Arial", 28), width=3, height=1, 
                            command=lambda: command_callback("down"))
        btn_left = tk.Button(self.frame, text="←", font=("Arial", 28), width=3, height=1, 
                            command=lambda: command_callback("left"))
        btn_right = tk.Button(self.frame, text="→", font=("Arial", 28), width=3, height=1, 
                             command=lambda: command_callback("right"))
        btn_shot = tk.Button(self.frame, text="ATIŞ", font=("Arial", 16), width=5, height=1, 
                            command=lambda: command_callback("shot"))
        btn_stop = tk.Button(self.frame, text="DUR", font=("Arial", 16), width=5, height=1, 
                            command=lambda: command_callback("stop"))
        
        btn_up.grid(row=0, column=1, pady=5)
        btn_left.grid(row=1, column=0, padx=5)
        btn_right.grid(row=1, column=2, padx=5)
        btn_down.grid(row=2, column=1, pady=5)
        btn_shot.grid(row=1, column=1, pady=5)
        btn_stop.grid(row=3, column=1, pady=5)
    
    def place(self, x, y, width, height):
        self.frame.place(x=x, y=y, width=width, height=height)
    
    def place_forget(self):
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
        self.frame.place(x=x, y=y, width=width, height=height)


class MainControls:
    def __init__(self, parent, start_callback, stop_callback, reset_callback):
        self.btn_start = tk.Button(parent, text="BAŞLAT", font=("Arial",14), 
                                  command=start_callback)
        self.btn_stop = tk.Button(parent, text="DURDUR", font=("Arial",14), 
                                 command=stop_callback)
        self.btn_reset = tk.Button(parent, text="RESET", font=("Arial",14), 
                                  bg="purple", fg="white", command=reset_callback)
    
    def place(self, x, y):
        self.btn_start.place(x=x, y=y, width=150, height=40)
        self.btn_stop.place(x=x+175, y=y, width=150, height=40)
        self.btn_reset.place(x=x+350, y=y, width=150, height=40)