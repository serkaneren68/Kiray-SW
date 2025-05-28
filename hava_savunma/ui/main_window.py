"""
Ana pencere ve UI yönetimi
"""
import tkinter as tk
from tkinter import messagebox
import threading
from .components import (CanvasComponent, ModeFrame, ControlButtons, 
                        ManualControls, RestrictedAreaFrame, FEFrame, LetterFrame)
from detection.yolo_detector import YoloDetector
from utils.video_handler import VideoHandler
from modes import ManualMode, Mode1, Mode2, Mode3
import config

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
        # Durum değişkenleri
        self.running = False
        self.mode = tk.StringVar(value="Manuel")
        self.confirmed_mode = "Mod 1"
        self.video_thread = None
        
        # Tespit değişkenleri
        self.detected_shape = None
        self.confirmed_shape = None
        self.awaiting_confirmation = False
        self.detected_letter = None
        self.confirmed_letter = None
        self.restricted_angle = None
        
        # Bileşenleri oluştur
        self.create_components()
        
        # Detektörleri başlat
        self.yolo_detector = YoloDetector(config.MODEL_PATH)
        self.video_handler = VideoHandler()
        
        # Modları başlat
        self.init_modes()
        
    def setup_window(self):
        """Pencere ayarlarını yap"""
        self.root.title(config.WINDOW_TITLE)
        self.root.configure(bg=config.WINDOW_BG)
        self.root.geometry(config.WINDOW_SIZE)
        
    def create_components(self):
        """UI bileşenlerini oluştur"""
        # Canvas
        self.canvas_component = CanvasComponent(self.root)
        
        # Mod seçici
        self.mode_frame = ModeFrame(self.root, self.mode, self.confirm_mode, self.reject_mode)
        
        # Kontrol butonları
        self.controls = ControlButtons(self.root, self.start, self.stop, self.reset_system)
        
        # Manuel kontroller
        self.manual_controls = ManualControls(self.root, self.manual_command)
        
        # Yasaklı alan
        self.restricted_frame = RestrictedAreaFrame(self.root, self.confirm_restricted_angle)
        
        # FE (Friend/Enemy) frame
        self.fe_frame = FEFrame(self.root)
        
        # Letter frame
        self.letter_frame = LetterFrame(self.root, self.accept_engagement)
        
    def init_modes(self):
        """Modları başlat"""
        self.modes = {
            "Manuel": ManualMode(self),
            "Mod 1": Mode1(self),
            "Mod 2": Mode2(self),
            "Mod 3": Mode3(self)
        }
        
    def start(self):
        """Video yakalamayı başlat"""
        if not self.running:
            self.running = True
            self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
            self.video_thread.start()
            
    def stop(self):
        """Uygulamayı durdur"""
        self.running = False
        self.video_handler.release()
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join(timeout=2)
        print("Program durduruluyor...")
        self.root.after(0, self.root.destroy)
        
    def video_loop(self):
        """Ana video döngüsü"""
        self.video_handler.initialize()
        
        while self.running:
            frame = self.video_handler.read()
            if frame is None:
                continue
                
            # Aktif moda göre işle
            mode_handler = self.modes[self.confirmed_mode]
            processed_frame = mode_handler.process(frame)
            
            # Canvas'ı güncelle
            self.canvas_component.update_frame(processed_frame)
            
    def confirm_mode(self):
        """Mod değişikliğini onayla"""
        self.confirmed_mode = self.mode.get()
        self.mode_frame.hide_buttons()
        
        # Tüm frame'leri gizle
        self.fe_frame.hide()
        self.letter_frame.hide()
        self.manual_controls.hide()
        self.restricted_frame.hide()
        
        # Seçilen moda göre frame'leri göster
        if self.confirmed_mode == "Mod 2":
            self.fe_frame.show()
        elif self.confirmed_mode == "Mod 3":
            self.letter_frame.show()
            self.restricted_frame.show()
            self.reset_detection_state()
        elif self.confirmed_mode == "Manuel":
            self.manual_controls.show()
            
    def reject_mode(self):
        """Mod değişikliğini reddet"""
        self.mode.set(self.confirmed_mode)
        self.mode_frame.hide_buttons()
        
    def reset_system(self):
        """Sistemi sıfırla"""
        self.mode.set("Mod 1")
        self.confirm_mode()
        
    def reset_detection_state(self):
        """Tespit durumunu sıfırla"""
        self.awaiting_confirmation = False
        self.detected_letter = None
        self.confirmed_letter = None
        self.detected_shape = None
        self.confirmed_shape = None
        
    def manual_command(self, direction):
        """Manuel komutları işle"""
        commands = {
            "up": "Yukarı hareket et",
            "down": "Aşağı hareket et",
            "left": "Sola hareket et",
            "right": "Sağa hareket et",
            "shot": "Atış yap"
        }
        print(commands.get(direction, "Bilinmeyen komut"))
        
    def confirm_restricted_angle(self, angle):
        """Yasaklı açıyı onayla"""
        try:
            angle_float = float(angle)
            if 0 <= angle_float <= 360:
                self.restricted_angle = angle_float
                messagebox.showinfo("Onay", f"Atışa Yasaklı Alan: {angle_float} Derece olarak ayarlandı.")
            else:
                messagebox.showerror("Hata", "Lütfen 0 ile 360 arasında bir değer giriniz.")
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir sayı giriniz.")
            
    def accept_engagement(self):
        """Angajmanı kabul et"""
        if self.awaiting_confirmation and self.confirmed_letter and self.confirmed_shape:
            self.letter_frame.update_display(self.confirmed_letter, self.confirmed_shape)
            messagebox.showinfo(
                "Onay",
                f"Angajman: Harf:{self.confirmed_letter} Şekil:{self.confirmed_shape} KABUL EDİLDİ"
            )
            self.awaiting_confirmation = False