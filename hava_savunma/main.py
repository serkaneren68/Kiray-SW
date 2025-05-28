"""
TEKNOFEST Hava Savunma Sistemleri - Ana Başlatıcı
"""
import tkinter as tk
import signal
import sys
from ui.main_window import MainWindow

def signal_handler(sig, frame):
    """CTRL+C sinyalini yakala ve uygulamayı kapat"""
    print("CTRL+C algılandı. Program kapatılıyor...")
    if hasattr(signal_handler, 'app'):
        signal_handler.app.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    
    # Signal handler'a app referansını ekle
    signal_handler.app = app
    signal.signal(signal.SIGINT, signal_handler)
    
    root.mainloop()