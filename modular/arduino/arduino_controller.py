import serial
import time
from config.constants import ARDUINO_COMMANDS


class ArduinoController:
    def __init__(self, port='COM5', baudrate=9600):
        self.arduino = None
        self.last_command_time = 0
        self.command_delay = 0.1
        
        try:
            self.arduino = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2)
            print("Arduino'ya bağlandı")
        except Exception as e:
            print(f"[HATA] Arduino bağlantısı kurulamadı: {e}")
            self.arduino = None
    
    def send_command(self, direction):
        current_time = time.time()
        if current_time - self.last_command_time < self.command_delay:
            return
            
        self.last_command_time = current_time
        
        if self.arduino and direction in ARDUINO_COMMANDS:
            try:
                self.arduino.write(ARDUINO_COMMANDS[direction])
                print(f"{direction.capitalize()} komutu gönderildi")
            except Exception as e:
                print(f"Komut gönderme hatası: {e}")
    
    def close(self):
        if self.arduino:
            try:
                self.arduino.close()
            except:
                pass