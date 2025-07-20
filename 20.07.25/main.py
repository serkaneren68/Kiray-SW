import sys
import os
import signal
import tkinter as tk

# ByteTrack klasör yolu ayarlama
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BT_DIR = os.path.join(BASE_DIR, "ByteTrack")
if BT_DIR not in sys.path:
    sys.path.insert(0, BT_DIR)

# ByteTrack'in var olduğunu kontrol et
if not os.path.exists(BT_DIR):
    print(f"UYARI: ByteTrack klasörü bulunamadı: {BT_DIR}")
    print("Takip özelliği çalışmayacak. ByteTrack'i indirip proje klasörüne yerleştirin.")

from gui.main_window import MainWindow


def signal_handler(sig, frame):
    print("CTRL+C algılandı. Program kapatılıyor...")
    if 'app' in globals():
        app.stop()


def main():
    # Ana pencere oluştur
    root = tk.Tk()
    
    # Uygulama örneği
    global app
    app = MainWindow(root)
    
    # CTRL+C sinyali yakalama
    signal.signal(signal.SIGINT, signal_handler)
    
    # Uygulamayı başlat
    root.mainloop()


if __name__ == "__main__":
    main()