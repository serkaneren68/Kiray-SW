import serial
import time
import re
from config.constants import ARDUINO_COMMANDS


class ArduinoController:
    def __init__(self, port='COM3', baudrate=9600):
        self.arduino = None
        self.last_command_time = 0
        self.command_delay = 0.03  # 50ms delay
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
        if not self.arduino:
            return
        
        try:
            # Mod 1 için hassas hareket
            if hasattr(self, 'current_mode') and self.current_mode == "Mod 1":
                # Daha yavaş ve hassas hareket için
                if command in ['up', 'down', 'left', 'right']:
                    # Küçük adımlarla hareket
                    self.arduino.write(f"{command[0].upper()}5\n".encode())  # 5 derece
                    return
            
            # Normal komutlar
            if command in ARDUINO_COMMANDS:
                self.arduino.write(ARDUINO_COMMANDS[command])
                print(f"[Arduino] Komut: {command}")
            elif command == "stop":
                self.arduino.write(b'X')
            else:
                self.arduino.write(f"{command}\n".encode())
                
        except Exception as e:
            print(f"Komut gönderme hatası: {e}")
    
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
                self.arduino.write(b'X')
                time.sleep(0.1)
                self.arduino.close()
                print("Arduino bağlantısı kapatıldı")
            except:
                pass