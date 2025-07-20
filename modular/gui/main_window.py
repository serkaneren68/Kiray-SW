import tkinter as tk
from PIL import Image, ImageTk
import cv2
import threading
import time
from tkinter import messagebox

from config.constants import *
from gui.frames import *
from gui.controls import *
from camera.camera_manager import CameraManager
from arduino.arduino_controller import ArduinoController
from detection.object_detector import ObjectDetector
from detection.qr_detector import QRDetector
from utils.helpers import add_crosshair
from utils.angle_calculator import AngleCalculator


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
        self.angle_calculator = AngleCalculator()
        
        # UI oluştur
        self._setup_ui()
        
        # Klavye event'lerini bağla
        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.bind('<KeyRelease>', self.on_key_release)
        
        # Aktif tuşları takip et
        self.pressed_keys = set()
    
    def _setup_ui(self):
        # Canvas
        self.canvas = tk.Canvas(self.root, bg="black", width=CANVAS_WIDTH, 
                               height=CANVAS_HEIGHT, highlightthickness=2, 
                               highlightbackground="gray")
        self.canvas.place(x=30, y=30)
        
        # Frame'ler
        self.mode_frame = ModeFrame(self.root, self.mode, self.on_mode_change,
                                   self.confirm_mode, self.reject_mode)
        self.mode_frame.place(30, 520)
        
        self.fe_frame = FriendEnemyFrame(self.root)
        self.letter_frame = LetterFrame(self.root, self.accept_engagement)
        self.restricted_area_frame = RestrictedAreaFrame(self.root, self.confirm_restricted_angle)
        self.camera_frame = CameraSelectionFrame(self.root, self.apply_camera_index)
        self.camera_frame.place(550, 520, 250, 120)
        
        # Kontroller
        self.manual_controls = ManualControls(self.root, self.manual_command)
        self.tracking_controls = TrackingControls(self.root, self.toggle_tracking)
        self.tracking_controls.place(850, 640, 180, 80)
        
        self.main_controls = MainControls(self.root, self.start, self.stop, self.reset_system)
        self.main_controls.place(30, 650)
    
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

        if self.confirmed_mode == "Mod 1":
            # Mod 1 için otomatik takibi etkinleştir
            self.tracking_enabled = True
            self.tracking_controls.update_button(True)
            self.object_detector.set_tracking(False)  # ByteTrack kapalı
            print("Mod 1: Otomatik hedef takibi aktif")
            
        elif self.confirmed_mode == "Mod 2":
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
            self.manual_controls.place(1000, 200, 350, 400)
            self.tracking_enabled = False
            self.tracking_controls.update_button(False)
    
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
            # Kamera indeksi
            new_index = int(self.camera_frame.get_camera_index())
            self.camera_index = new_index
            self.camera_manager.camera_index = new_index
            
            # Dönüşüm ayarları
            rotate_90 = self.camera_frame.get_rotate_90()
            flip_horizontal = self.camera_frame.get_flip_horizontal()
            flip_vertical = self.camera_frame.get_flip_vertical()
            
            self.camera_manager.set_transformations(rotate_90, flip_horizontal, flip_vertical)
            
            messagebox.showinfo("Bilgi", 
                f"Kamera ayarları güncellendi:\n"
                f"İndeks: {new_index}\n"
                f"90° Döndür: {rotate_90}\n"
                f"Yatay Aynala: {flip_horizontal}\n"
                f"Dikey Aynala: {flip_vertical}")
            
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
        tracking_lost_count = 0
        
        # Hedef takip değişkenleri
        locked_target_box = None  # Kilitlenilen hedefin son bilinen konumu
        locked_target_id = None   # Hedef ID'si (konum bazlı)
        target_locked = False
        last_movement_time = 0
        selected_target_id = None

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
                
            elif mode == "Mod 1" and self.object_detector.model:
                # Mod 1 - İlk kilitlenilen hedefi takip et
                if target_locked and locked_target_box:
                    # Kilitli hedefi bul
                    ann, current_box, all_boxes = self.object_detector.detect_and_track_target(
                        frame, mode, locked_target_box
                    )
                    
                    if current_box:
                        # Hedef hala görünüyor
                        tracking_lost_count = 0
                        locked_target_box = current_box  # Pozisyonu güncelle
                        
                        h, w = frame.shape[:2]
                        center_x = w // 2
                        center_y = h // 2
                        
                        x1, y1, x2, y2 = current_box
                        obj_x = (x1 + x2) // 2
                        obj_y = (y1 + y2) // 2
                        
                        # Piksel hatası
                        error_x = obj_x - center_x
                        error_y = obj_y - center_y
                        
                        # Açı hesaplama
                        angle_x, angle_y = self.angle_calculator.pixel_to_angle(error_x, error_y)
                        
                        # Debug bilgisi
                        cv2.putText(ann, f"Hedef: ({obj_x}, {obj_y})", 
                                (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 
                                0.6, (255, 255, 0), 2)
                        cv2.putText(ann, f"Piksel Hata: X={error_x} Y={error_y}", 
                                (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 
                                0.6, (255, 255, 0), 2)
                        cv2.putText(ann, f"Aci: X={angle_x:.1f}° Y={angle_y:.1f}°", 
                                (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 
                                0.6, (0, 255, 255), 2)
                        
                        # Hareket kontrolü
                        if (current_time - last_command_time) > 0.5:  # 500ms gecikme (motorun dönmesini bekle)
                            
                            # Açı bazlı hareket komutu
                            command, angle = self.angle_calculator.calculate_move_command(error_x, error_y)
                            
                            if command and angle > 0.5:  # Minimum 0.5 derece
                                # Arduino'nun beklediği format: R23, L45, U10, D5
                                motor_command = f"{command}{int(round(angle))}"
                                self.arduino_controller.send_command(motor_command)
                                
                                print(f"[Mod1] Piksel hatası: X={error_x}, Y={error_y}")
                                print(f"[Mod1] Hesaplanan açı: {angle:.2f}°")
                                print(f"[Mod1] Gönderilen komut: {motor_command}")
                                
                                # Durum güncelle
                                hareket_durumu = f"{command} {int(angle)}°"
                                
                                # Motorun hareketi tamamlamasını bekle
                                # Büyük açılar için daha uzun bekle
                                wait_time = 0.3 + (angle / 45.0) * 0.5  # 45 derece için +0.5 saniye
                                last_command_time = current_time + wait_time
                                
                                # Görsel geri bildirim
                                cv2.putText(ann, f"HAREKET: {motor_command}", 
                                        (center_x - 60, center_y - 80), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 
                                        0.8, (0, 255, 255), 2)
                                
                                # Hareket animasyonu için ok çiz
                                if command in ['L', 'R']:
                                    # Yatay ok
                                    arrow_y = center_y
                                    if command == 'L':
                                        cv2.arrowedLine(ann, (center_x, arrow_y), 
                                                    (center_x - 50, arrow_y), 
                                                    (255, 0, 0), 3)
                                    else:
                                        cv2.arrowedLine(ann, (center_x, arrow_y), 
                                                    (center_x + 50, arrow_y), 
                                                    (255, 0, 0), 3)
                                else:
                                    # Dikey ok
                                    arrow_x = center_x
                                    if command == 'U':
                                        cv2.arrowedLine(ann, (arrow_x, center_y), 
                                                    (arrow_x, center_y - 50), 
                                                    (255, 0, 0), 3)
                                    else:
                                        cv2.arrowedLine(ann, (arrow_x, center_y), 
                                                    (arrow_x, center_y + 50), 
                                                    (255, 0, 0), 3)
                            
                            else:
                                # Hedef merkezde
                                if abs(error_x) < 5 and abs(error_y) < 5:
                                    if hareket_durumu != "TAM MERKEZ":
                                        self.arduino_controller.send_command('X')
                                        hareket_durumu = "TAM MERKEZ"
                                    
                                    # Merkez işareti
                                    cv2.circle(ann, (center_x, center_y), 30, (0, 255, 0), 3)
                                    cv2.putText(ann, "MERKEZ", 
                                            (center_x - 40, center_y + 50), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 
                                            0.7, (0, 255, 0), 2)
                        
                        # Kilitlenme göstergesi - YEŞİL
                        cv2.rectangle(ann, (x1-5, y1-5), (x2+5, y2+5), (0, 255, 0), 3)
                        cv2.putText(ann, "KiLiTLi", 
                                (x1, y1-15), 
                                cv2.FONT_HERSHEY_SIMPLEX, 
                                0.8, (0, 255, 0), 2)
                        
                        # Hedef çizgisi
                        cv2.line(ann, (obj_x, obj_y), (center_x, center_y), 
                                (0, 255, 255), 1, cv2.LINE_AA)
                    
                    else:
                        # Kilitli hedef görüş alanında yok
                        tracking_lost_count += 1
                        cv2.putText(ann, f"HEDEF KAYIP ({tracking_lost_count}/30)", 
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                                0.7, (0, 255, 255), 2)
                        
                        # 30 frame (yaklaşık 1 saniye) kayıpsa kilidi kaldır
                        if tracking_lost_count > 30:
                            target_locked = False
                            locked_target_box = None
                            locked_target_id = None
                            self.arduino_controller.send_command('X')
                            hareket_durumu = "KİLİT KALDIRILDI"
                            print("[Mod1] Hedef kaybedildi, kilit kaldırıldı")
                
                else:
                    # Henüz hedef kilitlenmemiş - en yakını bul
                    ann, target_box, _ = self.object_detector.detect_objects(frame, mode)
                    
                    if target_box and self.tracking_enabled:
                        # İlk hedefi kilitle
                        locked_target_box = target_box
                        target_locked = True
                        tracking_lost_count = 0
                        print(f"[Mod1] İlk hedef kilitlendi: {locked_target_box}")
                        
                        cv2.putText(ann, "YENi HEDEF SECiLDi", 
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, (0, 255, 0), 2)
                
                    else:
                        cv2.putText(ann, "HEDEF ARANIYOR...", 
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                                0.7, (0, 0, 255), 2)
                                
            elif (mode == "Mod 2") and self.object_detector.model:
                ann, box, tracked_objects = self.object_detector.detect_objects(frame, mode)
                
                # Mod 2 için takip mantığı
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
                        self.awaiting_confirmation = True
                    ann = processed_frame
                else:
                    ann = frame.copy()

            # Crosshair ekle
            ann = add_crosshair(ann)
            
            # Durum bilgilerini ekle
            if mode == "Mod 1":
                cv2.putText(ann, "MOD 1: HASSAS TAKiP", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(ann, f"Durum: {hareket_durumu}", (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                
                # Takip durumu
                if self.tracking_enabled:
                    cv2.putText(ann, "TAKiP: AÇIK", (10, ann.shape[0] - 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                else:
                    cv2.putText(ann, "TAKiP: KAPALI", (10, ann.shape[0] - 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            
            elif mode == "Mod 2":
                cv2.putText(ann, "MOD 2: RENK BAZLI", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                if self.tracking_enabled:
                    cv2.putText(ann, f"Takip ID: {selected_target_id}", (10, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            elif mode == "Mod 3":
                cv2.putText(ann, "MOD 3: QR & ŞEKiL", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
                if self.awaiting_confirmation:
                    cv2.putText(ann, "ONAY BEKLiYOR", (10, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            # FPS hesaplama (opsiyonel)
            current_fps = 1.0 / (current_time - self.last_fps_time) if hasattr(self, 'last_fps_time') else 0
            self.last_fps_time = current_time
            cv2.putText(ann, f"FPS: {current_fps:.1f}", (ann.shape[1] - 100, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

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