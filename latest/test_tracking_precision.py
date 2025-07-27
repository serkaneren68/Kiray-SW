# test_tracking_precision.py
import time
from arduino.arduino_controller import ArduinoController

arduino = ArduinoController()

print("Takip Hassasiyet Testi")
print("="*40)

# Test 1: 90 derece dönüş
print("Test 1: 90 derece sağa dönüş")
steps_90_degree = int(90 * 2.22)  # 200 adım
arduino.send_direct_movement(steps_90_degree, 0)
time.sleep(3)

print(f"90 derece için {steps_90_degree} adım gönderildi")
input("Doğru mu? (Enter)")

# Test 2: Küçük düzeltme
print("\nTest 2: 5 derece sol düzeltme")
steps_5_degree = int(5 * 2.22)  # 11 adım
arduino.send_direct_movement(-steps_5_degree, 0)

arduino.close()