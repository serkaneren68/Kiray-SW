import serial
import time
import re
from config.constants import ARDUINO_COMMANDS, STEPS_PER_DEGREE_YAW, STEPS_PER_DEGREE_PITCH


class ArduinoController:
    def __init__(self, port='COM3', baudrate=9600):
        self.arduino = None
        self.last_command_time = 0
        self.command_delay = 0.03
        self.current_yaw = 0.0  # Float olarak başlat
        self.current_pitch = 0.0
        self.current_speed = 50
        
        # Yasaklı alan değişkenleri
        self.reference_yaw = 0.0
        self.restricted_area_enabled = False
        self.restricted_yaw_min = -15
        self.restricted_yaw_max = 15
        
        try:
            self.arduino = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)
            print("ESP8266'ya bağlandı")
            self.send_command("speed:50")
        except Exception as e:
            print(f"[HATA] ESP8266 bağlantısı kurulamadı: {e}")
            self.arduino = None
    
    def set_reference_point(self):
        """Mevcut pozisyonu referans (0) noktası olarak ayarla"""
        self.reference_yaw = self.current_yaw
        print(f"Referans noktası ayarlandı: {self.reference_yaw}°")
        print(f"Mevcut mutlak pozisyon: {self.current_yaw}°")
        return True
    
    def get_relative_yaw(self):
        """Referans noktasına göre yaw açısını döndür"""
        relative = self.current_yaw - self.reference_yaw
        print(f"[DEBUG] Mutlak: {self.current_yaw:.1f}°, Referans: {self.reference_yaw:.1f}°, Göreceli: {relative:.1f}°")
        return relative
    
    def set_restricted_area(self, yaw_min, yaw_max):
        """Yasaklı alan sınırlarını ayarla"""
        self.restricted_yaw_min = yaw_min
        self.restricted_yaw_max = yaw_max
        self.restricted_area_enabled = True
        print(f"Yasaklı alan ayarlandı: {yaw_min}° ile {yaw_max}° arası")
    
    def is_shot_allowed(self):
        """Mevcut pozisyonda atış izni var mı kontrol et"""
        if not self.restricted_area_enabled:
            return True
        
        relative_yaw = self.get_relative_yaw()
        
        # Yasaklı alanda mı kontrolü
        if self.restricted_yaw_min <= relative_yaw <= self.restricted_yaw_max:
            print(f"ATIŞ ENGELLENDİ! Mevcut açı: {relative_yaw:.1f}° (Yasaklı: {self.restricted_yaw_min}° - {self.restricted_yaw_max}°)")
            return False
        
        return True
    
    def send_command(self, command):
        current_time = time.time()
        if current_time - self.last_command_time < self.command_delay:
            return
            
        self.last_command_time = current_time
        
        if not self.arduino:
            return
        
        try:
            # ATIŞ KOMUTU KONTROLÜ
            if command == "shot":
                if not self.is_shot_allowed():
                    return  # Atış engellendi
                    
            # Basit komutlar (SÜREKLİ MOD İÇİN)
            if command in ARDUINO_COMMANDS:
                cmd_with_newline = ARDUINO_COMMANDS[command] + b'\n'
                self.arduino.write(cmd_with_newline)
                print(f"{command.capitalize()} komutu gönderildi")
                
                # SÜREKLİ MOD İÇİN POZİSYON GÜNCELLEMESİ
                # Arduino kodunda moveMotors(80, 0) gibi sabit değerler var
                if command == "right":
                    self.current_yaw += 80 / STEPS_PER_DEGREE_YAW  # 80 adım
                    print(f"Sağa hareket - Yeni yaw: {self.current_yaw:.2f}°")
                elif command == "left":
                    self.current_yaw -= 80 / STEPS_PER_DEGREE_YAW
                    print(f"Sola hareket - Yeni yaw: {self.current_yaw:.2f}°")
                elif command == "up":
                    self.current_pitch += 80 / STEPS_PER_DEGREE_PITCH
                    print(f"Yukarı hareket - Yeni pitch: {self.current_pitch:.2f}°")
                elif command == "down":
                    self.current_pitch -= 80 / STEPS_PER_DEGREE_PITCH
                    print(f"Aşağı hareket - Yeni pitch: {self.current_pitch:.2f}°")
            
            # Gelişmiş komutlar (ADIM MODU İÇİN)
            elif ":" in command:
                cmd_type, value = command.split(":", 1)
                
                if cmd_type == "speed":
                    self.arduino.write(f"V{value}\n".encode())
                    self.current_speed = int(value)
                    print(f"Hız ayarlandı: {value}%")
                
                elif cmd_type in ["up", "down", "left", "right"]:
                    step_value = int(value)
                    
                    # ADIM MODU KOMUTLARINI ARDUINO'YA GÖNDER
                    if cmd_type == "up":
                        # Arduino'ya M komutu olarak gönder
                        self.send_direct_movement(0, step_value)
                    elif cmd_type == "down":
                        self.send_direct_movement(0, -step_value)
                    elif cmd_type == "left":
                        self.send_direct_movement(-step_value, 0)
                    elif cmd_type == "right":
                        self.send_direct_movement(step_value, 0)
            
            elif command == "home":
                self.arduino.write(b"H\n")
                self.current_yaw = 0.0
                self.current_pitch = 0.0
                print("Home pozisyonuna dönülüyor")
            
            elif command == "stop":
                self.arduino.write(b"X\n")
                print("Motorlar durduruldu")
                
        except Exception as e:
            print(f"Komut gönderme hatası: {e}")
    
    def send_direct_movement(self, yaw_steps, pitch_steps):
        """ESP8266'ya eş zamanlı motor hareketi için komut gönder"""
        if not self.arduino:
            return
        
        try:
            command = f"M{yaw_steps},{pitch_steps}\n"
            self.arduino.write(command.encode())
            
            # POZISYON GÜNCELLEMESİ ÖNEMLİ!
            yaw_change = yaw_steps / STEPS_PER_DEGREE_YAW
            pitch_change = pitch_steps / STEPS_PER_DEGREE_PITCH
            
            self.current_yaw += yaw_change
            self.current_pitch += pitch_change
            
            print(f"Direkt hareket: Yaw={yaw_steps} adım ({yaw_change:.2f}°), Pitch={pitch_steps} adım ({pitch_change:.2f}°)")
            print(f"Yeni pozisyon - Yaw: {self.current_yaw:.2f}°, Pitch: {self.current_pitch:.2f}°")
            
        except Exception as e:
            print(f"Direkt hareket gönderme hatası: {e}")
    
    def get_position(self):
        """Mevcut pozisyonu döndür"""
        return self.current_yaw, self.current_pitch
    
    def close(self):
        if self.arduino:
            try:
                self.arduino.write(b'X\n')
                time.sleep(0.1)
                self.arduino.close()
                print("ESP8266 bağlantısı kapatıldı")
            except:
                pass