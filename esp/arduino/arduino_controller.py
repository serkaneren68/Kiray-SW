import serial
import time
import re
from config.constants import ARDUINO_COMMANDS, STEPS_PER_DEGREE_YAW, STEPS_PER_DEGREE_PITCH


class ArduinoController:
    def __init__(self, port='COM3', baudrate=9600):
        self.arduino = None
        self.last_command_time = 0
        self.command_delay = 0.03  # 30ms delay
        self.current_yaw = 0
        self.current_pitch = 0
        self.current_speed = 50
        
        try:
            self.arduino = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)
            print("ESP8266'ya bağlandı")
            # Başlangıç ayarlarını gönder
            self.send_command("speed:50")
        except Exception as e:
            print(f"[HATA] ESP8266 bağlantısı kurulamadı: {e}")
            self.arduino = None
    
    def send_command(self, command):
        current_time = time.time()
        if current_time - self.last_command_time < self.command_delay:
            return
            
        self.last_command_time = current_time
        
        if not self.arduino:
            return
        
        try:
            # Basit komutlar (eski sistem)
            if command in ARDUINO_COMMANDS:
                # Yeni satır karakteri ekle
                cmd_with_newline = ARDUINO_COMMANDS[command] + b'\n'
                self.arduino.write(cmd_with_newline)
                print(f"{command.capitalize()} komutu gönderildi")
            
            # Gelişmiş komutlar
            elif ":" in command:
                cmd_type, value = command.split(":", 1)
                
                if cmd_type == "speed":
                    # Hız komutu: V<hız_değeri>
                    self.arduino.write(f"V{value}\n".encode())
                    self.current_speed = int(value)
                    print(f"Hız ayarlandı: {value}%")
                
                elif cmd_type in ["up", "down", "left", "right"]:
                    # Adım komutu: <yön>:<adım>
                    step_value = int(value)
                    if cmd_type == "up":
                        self.arduino.write(f"U{step_value}\n".encode())
                    elif cmd_type == "down":
                        self.arduino.write(f"D{step_value}\n".encode())
                    elif cmd_type == "left":
                        self.arduino.write(f"L{step_value}\n".encode())
                    elif cmd_type == "right":
                        self.arduino.write(f"R{step_value}\n".encode())
                    print(f"{cmd_type} {step_value} adım")
            
            elif command == "home":
                # Home komutu
                self.arduino.write(b"H\n")
                self.current_yaw = 0
                self.current_pitch = 0
                print("Home pozisyonuna dönülüyor")
            
            elif command == "stop":
                # Stop komutu
                self.arduino.write(b"X\n")
                print("Motorlar durduruldu")
            
            # ESP'den gelen cevapları oku
            if self.arduino.in_waiting > 0:
                response = self.arduino.readline().decode('utf-8').strip()
                self.process_response(response)
                
        except Exception as e:
            print(f"Komut gönderme hatası: {e}")
    
    def send_direct_movement(self, yaw_steps, pitch_steps):
        """
        ESP8266'ya eş zamanlı motor hareketi için komut gönder
        
        Args:
            yaw_steps: Yatay hareket adım sayısı (+ sağ, - sol)
            pitch_steps: Dikey hareket adım sayısı (+ yukarı, - aşağı)
        """
        if not self.arduino:
            return
        
        try:
            # ESP için hareket komutu - Format: M<yaw_steps>,<pitch_steps>
            # ESP kodu zaten eş zamanlı hareket yapıyor
            command = f"M{yaw_steps},{pitch_steps}\n"
            self.arduino.write(command.encode())
            
            # Pozisyonu güncelle (tahmin)
            self.current_yaw += yaw_steps / STEPS_PER_DEGREE_YAW
            self.current_pitch += pitch_steps / STEPS_PER_DEGREE_PITCH
            
            print(f"ESP'ye gönderildi - Yaw: {yaw_steps}, Pitch: {pitch_steps} adım (eş zamanlı)")
            
        except Exception as e:
            print(f"ESP hareket gönderme hatası: {e}")
    
    def center_on_target(self, angle_x, angle_y):
        """
        Hedefe doğrudan açı değerleriyle git (ESP için)
        
        Args:
            angle_x: Yatay açı (derece)
            angle_y: Dikey açı (derece)
        """
        yaw_steps = int(angle_x * STEPS_PER_DEGREE_YAW)
        pitch_steps = int(angle_y * STEPS_PER_DEGREE_PITCH)
        
        # ESP'ye eş zamanlı hareket komutu gönder
        self.send_direct_movement(yaw_steps, pitch_steps)
    
    def process_response(self, response):
        """ESP'den gelen cevapları işle"""
        if response:
            print(f"ESP: {response}")
            
        # Pozisyon güncellemesi varsa işle
        if response.startswith("POS:"):
            try:
                pos_data = response[4:].split(",")
                self.current_yaw = float(pos_data[0])
                self.current_pitch = float(pos_data[1])
                print(f"Pozisyon: Yaw={self.current_yaw}, Pitch={self.current_pitch}")
            except:
                pass
    
    def get_position(self):
        """Mevcut pozisyonu döndür"""
        return self.current_yaw, self.current_pitch
    
    def close(self):
        if self.arduino:
            try:
                # Motorları durdur
                self.arduino.write(b'X\n')
                time.sleep(0.1)
                self.arduino.close()
                print("ESP8266 bağlantısı kapatıldı")
            except:
                pass