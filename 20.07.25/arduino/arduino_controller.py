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
            print("Arduino'ya bağlandı")
            # Başlangıç ayarlarını gönder
            self.send_command("speed:50")
        except Exception as e:
            print(f"[HATA] Arduino bağlantısı kurulamadı: {e}")
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
                self.arduino.write(ARDUINO_COMMANDS[command])
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
                        self.current_pitch += step_value
                    elif cmd_type == "down":
                        self.arduino.write(f"D{step_value}\n".encode())
                        self.current_pitch -= step_value
                    elif cmd_type == "left":
                        self.arduino.write(f"L{step_value}\n".encode())
                        self.current_yaw -= step_value
                    elif cmd_type == "right":
                        self.arduino.write(f"R{step_value}\n".encode())
                        self.current_yaw += step_value
                    print(f"{cmd_type} {step_value} derece")
            
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
            
            # Arduino'dan gelen cevapları oku
            if self.arduino.in_waiting > 0:
                response = self.arduino.readline().decode('utf-8').strip()
                self.process_response(response)
                
        except Exception as e:
            print(f"Komut gönderme hatası: {e}")
    
    def send_direct_movement(self, yaw_steps, pitch_steps):
        """
        Tek komutta birden fazla adım gönder
        
        Args:
            yaw_steps: Yatay hareket adım sayısı (+ sağ, - sol)
            pitch_steps: Dikey hareket adım sayısı (+ yukarı, - aşağı)
        """
        if not self.arduino:
            return
        
        try:
            # Hareket komutunu oluştur
            # Format: M<yaw_steps>,<pitch_steps>
            command = f"M{yaw_steps},{pitch_steps}\n"
            self.arduino.write(command.encode())
            
            # Pozisyonu güncelle (tahmin)
            self.current_yaw += yaw_steps / STEPS_PER_DEGREE_YAW
            self.current_pitch += pitch_steps / STEPS_PER_DEGREE_PITCH
            
            print(f"Direkt hareket: Yaw={yaw_steps} adım, Pitch={pitch_steps} adım")
            
        except Exception as e:
            print(f"Direkt hareket gönderme hatası: {e}")
    
    def center_on_target(self, angle_x, angle_y):
        """
        Hedefe doğrudan açı değerleriyle git
        
        Args:
            angle_x: Yatay açı (derece)
            angle_y: Dikey açı (derece)
        """
        yaw_steps = int(angle_x * STEPS_PER_DEGREE_YAW)
        pitch_steps = int(angle_y * STEPS_PER_DEGREE_PITCH)
        
        self.send_direct_movement(yaw_steps, pitch_steps)
    
    def process_response(self, response):
        """Arduino'dan gelen cevapları işle"""
        # Pozisyon güncellemesi: POS:yaw,pitch
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
                print("Arduino bağlantısı kapatıldı")
            except:
                pass