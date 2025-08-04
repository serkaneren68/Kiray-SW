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


import tkinter as tk
import time

class MainWindow:
    holding_keys: dict = {}
    hold_interval = 100
    def __init__(self, root):
        self.root = root
        self.root.title("KIRAY HAVA SAVUNMA KONTROL PANELI")
        self.root.configure(bg="black")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # Başlangıç animasyonu
        self.start_animation()

        # Başlangıçtan sonra ana UI'i başlat
        self.root.after(4500, self._setup_ui)  # Yalnızca burada çağırın
        
        # Diğer durum değişkenleri
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
        self.mode = tk.StringVar(value="Manuel")
        self.confirmed_mode = "Mod 1"
        self.camera_manager = CameraManager(self.camera_index)
        self.arduino_controller = ArduinoController()
        self.object_detector = ObjectDetector()
        self.qr_detector = QRDetector()
        self.restricted_area_enabled = False
        self.update_timer = None
        self.auto_fire_enabled = False
        self.last_auto_fire_time = 0
        self.auto_fire_cooldown = 3.5

    def start_animation(self):
        self.canvas = tk.Canvas(self.root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg='black')
        self.canvas.pack()

        # PNG görseli yükleme
        image = Image.open('esdeath.jpg')  # Görsel dosya yolunu buraya ekleyin
        self.tk_image = ImageTk.PhotoImage(image)
        
        # Görseli ekranın ortasına yerleştirme
        self.canvas.create_image(WINDOW_WIDTH//3, WINDOW_HEIGHT//3, image=self.tk_image)

    def _setup_ui(self):
        self.canvas.destroy()

        # Canvas
        self.canvas = tk.Canvas(self.root, bg="black", width=CANVAS_WIDTH, 
                            height=CANVAS_HEIGHT, highlightthickness=2, 
                            highlightbackground="gray")
        self.canvas.place(x=20, y=20)
        
        # Frame'ler
        self.mode_frame = ModeFrame(self.root, self.mode, self.on_mode_change,
                                self.confirm_mode, self.reject_mode)
        self.mode_frame.place(20, CANVAS_HEIGHT + 30)
        
        self.fe_frame = FriendEnemyFrame(self.root)
        self.letter_frame = LetterFrame(self.root, self.accept_engagement)
        self.restricted_area_frame = RestrictedAreaFrame(self.root, self.set_reference_point, 
                                                        self.confirm_restricted_area)
        
        # Sağ panel başlangıç konumu
        right_panel_x = CANVAS_WIDTH + 40
        
        # Kamera ayarları - sağ üst
        self.camera_frame = CameraSelectionFrame(self.root, self.apply_camera_index)
        self.camera_frame.place(right_panel_x, 20, 300, 180)
        
        # Kontroller - sağ taraf
        self.manual_controls = ManualControls(self.root, self.manual_command)
        
    # Takip kontrolü
        self.tracking_controls = TrackingControls(self.root, self.toggle_tracking)
        self.tracking_controls.place(right_panel_x, 440, 300, 100)
        
        # Atış modu çerçevesi
        self.fire_mode_frame = tk.LabelFrame(self.root, text="Atış Modu", 
                                            bg="black", fg="orange", bd=1)
        
        self.fire_mode_btn = tk.Button(
            self.fire_mode_frame,
            text="MANUEL ATIŞ",
            font=("Arial", 12),
            bg="blue",
            fg="white",
            command=self.toggle_fire_mode
        )
        self.fire_mode_btn.pack(pady=8, padx=15)
        
        # Bilgi etiketi
        self.fire_info_label = tk.Label(
            self.fire_mode_frame,
            text="Space tuşu ile ateş edin",
            font=("Arial", 9),
            bg="black",
            fg="yellow"
        )
        self.fire_info_label.pack(pady=3)
        
        # Atış modu çerçevesini yerleştirme
        self.fire_mode_frame.place(x=right_panel_x, y=550, width=300, height=90)
            
        # Ana kontroller - alt kısım
        self.main_controls = MainControls(self.root, self.start, self.stop, self.reset_system)
        self.main_controls.place(20, CANVAS_HEIGHT + 160)
        
        # Klavye kontrolü
        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.bind('<KeyRelease>', self.on_key_release)
        
        # Aktif tuşları takip et
        self.pressed_keys = set()
        self.update_timer = None

    def on_key_press(self, event):
        """Klavye tuşuna basıldığında"""
        key = event.keysym
        
        # ATIŞ KONTROLÜ - SPACE TUŞU İÇİN ÖZEL DURUM
        if key == 'space' and not self.auto_fire_enabled:
            # Space tuşu için pressed_keys kontrolü yapma
            if self.confirmed_mode in ["Manuel", "Mod 1", "Mod 2"]:
                self.arduino_controller.send_command('shot')
                print("🎯 MANUEL ATIŞ!")
            return  # Erken çık, pressed_keys'e ekleme
        
        # Diğer tuşlar için normal kontrol
        if key in self.pressed_keys:
            return
        
        self.pressed_keys.add(key)
        
        # Yön tuşları kontrolü (sadece Manuel modda)
        if self.confirmed_mode == "Manuel" and hasattr(self, 'manual_controls'):
            if key == 'Up':
                self.manual_controls.start_movement('up')
            elif key == 'Down':
                self.manual_controls.start_movement('down')
            elif key == 'Left':
                self.manual_controls.start_movement('left')
            elif key == 'Right':
                self.manual_controls.start_movement('right')
            elif key == 'Escape':
                self.manual_command('stop')
            elif key == 'Home':
                self.manual_command('home')

    def on_key_release(self, event):
        """Klavye tuşu bırakıldığında"""
        key = event.keysym
        
        # Space tuşu için özel durum - pressed_keys'den çıkarma
        if key == 'space':
            return  # Space için release işlemi yapma
        
        # Tuşu basılı listesinden çıkar
        self.pressed_keys.discard(key)
        
        # Manuel mod kontrolü
        if self.confirmed_mode != "Manuel":
            return
        
        # Yön tuşları bırakıldığında dur
        if hasattr(self, 'manual_controls'):
            if key in ('Up', 'Down', 'Left', 'Right'):
                dir_map = {'Up':'up', 'Down':'down', 'Left':'left', 'Right':'right'}
                direction = dir_map[key]

                # Basmayı bırakınca dur komutu
                self.holding_keys[direction] = False
                self.manual_controls.stop_movement(direction)

    def on_mode_change(self, *args):
        idx = ["Manuel", "Mod 1", "Mod 2", "Mod 3"].index(self.mode.get())
        self.mode_frame.show_confirm_buttons(idx)
    
    def confirm_mode(self):
        """Mod onaylama"""
        self.confirmed_mode = self.mode.get()
        self.mode_frame.hide_confirm_buttons()
        
        # Tüm mod-spesifik frame'leri gizle
        self.fe_frame.place_forget()
        self.letter_frame.place_forget()
        self.manual_controls.place_forget()
        self.restricted_area_frame.place_forget()
        
        # Açı güncellemesini durdur
        if hasattr(self, 'update_timer') and self.update_timer:
            self.root.after_cancel(self.update_timer)
            self.update_timer = None

        # Sağ panel konumu
        right_panel_x = CANVAS_WIDTH + 40

        if self.confirmed_mode == "Mod 2":
            # Dost/Düşman çerçevesi - manuel kontrollerin yerine
            self.fe_frame.place(right_panel_x, 210, 300, 120)
            
        elif self.confirmed_mode == "Mod 3":
            # Letter frame - üstte
            self.letter_frame.place(right_panel_x, 210, 300, 160)
            # Restricted area yok (şimdilik)
            self.awaiting_confirmation = False
            self.detected_letter = None
            self.confirmed_letter = None
            self.detected_shape = None
            self.confirmed_shape = None
            
        elif self.confirmed_mode == "Manuel":
            # Manuel kontroller
            self.manual_controls.place(right_panel_x, 210, 300, 220)
            # Yasaklı alan kontrolü - altta
            self.restricted_area_frame.place(right_panel_x, 550, 300, 280)
            # Manuel modda açı güncellemesini başlat
            self.start_angle_update()
    
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
        print(f"[MAIN] Manuel komut alındı: {command}")  # Debug için ekleyin
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
    
    def _repeat_hold(self, direction):
        # Eğer hâlâ basılı tutuluyorsa, hareket komutunu tekrar gönder
        if self.holding_keys.get(direction, False):
            self.manual_controls.start_movement(direction)
            # Bir sonraki tetikleme
            self.root.after(self.hold_interval,
                            lambda d=direction: self._repeat_hold(d))

    def video_loop(self):
        if not self.camera_manager.start_camera():
            messagebox.showerror("Hata", "Kamera açılamadı!")
            self.running = False
            return

        # Tracker hesaplayıcı
        from utils.tracker_calculator import TrackerCalculator
        tracker_calc = TrackerCalculator()
        
        image_id = None
        last_tracking_time = time.time()
        
        # Her iki mod için ortak hedef takip değişkenleri
        target_tracking = {
            'current_target_id': None,
            'target_bbox': None,  # BBOX'I DA SAKLA
            'target_lost_frames': 0,
            'max_lost_frames': 10,
            'is_locked': False,
            'first_lock': True  # İLK KİLİTLEME İÇİN
        }

        while self.running:
            ret, frame = self.camera_manager.read_frame()
            if not ret:
                time.sleep(0.1)
                continue

            mode = self.confirmed_mode
            ann = frame.copy()
            current_time = time.time()

            # MOD 1 - TÜM BALONLARI TAKİP ET
            if mode == "Mod 1" and self.object_detector.model:
                ann, box, tracked_objects = self.object_detector.detect_objects(frame, mode)
                
                # Takip aktifse
                if self.tracking_enabled:
                    # EĞER KİLİTLİ BİR HEDEF VARSA
                    if target_tracking['is_locked'] and target_tracking['target_bbox'] is not None:
                        # Mevcut kilitli hedefin pozisyonunu güncelle
                        x1_old, y1_old, x2_old, y2_old = target_tracking['target_bbox']
                        cx_old = (x1_old + x2_old) // 2
                        cy_old = (y1_old + y2_old) // 2
                        
                        # En yakın nesneyi bul (ID yerine pozisyon bazlı)
                        min_distance = float('inf')
                        closest_box = None
                        
                        if tracked_objects:
                            for obj in tracked_objects:
                                x1, y1, x2, y2 = obj['bbox']
                                cx = (x1 + x2) // 2
                                cy = (y1 + y2) // 2
                                
                                # Eski pozisyona olan mesafe
                                distance = ((cx - cx_old)**2 + (cy - cy_old)**2)**0.5
                                
                                if distance < min_distance and distance < 100:  # 100 piksel içinde
                                    min_distance = distance
                                    closest_box = obj['bbox']
                                    target_tracking['current_target_id'] = obj['id']
                        
                        elif box:  # ByteTrack çalışmıyorsa
                            x1, y1, x2, y2 = box
                            cx = (x1 + x2) // 2
                            cy = (y1 + y2) // 2
                            distance = ((cx - cx_old)**2 + (cy - cy_old)**2)**0.5
                            
                            if distance < 100:  # 100 piksel içinde
                                closest_box = box
                        
                        # Hedef bulunduysa güncelle
                        if closest_box:
                            target_tracking['target_bbox'] = closest_box
                            target_tracking['target_lost_frames'] = 0
                            target_box = closest_box
                        else:
                            # Hedef kayıp
                            target_tracking['target_lost_frames'] += 1
                            target_box = None
                            
                            if target_tracking['target_lost_frames'] > target_tracking['max_lost_frames']:
                                print("Hedef tamamen kayboldu, kilit açılıyor")
                                target_tracking['is_locked'] = False
                                target_tracking['current_target_id'] = None
                                target_tracking['target_bbox'] = None
                                target_tracking['first_lock'] = True
                    
                    # İLK HEDEF SEÇİMİ (sadece kilitli değilse ve ilk sefer)
                    elif not target_tracking['is_locked'] and target_tracking['first_lock']:
                        if tracked_objects and len(tracked_objects) > 0:
                            # İlk nesneyi seç ve HEMEN kilitle
                            first_obj = tracked_objects[0]
                            target_tracking['current_target_id'] = first_obj['id']
                            target_tracking['target_bbox'] = first_obj['bbox']
                            target_tracking['is_locked'] = True
                            target_tracking['first_lock'] = False
                            target_box = first_obj['bbox']
                            print(f"İlk hedef kilitlendi: ID {target_tracking['current_target_id']}")
                        elif box:
                            # ByteTrack yoksa basit takip
                            target_tracking['target_bbox'] = box
                            target_tracking['is_locked'] = True
                            target_tracking['first_lock'] = False
                            target_box = box
                            print("İlk hedef kilitlendi (basit takip)")
                    
                    # TAKİP KONTROLÜ - SADECE KİLİTLİ HEDEF İÇİN
                    if target_tracking['is_locked'] and 'target_box' in locals() and target_box and (current_time - last_tracking_time >= TRACKING_INTERVAL):
                        yaw_steps, pitch_steps = tracker_calc.calculate_movement(target_box)
                        
                        if yaw_steps != 0 or pitch_steps != 0:
                            self.arduino_controller.send_direct_movement(yaw_steps, pitch_steps)
                        
                        last_tracking_time = current_time
                        
                        # Takip edilen hedefi vurgula
                        x1, y1, x2, y2 = target_box
                        cv2.rectangle(ann, (x1-5, y1-5), (x2+5, y2+5), (0, 255, 255), 4)
                        cv2.putText(ann, "KILITLI", (x1, y1-25), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                        
                        # Kilit sembolü
                        cv2.drawMarker(ann, ((x1+x2)//2, (y1+y2)//2), (0, 0, 255), 
                                    cv2.MARKER_TILTED_CROSS, 30, 3)
                        
                        # Hedef bilgisi
                        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                        error_x = cx - tracker_calc.center_x
                        error_y = cy - tracker_calc.center_y
                        cv2.putText(ann, f"Hata: X={error_x}, Y={error_y}", 
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    # Kilit durumu
                    if target_tracking['is_locked']:
                        cv2.putText(ann, "HEDEF KILITLI - DEGISTIRILEMEZ", (10, 60), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                        
                        if target_tracking['target_lost_frames'] > 0:
                            cv2.putText(ann, f"Hedef Aranıyor: {target_tracking['target_lost_frames']}/{target_tracking['max_lost_frames']}", 
                                    (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
                
                # Takip kapalıysa sıfırla
                if not self.tracking_enabled:
                    target_tracking = {
                        'current_target_id': None,
                        'target_bbox': None,
                        'target_lost_frames': 0,
                        'max_lost_frames': 10,
                        'is_locked': False,
                        'first_lock': True
                    }

                if (self.auto_fire_enabled and 
                    target_tracking['is_locked'] and 
                    'target_box' in locals() and 
                    target_box):
                    
                    if self.is_target_centered(target_box):
                        if self.execute_auto_fire():
                            # Atış göstergesi
                            x1, y1, x2, y2 = target_box
                            cv2.putText(ann, "OTONOM ATIS!", 
                                    (x1, y1-50), cv2.FONT_HERSHEY_SIMPLEX, 
                                    1.0, (0, 255, 255), 3)
                            
                            # Atış efekti
                            cv2.circle(ann, ((x1+x2)//2, (y1+y2)//2), 50, (0, 255, 255), 3)
            
            # MOD 2 - SADECE DÜŞMAN (KIRMIZI) BALONLARI TAKİP ET
            elif mode == "Mod 2" and self.object_detector.model:
                ann, box, tracked_objects = self.object_detector.detect_objects(frame, mode)
                
                # Takip aktifse
                if self.tracking_enabled:
                    # EĞER KİLİTLİ BİR DÜŞMAN HEDEF VARSA
                    if target_tracking['is_locked'] and target_tracking['target_bbox'] is not None:
                        # Mevcut kilitli düşman hedefin pozisyonunu güncelle
                        x1_old, y1_old, x2_old, y2_old = target_tracking['target_bbox']
                        cx_old = (x1_old + x2_old) // 2
                        cy_old = (y1_old + y2_old) // 2
                        
                        # En yakın düşman nesneyi bul (pozisyon bazlı)
                        min_distance = float('inf')
                        closest_box = None
                        
                        if tracked_objects:
                            for obj in tracked_objects:
                                x1, y1, x2, y2 = obj['bbox']
                                cx = (x1 + x2) // 2
                                cy = (y1 + y2) // 2
                                
                                # Eski pozisyona olan mesafe
                                distance = ((cx - cx_old)**2 + (cy - cy_old)**2)**0.5
                                
                                if distance < min_distance and distance < 100:  # 100 piksel içinde
                                    min_distance = distance
                                    closest_box = obj['bbox']
                                    target_tracking['current_target_id'] = obj['id']
                        
                        elif box:  # ByteTrack çalışmıyorsa
                            x1, y1, x2, y2 = box
                            cx = (x1 + x2) // 2
                            cy = (y1 + y2) // 2
                            distance = ((cx - cx_old)**2 + (cy - cy_old)**2)**0.5
                            
                            if distance < 100:  # 100 piksel içinde
                                closest_box = box
                        
                        # Düşman hedef bulunduysa güncelle
                        if closest_box:
                            target_tracking['target_bbox'] = closest_box
                            target_tracking['target_lost_frames'] = 0
                            target_box = closest_box
                        else:
                            # Düşman hedef kayıp
                            target_tracking['target_lost_frames'] += 1
                            target_box = None
                            
                            if target_tracking['target_lost_frames'] > target_tracking['max_lost_frames']:
                                print("Düşman hedef tamamen kayboldu, kilit açılıyor")
                                target_tracking['is_locked'] = False
                                target_tracking['current_target_id'] = None
                                target_tracking['target_bbox'] = None
                                target_tracking['first_lock'] = True
                    
                    # İLK DÜŞMAN HEDEF SEÇİMİ (sadece kilitli değilse ve ilk sefer)
                    elif not target_tracking['is_locked'] and target_tracking['first_lock']:
                        if tracked_objects and len(tracked_objects) > 0:
                            # En yakın düşmanı seç ve HEMEN kilitle
                            min_distance = float('inf')
                            closest_enemy = None
                            
                            for obj in tracked_objects:
                                x1, y1, x2, y2 = obj['bbox']
                                cx = (x1 + x2) // 2
                                cy = (y1 + y2) // 2
                                distance = abs(cx - tracker_calc.center_x) + abs(cy - tracker_calc.center_y)
                                
                                if distance < min_distance:
                                    min_distance = distance
                                    closest_enemy = obj
                            
                            if closest_enemy:
                                target_tracking['current_target_id'] = closest_enemy['id']
                                target_tracking['target_bbox'] = closest_enemy['bbox']
                                target_tracking['is_locked'] = True
                                target_tracking['first_lock'] = False
                                target_box = closest_enemy['bbox']
                                print(f"İlk düşman hedef kilitlendi: ID {target_tracking['current_target_id']}")
                        elif box:
                            # ByteTrack yoksa basit takip
                            target_tracking['target_bbox'] = box
                            target_tracking['is_locked'] = True
                            target_tracking['first_lock'] = False
                            target_box = box
                            print("İlk düşman hedef kilitlendi (basit takip)")
                    
                    # TAKİP KONTROLÜ - SADECE KİLİTLİ DÜŞMAN HEDEF İÇİN
                    if target_tracking['is_locked'] and 'target_box' in locals() and target_box and (current_time - last_tracking_time >= TRACKING_INTERVAL):
                        yaw_steps, pitch_steps = tracker_calc.calculate_movement(target_box)
                        
                        if yaw_steps != 0 or pitch_steps != 0:
                            self.arduino_controller.send_direct_movement(yaw_steps, pitch_steps)
                        
                        last_tracking_time = current_time
                        
                        # Takip edilen düşman hedefi vurgula
                        x1, y1, x2, y2 = target_box
                        cv2.rectangle(ann, (x1-5, y1-5), (x2+5, y2+5), (0, 255, 255), 4)
                        cv2.putText(ann, "DUSMAN KILITLI", (x1, y1-25), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
                        
                        # Kilit ve hedef sembolü
                        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                        cv2.drawMarker(ann, (cx, cy), (0, 0, 255), cv2.MARKER_TILTED_CROSS, 30, 3)
                        
                        # Çift daire hedef göstergesi
                        cv2.circle(ann, (cx, cy), 25, (0, 0, 255), 2)
                        cv2.circle(ann, (cx, cy), 30, (0, 255, 255), 2)
                        
                        # Hedef bilgisi
                        error_x = cx - tracker_calc.center_x
                        error_y = cy - tracker_calc.center_y
                        cv2.putText(ann, f"Hata: X={error_x}, Y={error_y}", 
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    # Kilit durumu
                    if target_tracking['is_locked']:
                        cv2.putText(ann, "DUSMAN HEDEF KILITLI - DEGISTIRILEMEZ", (10, 60), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                        
                        if target_tracking['target_lost_frames'] > 0:
                            cv2.putText(ann, f"Düşman Aranıyor: {target_tracking['target_lost_frames']}/{target_tracking['max_lost_frames']}", 
                                    (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
                
                # Takip kapalıysa sıfırla
                if not self.tracking_enabled:
                    target_tracking = {
                        'current_target_id': None,
                        'target_bbox': None,
                        'target_lost_frames': 0,
                        'max_lost_frames': 10,
                        'is_locked': False,
                        'first_lock': True
                    }
                
                # Durum bilgisi - sadece tespit edilen düşman sayısı
                if tracked_objects:
                    enemy_count = len(tracked_objects)
                    cv2.putText(ann, f"Tespit Edilen Düşman: {enemy_count}", 
                            (10, CANVAS_HEIGHT - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    
                    # Kilitli hedef varsa ekstra bilgi
                    if target_tracking['is_locked']:
                        cv2.putText(ann, "YENİ DÜŞMANLAR GÖRMEZDEN GELİNİYOR", 
                                (10, CANVAS_HEIGHT - 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
                
                # Durum bilgisi
                enemy_count = len([obj for obj in tracked_objects]) if tracked_objects else 0
                cv2.putText(ann, f"Dusman Sayisi: {enemy_count}", 
                        (10, CANVAS_HEIGHT - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                if (self.auto_fire_enabled and 
                    target_tracking['is_locked'] and 
                    'target_box' in locals() and 
                    target_box):
                    
                    if self.is_target_centered(target_box):
                        if self.execute_auto_fire():
                            # Düşman atış göstergesi
                            x1, y1, x2, y2 = target_box
                            cv2.putText(ann, "DUSMAN IMHA!", 
                                    (x1, y1-50), cv2.FONT_HERSHEY_SIMPLEX, 
                                    1.0, (0, 0, 255), 3)
                            
                            # Çifte atış efekti
                            cv2.circle(ann, ((x1+x2)//2, (y1+y2)//2), 40, (0, 0, 255), 4)
                            cv2.circle(ann, ((x1+x2)//2, (y1+y2)//2), 60, (255, 255, 0), 2)
            
            # MOD 3 - QR KOD VE ŞEKİL TESPİTİ
            elif mode == "Mod 3":
                if not self.awaiting_confirmation:
                    letter = self.qr_detector.detect(frame)
                    if letter:
                        self.detected_letter = letter
                        self.confirmed_letter = letter
                        self.letter_frame.update_letter(letter)
                    
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
            
            elif mode == "Manuel":
                # Manuel modda görüntüyü göster
                if self.restricted_area_enabled and hasattr(self, 'arduino_controller'):
                    # Yasaklı alan göstergesi ekle
                    relative_yaw = self.arduino_controller.get_relative_yaw()
                    shot_allowed = self.arduino_controller.is_shot_allowed()
                    
                    # Üst bilgi çubuğu
                    cv2.rectangle(ann, (0, 0), (CANVAS_WIDTH, 40), (0, 0, 0), -1)
                    
                    # Açı bilgisi
                    cv2.putText(ann, f"Aci: {relative_yaw:.1f} derece", 
                            (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    
                    # Yasaklı alan bilgisi
                    min_angle = self.arduino_controller.restricted_yaw_min
                    max_angle = self.arduino_controller.restricted_yaw_max
                    cv2.putText(ann, f"Yasakli: {min_angle} - {max_angle}", 
                            (CANVAS_WIDTH//2 - 100, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
                    
                    # Atış durumu
                    if shot_allowed:
                        cv2.putText(ann, "ATIS: SERBEST", 
                                (CANVAS_WIDTH - 200, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    else:
                        cv2.putText(ann, "ATIS: YASAK!", 
                                (CANVAS_WIDTH - 200, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        # Kırmızı çerçeve
                        cv2.rectangle(ann, (2, 2), (CANVAS_WIDTH-3, CANVAS_HEIGHT-3), (0, 0, 255), 3)
                        
                        # Ortada büyük uyarı
                        warning_text = "YASAKLI BOLGEDE"
                        font_scale = 1.5
                        thickness = 3
                        (text_width, text_height), _ = cv2.getTextSize(warning_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
                        text_x = (CANVAS_WIDTH - text_width) // 2
                        text_y = CANVAS_HEIGHT // 2
                        
                        # Arka plan kutusu
                        cv2.rectangle(ann, (text_x - 10, text_y - text_height - 10), 
                                    (text_x + text_width + 10, text_y + 10), (0, 0, 0), -1)
                        cv2.rectangle(ann, (text_x - 10, text_y - text_height - 10), 
                                    (text_x + text_width + 10, text_y + 10), (0, 0, 255), 2)
                        
                        # Uyarı metni
                        cv2.putText(ann, warning_text, (text_x, text_y), 
                                cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness)
                
                # Açı göstergesi çizimi (isteğe bağlı)
                if hasattr(self, 'arduino_controller'):
                    # Açı göstergesi yarım daire
                    center_x = CANVAS_WIDTH // 2
                    gauge_y = CANVAS_HEIGHT - 60
                    gauge_radius = 150
                    
                    # Yarım daire arka plan
                    cv2.ellipse(ann, (center_x, gauge_y), (gauge_radius, gauge_radius), 
                            0, 180, 360, (100, 100, 100), 2)
                    
                    # Açı işaretleri
                    for angle in [-90, -45, 0, 45, 90]:
                        rad = np.radians(180 - angle)  # OpenCV için açı dönüşümü
                        x = int(center_x + gauge_radius * np.cos(rad))
                        y = int(gauge_y - gauge_radius * np.sin(rad))
                        cv2.circle(ann, (x, y), 3, (200, 200, 200), -1)
                        cv2.putText(ann, str(angle), (x-15, y-10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
                    
                    # Mevcut açı göstergesi
                    if hasattr(self, 'arduino_controller'):
                        current_angle = self.arduino_controller.get_relative_yaw()
                        if -90 <= current_angle <= 90:
                            rad = np.radians(180 - current_angle)
                            x = int(center_x + gauge_radius * np.cos(rad))
                            y = int(gauge_y - gauge_radius * np.sin(rad))
                            cv2.line(ann, (center_x, gauge_y), (x, y), (0, 255, 255), 3)
                            cv2.circle(ann, (x, y), 8, (0, 255, 255), -1)
                    
                    # Yasaklı alan işaretleme
                    if self.restricted_area_enabled:
                        min_angle = max(-90, self.arduino_controller.restricted_yaw_min)
                        max_angle = min(90, self.arduino_controller.restricted_yaw_max)
                        
                        # Yasaklı alan yayı
                        if min_angle < max_angle:
                            cv2.ellipse(ann, (center_x, gauge_y), (gauge_radius-10, gauge_radius-10),
                                    0, 180-max_angle, 180-min_angle, (0, 0, 255), 10)
                                        # Yasaklı alan sınır çizgileri
                            for angle in [min_angle, max_angle]:
                                if -90 <= angle <= 90:
                                    rad = np.radians(180 - angle)
                                    x1 = int(center_x + (gauge_radius - 20) * np.cos(rad))
                                    y1 = int(gauge_y - (gauge_radius - 20) * np.sin(rad))
                                    x2 = int(center_x + (gauge_radius + 20) * np.cos(rad))
                                    y2 = int(gauge_y - (gauge_radius + 20) * np.sin(rad))
                                    cv2.line(ann, (x1, y1), (x2, y2), (0, 0, 255), 2)
            
            # Crosshair ekle
            ann = add_crosshair(ann)
            
            # Mod bilgisi
            cv2.putText(ann, f"Mod: {mode}", (CANVAS_WIDTH - 150, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # Takip durumu
            if self.tracking_enabled:
                cv2.putText(ann, "TAKIP: ACIK", (CANVAS_WIDTH - 150, 55), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Hedef durumu
                if target_tracking['current_target_id'] is not None:
                    cv2.putText(ann, f"Hedef: ID {target_tracking['current_target_id']}", 
                            (CANVAS_WIDTH - 150, 80), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    
                    # Kilit durumu
                    if target_tracking['is_locked']:
                        cv2.putText(ann, "KILITLI", (CANVAS_WIDTH - 150, 105), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            else:
                cv2.putText(ann, "TAKIP: KAPALI", (CANVAS_WIDTH - 150, 55), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            
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
                print(f"Görüntü hatası: {e}")

        self.camera_manager.release()

        # Atış modu bilgisi
        if mode in ["Mod 1", "Mod 2"]:
            fire_mode_text = "OTONOM" if self.auto_fire_enabled else "MANUEL"
            fire_color = (0, 0, 255) if self.auto_fire_enabled else (0, 255, 0)
            
            cv2.putText(ann, f"Atis: {fire_mode_text}", 
                    (10, CANVAS_HEIGHT - 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, fire_color, 2)
            
            # Otonom modda merkez toleransı göster
            if self.auto_fire_enabled:
                center_x, center_y = CAMERA_WIDTH // 2, CAMERA_HEIGHT // 2
                cv2.circle(ann, (center_x, center_y), 25, (255, 255, 0), 2)
                cv2.putText(ann, "ATIS BOLGE", (center_x-60, center_y-35), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        # Yeni fonksiyonlar ekleyin:
    def set_reference_point(self):
        """Mevcut pozisyonu referans noktası olarak ayarla"""
        if self.arduino_controller.set_reference_point():
            messagebox.showinfo("Başarılı", "Referans noktası (0°) ayarlandı!")
            # Periyodik güncelleme başlat
            self.start_angle_update()

    def confirm_restricted_area(self):
        """Yasaklı alan ayarlarını onayla"""
        min_angle, max_angle = self.restricted_area_frame.get_angles()
        
        if min_angle is None or max_angle is None:
            messagebox.showerror("Hata", "Geçerli açı değerleri girin!")
            return
        
        if min_angle >= max_angle:
            messagebox.showerror("Hata", "Min açı, max açıdan küçük olmalı!")
            return
        
        self.arduino_controller.set_restricted_area(min_angle, max_angle)
        self.restricted_area_enabled = True
        self.restricted_area_frame.update_status(True, min_angle, max_angle)
        messagebox.showinfo("Başarılı", f"Yasaklı alan ayarlandı!\n{min_angle}° - {max_angle}° arası atış yasak")

    def start_angle_update(self):
        """Açı göstergesini periyodik olarak güncelle"""
        if self.confirmed_mode == "Manuel":
            self.update_angle_display()
    
    def update_angle_display(self):
        """Açı ve atış durumu göstergesini güncelle"""
        if self.confirmed_mode == "Manuel" and hasattr(self, 'restricted_area_frame'):
            # Mevcut açıyı al
            relative_yaw = self.arduino_controller.get_relative_yaw()
            self.restricted_area_frame.update_angle(relative_yaw)
            
            # Atış durumunu kontrol et
            shot_allowed = self.arduino_controller.is_shot_allowed()
            min_angle = self.arduino_controller.restricted_yaw_min
            max_angle = self.arduino_controller.restricted_yaw_max
            self.restricted_area_frame.update_shot_status(shot_allowed, min_angle, max_angle)
            
            # Manuel kontrol pozisyon güncellemesi
            if hasattr(self, 'manual_controls'):
                yaw, pitch = self.arduino_controller.get_position()
                self.manual_controls.update_position(relative_yaw, pitch)
            
            # 100ms sonra tekrar çağır
            self.update_timer = self.root.after(100, self.update_angle_display)

    def toggle_fire_mode(self):
        """Atış modunu değiştir"""
        self.auto_fire_enabled = not self.auto_fire_enabled
        
        if self.auto_fire_enabled:
            self.fire_mode_btn.config(text="OTONOM ATIŞ", bg="red")
            self.fire_info_label.config(text="Hedefe kilitlenince otomatik ateş")
        else:
            self.fire_mode_btn.config(text="MANUEL ATIŞ", bg="blue")
            self.fire_info_label.config(text="Space tuşu ile ateş edin")
        
        print(f"Atış modu: {'OTONOM' if self.auto_fire_enabled else 'MANUEL'}")

    def is_target_centered(self, bbox):
        """Hedefin merkezde olup olmadığını kontrol et"""
        if not bbox or len(bbox) != 4:
            return False
        
        x1, y1, x2, y2 = bbox
        target_center_x = (x1 + x2) // 2
        target_center_y = (y1 + y2) // 2
        
        screen_center_x = CAMERA_WIDTH // 2
        screen_center_y = CAMERA_HEIGHT // 2
        
        # Merkez toleransı (pikseller)
        center_tolerance = 25  # 25 piksel tolerans
        
        distance = ((target_center_x - screen_center_x)**2 + (target_center_y - screen_center_y)**2)**0.5
        
        return distance <= center_tolerance

    def execute_auto_fire(self):
        """Otonom atış gerçekleştir"""
        import time
        current_time = time.time()
        
        # Rate limiting - çok sık atış engelleme
        if current_time - self.last_auto_fire_time < self.auto_fire_cooldown:
            return False
        
        # Yasaklı alan kontrolü (varsa)
        if hasattr(self.arduino_controller, 'is_shot_allowed'):
            if not self.arduino_controller.is_shot_allowed():
                print("OTONOM ATIŞ ENGELLENDİ: Yasaklı alanda!")
                return False
        
        # Atış komutu gönder
        self.arduino_controller.send_command("shot")
        self.last_auto_fire_time = current_time
        print("🎯 OTONOM ATIŞ GERÇEKLEŞTİRİLDİ!")
        return True