# calibration_test.py (modular klasöründe)
import sys
import os
import tkinter as tk

# Path ayarlaması gerek yok çünkü ana klasördeyiz
from arduino.arduino_controller import ArduinoController

from config.constants import ARDUINO_COMMANDS, STEPS_PER_DEGREE_YAW, STEPS_PER_DEGREE_PITCH

class CalibrationTool:
    def __init__(self):
        self.arduino = ArduinoController()
        self.step_size = 10
        
        # GUI oluştur
        self.root = tk.Tk()
        self.root.title("Motor Kalibrasyon Aracı")
        self.root.geometry("400x350")
        self.root.configure(bg="lightgray")
        
        # Başlık
        title = tk.Label(self.root, text="MOTOR KALİBRASYON ARACI", 
                        font=("Arial", 16, "bold"), bg="lightgray")
        title.pack(pady=10)
        
        # Adım büyüklüğü kontrolü
        step_frame = tk.Frame(self.root, bg="lightgray")
        step_frame.pack(pady=10)
        
        tk.Label(step_frame, text="Adım Sayısı:", bg="lightgray", 
                font=("Arial", 12)).pack(side=tk.LEFT)
        self.step_var = tk.StringVar(value="10")
        step_entry = tk.Entry(step_frame, textvariable=self.step_var, 
                             width=10, font=("Arial", 12))
        step_entry.pack(side=tk.LEFT, padx=5)
        
        # Yön butonları
        button_frame = tk.Frame(self.root, bg="lightgray")
        button_frame.pack(pady=20)
        
        # Buton stili
        btn_style = {
            'font': ("Arial", 20),
            'width': 3,
            'height': 1
        }
        
        tk.Button(button_frame, text="↑", command=lambda: self.move(0, 1), 
                 **btn_style).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(button_frame, text="←", command=lambda: self.move(-1, 0), 
                 **btn_style).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(button_frame, text="•", bg="red", fg="white",
                 **btn_style).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(button_frame, text="→", command=lambda: self.move(1, 0), 
                 **btn_style).grid(row=1, column=2, padx=5, pady=5)
        tk.Button(button_frame, text="↓", command=lambda: self.move(0, -1), 
                 **btn_style).grid(row=2, column=1, padx=5, pady=5)
        
        # Kontrol butonları
        control_frame = tk.Frame(self.root, bg="lightgray")
        control_frame.pack(pady=10)
        
        tk.Button(control_frame, text="HOME", command=self.home, 
                 bg="green", fg="white", font=("Arial", 12),
                 width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="STOP", command=self.stop, 
                 bg="orange", fg="white", font=("Arial", 12),
                 width=10).pack(side=tk.LEFT, padx=5)
        
        # Bilgi etiketi
        self.info_label = tk.Label(self.root, text="Hazır", fg="blue",
                                  bg="lightgray", font=("Arial", 10))
        self.info_label.pack(pady=10)
        
        # Kapatma eventi
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def move(self, x_dir, y_dir):
        try:
            steps = int(self.step_var.get())
            yaw_steps = x_dir * steps
            pitch_steps = y_dir * steps
            
            # Arduino'ya gönder
            self.arduino.send_direct_movement(yaw_steps, pitch_steps)
            
            direction = ""
            if x_dir == 1: direction = "SAĞ"
            elif x_dir == -1: direction = "SOL"
            elif y_dir == 1: direction = "YUKARI"
            elif y_dir == -1: direction = "AŞAĞI"
            
            self.info_label.config(
                text=f"{direction}: Yaw={yaw_steps}, Pitch={pitch_steps} adım"
            )
        except ValueError:
            self.info_label.config(text="Hata: Geçerli bir sayı girin!", fg="red")
    
    def home(self):
        self.arduino.send_command("home")
        self.info_label.config(text="Home pozisyonuna dönülüyor...", fg="green")
    
    def stop(self):
        self.arduino.send_command("stop")
        self.info_label.config(text="Motorlar durduruldu", fg="orange")
    
    def on_close(self):
        if self.arduino:
            self.arduino.close()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    print("Motor Kalibrasyon Aracı Başlatılıyor...")
    print("="*40)
    print("KULLANIM:")
    print("1. Adım sayısını girin")
    print("2. Ok tuşlarıyla test edin")
    print("3. Kaç derece döndüğünü ölçün")
    print("4. constants.py'de STEPS_PER_DEGREE değerini ayarlayın")
    print("="*40)
    
    tool = CalibrationTool()
    tool.run()