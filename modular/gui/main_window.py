import tkinter as tk
from PIL import Image, ImageTk
import cv2
import threading
import time
from tkinter import messagebox

from config.constants import *
from gui.frames import *
from gui.controls import ManualControls, TrackingControls, MainControls
from camera.camera_manager import CameraManager
from arduino.arduino_controller import ArduinoController
from detection.object_detector import ObjectDetector
from detection.qr_detector import QRDetector
from utils.helpers import add_crosshair


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Hava Savunma Kontrol Paneli")
        self.root.configure(bg="black")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        
        # Durum değişkenleri
        self.running = False
        self.video_thread = None
        self.detected_shape = None
        self.confirmed_shape = None
        self.awaiting_confirmation = False
        self.detected_letter = None
        self.confirmed_letter = None
        self.restricted_angle = None
        self.tracking_enabled = False
        self.camera_index = 0
        
        # Mod durumu
        self.mode = tk.StringVar(value="Manuel")
        self.confirmed_mode = "Mod 1"
        
        # Bileşenler
        self.camera_manager = CameraManager(self.camera_index)
        self.arduino_controller = ArduinoController()
        self.object_detector = ObjectDetector()
        self.qr_detector = QRDetector()
        
        # UI oluştur
        self._setup_ui()
    
    def _setup_ui(self):
        # Canvas
        self.canvas = tk.Canvas(self.root, bg="black", width=CANVAS_WIDTH, 
                               height=CANVAS_HEIGHT, highlightthickness=2, 
                               highlightbackground="gray")
        self.canvas.place(x=30, y=30)
        
        # Frame'ler
        self.mode_frame = ModeFrame(self.root, self.mode, self.on_mode_change,
                                   self.confirm_mode, self.reject_mode)
        self.mode_frame.place(30, 580)
        
        self.fe_frame = FriendEnemyFrame(self.root)
        self.letter_frame = LetterFrame(self.root, self.accept_engagement)
        self.restricted_area_frame = RestrictedAreaFrame(self.root, self.confirm_restricted_angle)
        self.camera_frame = CameraSelectionFrame(self.root, self.apply_camera_index)
        self.camera_frame.place(600, 580, 300, 100)
        
        # Kontroller
        self.manual_controls = ManualControls(self.root, self.manual_command)
        self.tracking_controls = TrackingControls(self.root, self.toggle_tracking)
        self.tracking_controls.place(1000, 700, 200, 100)
        
        self.main_controls = MainControls(self.root, self.start, self.stop, self.reset_system)
        self.main_controls.place(30, 700)

        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.bind('<KeyRelease>', self.on_key_release)
        
        # Aktif tuşları takip et
        self.pressed_keys = set()
    
    def on_key_press(self, event):
        """Klavye tuşuna basıldığında"""
        if self.confirmed_mode != "Manuel":
            return
        
        key = event.keysym
    
        # Tuş zaten basılıysa tekrar gönderme
        if key in self.pressed_keys:
            return
        
        self.pressed_keys.add(key)
        
        # Yön tuşları kontrolü
        if hasattr(self, 'manual_controls'):
            if key == 'Up':
                self.manual_controls.start_movement('up')
            elif key == 'Down':
                self.manual_controls.start_movement('down')
            elif key == 'Left':
                self.manual_controls.start_movement('left')
            elif key == 'Right':
                self.manual_controls.start_movement('right')
            elif key == 'space':  # Space tuşu atış için
                self.manual_command('shot')
            elif key == 'Escape':  # ESC tuşu durdurma için
                self.manual_command('stop')
            elif key == 'Home':  # Home tuşu
                self.manual_command('home')

    def on_key_release(self, event):
        """Klavye tuşu bırakıldığında"""
        if self.confirmed_mode != "Manuel":
            return
        
        key = event.keysym
        
        # Tuşu basılı listesinden çıkar
        self.pressed_keys.discard(key)
        
        # Yön tuşları bırakıldığında dur
        if hasattr(self, 'manual_controls'):
            if key in ['Up', 'Down', 'Left', 'Right']:
                self.manual_controls.stop_movement(key.lower())

    def on_mode_change(self, *args):
        idx = ["Manuel", "Mod 1", "Mod 2", "Mod 3"].index(self.mode.get())
        self.mode_frame.show_confirm_buttons(idx)
    
    def confirm_mode(self):
        self.confirmed_mode = self.mode.get()
        self.mode_frame.hide_confirm_buttons()
        self.fe_frame.place_forget()
        self.letter_frame.place_forget()
        self.manual_controls.place_forget()
        self.restricted_area_frame.place_forget()

        if self.confirmed_mode == "Mod 2":
            self.fe_frame.place(1000, 50, 500, 150)
        elif self.confirmed_mode == "Mod 3":
            self.letter_frame.place(1000, 300, 450, 180)
            self.restricted_area_frame.place(1000, 500, 300, 150)
            self.awaiting_confirmation = False
            self.detected_letter = None
            self.confirmed_letter = None
            self.detected_shape = None
            self.confirmed_shape = None
        elif self.confirmed_mode == "Manuel":
            self.manual_controls.place(1000, 200, 300, 300)
    
    def reject_mode(self):
        self.mode.set(self.confirmed_mode)
        self.mode_frame.hide_confirm_buttons()
    
    def reset_system(self):
        self.mode.set("Mod 1")
        self.confirmed_mode = "Mod 1"
        self.mode_frame.hide_confirm_buttons()
        self.fe_frame.place_forget()
        self.letter_frame.place_forget()
        self.manual_controls.place_forget()
        self.restricted_area_frame.place_forget()
    
    # manual_command metodunu güncelle
    def manual_command(self, command):
        self.arduino_controller.send_command(command)
        
        # Pozisyon güncellemesi al
        if hasattr(self, 'manual_controls'):
            yaw, pitch = self.arduino_controller.get_position()
            self.manual_controls.update_position(yaw, pitch)
    
    def toggle_tracking(self):
        self.tracking_enabled = not self.tracking_enabled
        self.tracking_controls.update_button(self.tracking_enabled)
        
        # Object detector'da tracking'i aç/kapa
        self.object_detector.set_tracking(self.tracking_enabled)
        
        if self.tracking_enabled:
            print("Otomatik takip ve ByteTrack başlatıldı")
        else:
            print("Otomatik takip ve ByteTrack durduruldu")
    
    def confirm_restricted_angle(self):
        angle_str = self.restricted_area_frame.get_angle()
        try:
            angle = float(angle_str)
            if 0 <= angle <= 360:
                self.restricted_angle = angle
                messagebox.showinfo("Onay", f"Atışa Yasaklı Alan: {angle} Derece olarak ayarlandı.")
            else:
                messagebox.showerror("Hata", "Lütfen 0 ile 360 arasında bir değer giriniz.")
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir sayı giriniz.")
    
    def apply_camera_index(self):
        try:
            new_index = int(self.camera_frame.get_camera_index())
            self.camera_index = new_index
            self.camera_manager.camera_index = new_index
            messagebox.showinfo("Bilgi", f"Kamera indeksi {new_index} olarak ayarlandı")
            
            if self.running:
                self.stop()
                time.sleep(1)
                self.start()
                
        except ValueError:
            messagebox.showerror("Hata", "Geçerli bir sayı giriniz")
    
    def accept_engagement(self):
        if self.awaiting_confirmation:
            self.letter_frame.update_letter(self.confirmed_letter)
            self.letter_frame.update_shape(self.confirmed_shape)
            messagebox.showinfo(
                "Onay",
                f"Angajman: Harf:{self.confirmed_letter} Şekil:{self.confirmed_shape} KABUL EDİLDİ"
            )
            self.awaiting_confirmation = False
    
    def track_object(self, frame, box):
        if not self.arduino_controller.arduino or not self.tracking_enabled:
            return
        
        if box is None or len(box) != 4:
            return
        
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        x1, y1, x2, y2 = box
        obj_x = (x1 + x2) // 2
        obj_y = (y1 + y2) // 2
        
        hata_x = obj_x - center_x
        
        if abs(hata_x) > PIXEL_THRESHOLD:
            if hata_x < 0:
                self.arduino_controller.send_command('left')
                print(f"Nesne sola kaymış, sola dön: {hata_x}")
            else:
                self.arduino_controller.send_command('right')
                print(f"Nesne sağa kaymış, sağa dön: {hata_x}")
    
    def start(self):
        if not self.running:
            self.running = True
            self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
            self.video_thread.start()
    
    def stop(self):
        self.running = False
        self.arduino_controller.close()
        self.camera_manager.release()
        if self.video_thread and self.video_thread.is_alive():
            self.video_thread.join(timeout=2)
        print("Program durduruluyor...")
        self.root.after(0, self.root.destroy)
    
    def video_loop(self):
        if not self.camera_manager.start_camera():
            messagebox.showerror("Hata", "Kamera açılamadı! Lütfen bağlantıyı kontrol edin.")
            self.running = False
            return

        image_id = None
        last_command_time = time.time()
        hareket_durumu = "DUR"
        selected_target_id = None  # Takip edilen hedefin ID'si

        while self.running:
            ret, frame = self.camera_manager.read_frame()
            if not ret:
                print("Kare alınamadı. Tekrar deniyor...")
                time.sleep(0.1)
                continue

            mode = self.confirmed_mode
            ann = frame.copy()
            current_time = time.time()

            if mode == "Manuel":
                ann = frame.copy()
            elif (mode == "Mod 1" or mode == "Mod 2") and self.object_detector.model:
                ann, box, tracked_objects = self.object_detector.detect_objects(frame, mode)
                
                # Takip aktifse ve nesne tespit edildiyse
                if self.tracking_enabled and tracked_objects:
                    # İlk seferinde veya hedef kaybolmuşsa yeni hedef seç
                    if selected_target_id is None:
                        selected_target_id = tracked_objects[0]['id']
                    
                    # Seçili hedefi bul
                    target_box = None
                    for obj in tracked_objects:
                        if obj['id'] == selected_target_id:
                            target_box = obj['bbox']
                            break
                    
                    # Hedef kaybolmuşsa yeni hedef seç
                    if target_box is None and tracked_objects:
                        selected_target_id = tracked_objects[0]['id']
                        target_box = tracked_objects[0]['bbox']
                    
                    # Takip kontrolü
                    if target_box and (current_time - last_command_time) > COMMAND_DELAY:
                        h, w = frame.shape[:2]
                        center_x = w // 2
                        
                        x1, y1, x2, y2 = target_box
                        obj_x = (x1 + x2) // 2
                        hata_x = obj_x - center_x
                        
                        # Seçili hedefi vurgula
                        cv2.rectangle(ann, (x1-5, y1-5), (x2+5, y2+5), (0, 255, 255), 3)
                        cv2.putText(ann, "TRACKING", (x1, y1-25), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                        
                        if abs(hata_x) > CENTER_TOLERANCE:
                            if hata_x < 0:
                                if hareket_durumu != "SOL":
                                    self.arduino_controller.send_command('left')
                                    hareket_durumu = "SOL"
                            else:
                                if hareket_durumu != "SAĞ":
                                    self.arduino_controller.send_command('right')
                                    hareket_durumu = "SAĞ"
                        else:
                            if hareket_durumu != "DUR":
                                self.arduino_controller.send_command('stop')
                                print("MERKEZE ULAŞILDI - DUR")
                                hareket_durumu = "DUR"
                        
                        last_command_time = current_time
                else:
                    # Takip kapalıysa hedef ID'yi sıfırla
                    selected_target_id = None
                    
            elif mode == "Mod 3":
                if not self.awaiting_confirmation:
                    # QR kod tespiti
                    letter = self.qr_detector.detect(frame)
                    if letter:
                        self.detected_letter = letter
                        self.confirmed_letter = letter
                        self.letter_frame.update_letter(letter)
                    
                    # Renk ve şekil tespiti
                    processed_frame, result = self.object_detector.detect_color_shape(frame)
                    color, shape, box = result
                    if color and shape:
                        self.detected_shape = f"{color} {shape}"
                        self.confirmed_shape = f"{color} {shape}"
                        self.letter_frame.update_shape(f"{color} {shape}")
                        self.awaiting_confirmation = True  # Onay bekle
                    ann = processed_frame
                else:
                    ann = frame.copy()

            # Crosshair ekle
            ann = add_crosshair(ann)
            
            # Durum bilgilerini ekle
            if self.tracking_enabled:
                cv2.putText(ann, "TRACKING: ON", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                if selected_target_id:
                    cv2.putText(ann, f"Target ID: {selected_target_id}", (10, 60), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # Görüntüyü göster
            try:
                image = cv2.cvtColor(ann, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                if image_id is None:
                    image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=image)
                else:
                    self.canvas.itemconfig(image_id, image=image)

                self.canvas.image = image
            except Exception as e:
                print(f"Görüntü işleme hatası: {e}")

        self.camera_manager.release()