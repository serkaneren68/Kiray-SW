import tkinter as tk
from PIL import Image, ImageTk
import cv2
from ultralytics import YOLO
import threading
import numpy as np
import pytesseract
import time

class App:
    def __init__(self, root):
        self.detected_shape = None
        self.confirmed_shape = None
        self.awaiting_confirmation = False
        self.detected_letter = None
        self.confirmed_letter = None

        self.root = root
        self.root.title("Hava Savunma Kontrol Paneli")
        self.root.configure(bg="black")
        self.root.geometry("1920x1080")
        self.running = False

        # Mode state
        self.mode = tk.StringVar(value="Manuel")
        self.confirmed_mode = "Mod 1"

        # Setup UI
        self._create_canvas()
        self._create_mode_frame()
        self._create_fe_frame()
        self._create_letter_frame()
        self._create_controls()

        # QR detector for Mod 3
        self.qr_detector = cv2.QRCodeDetector()
        # OCR (unused if using QR)
        try:
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        except:
            pass
        # YOLO for Mod 1/2
        self.model = YOLO("best2.pt")

    def _create_canvas(self):
        self.canvas = tk.Canvas(self.root, bg="black", width=780, height=475,
                                highlightthickness=2, highlightbackground="gray")
        self.canvas.place(x=30, y=30)

    def _create_mode_frame(self):
        frame = tk.Frame(self.root, bg="black", width=900, height=140)
        frame.place(x=30, y=580)
        for i, m in enumerate(["Manuel","Mod 1","Mod 2","Mod 3"]):
            tk.Radiobutton(frame, text=m, variable=self.mode, value=m,
                           font=("Arial",16), bg="black", fg="white").place(x=0 + i*175, y=5, width=150, height=40)
        self.btn_ok = tk.Button(frame, text="✔", fg="green", font=("Arial",20), command=self.confirm_mode)
        self.btn_no = tk.Button(frame, text="✖", fg="red",   font=("Arial",20), command=self.reject_mode)
        self.btn_ok.place_forget()
        self.btn_no.place_forget()
        self.mode_frame = frame
        self.mode.trace_add("write", self.on_mode_change)

    def _create_fe_frame(self):
        frame = tk.LabelFrame(self.root, text="Dost/Düşman Seçimi", bg="black", fg="limegreen", bd=2)
        self.friend_buttons = {}
        self.enemy_buttons = {}
        self.friend_color = tk.StringVar(value="yesil")
        self.enemy_color  = tk.StringVar(value="kirmizi")
        for i, clr in enumerate(["kirmizi","yesil","mavi"]):
            btn_f = tk.Radiobutton(frame, text=f"{clr.title()} Dost", variable=self.friend_color, value=clr,
                                  font=("Arial",12), command=self.check_fe_conflict, bg="black", fg="white", selectcolor="black")
            btn_e = tk.Radiobutton(frame, text=f"{clr.title()} Düşman", variable=self.enemy_color, value=clr,
                                  font=("Arial",12), command=self.check_fe_conflict, bg="black", fg="white", selectcolor="black")
            btn_f.place(x=10, y=10+i*40)
            btn_e.place(x=160, y=10+i*40)
            self.friend_buttons[clr] = btn_f
            self.enemy_buttons[clr]  = btn_e
        self.fe_frame = frame

    def _create_letter_frame(self):
        frame = tk.LabelFrame(self.root, text="Angajman Onay", bg="black", fg="dodgerblue", bd=2)
        self.letter_label = tk.Label(frame, text="Harf: —", font=("Arial", 28), fg="cyan", bg="black")
        self.shape_label  = tk.Label(frame, text="Şekil: —", font=("Arial", 20), fg="orange", bg="black")
        self.btn_accept  = tk.Button(frame, text="Angajmanı Kabul Et", font=("Arial",16), command=self.accept_engagement)
        self.letter_label.pack(pady=5)
        self.shape_label.pack(pady=5)
        self.btn_accept.pack(pady=10)
        self.letter_frame = frame

    def _create_controls(self):
        y = 700
        self.btn_start = tk.Button(self.root, text="BAŞLAT", font=("Arial",14), command=self.start)
        self.btn_stop  = tk.Button(self.root, text="DURDUR", font=("Arial",14), command=self.stop)
        self.btn_reset = tk.Button(self.root, text="RESET", font=("Arial",14), bg="purple", fg="white", command=self.reset_system)
        self.btn_start.place(x=30, y=y, width=150, height=40)
        self.btn_stop.place(x=205, y=y, width=150, height=40)
        self.btn_reset.place(x=380, y=y, width=150, height=40)

    def on_mode_change(self, *args):
        idx = ["Manuel","Mod 1","Mod 2","Mod 3"].index(self.mode.get())
        x0 = idx*175
        self.btn_ok.place(in_=self.mode_frame, x=x0, y=60, width=70, height=30)
        self.btn_no.place(in_=self.mode_frame, x=x0+80, y=60, width=70, height=30)

    def confirm_mode(self):
        self.confirmed_mode = self.mode.get()
        self.btn_ok.place_forget()
        self.btn_no.place_forget()
        self.fe_frame.place_forget()
        self.letter_frame.place_forget()
        if self.confirmed_mode == "Mod 2":
            self.fe_frame.place(x=1000, y=50, width=320, height=160)
        elif self.confirmed_mode == "Mod 3":
            # sadece onay çerçevesi
            self.letter_frame.place(x=1000, y=300, width=300, height=180)
            self.awaiting_confirmation = False
            self.detected_letter = None
            self.confirmed_letter = None
            self.detected_shape  = None
            self.confirmed_shape  = None

    def reject_mode(self):
        self.mode.set(self.confirmed_mode)
        self.btn_ok.place_forget()
        self.btn_no.place_forget()

    def reset_system(self):
        self.running = False
        time.sleep(0.1)
        self.mode.set("Mod 1")
        self.confirmed_mode = "Mod 1"
        self.btn_ok.place_forget()
        self.btn_no.place_forget()
        self.fe_frame.place_forget()
        self.letter_frame.place_forget()
        if not self.running:
            self.start()

    def check_fe_conflict(self):
        dost, dusman = self.friend_color.get(), self.enemy_color.get()
        for clr, btn in self.enemy_buttons.items(): btn.config(state="disabled" if clr==dost else "normal")
        for clr, btn in self.friend_buttons.items(): btn.config(state="disabled" if clr==dusman else "normal")

    def accept_engagement(self):
        if self.awaiting_confirmation:
            self.letter_label.config(text=f"Harf: {self.confirmed_letter}")
            self.shape_label.config(text=f"Şekil: {self.confirmed_shape}")
            status = f"Angajman: Harf:{self.confirmed_letter} Şekil:{self.confirmed_shape} KABUL EDİLDİ"
            tk.messagebox.showinfo("Onay", status)
            self.awaiting_confirmation = False

    def detect_color(self, roi):
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        h = np.mean(hsv[:,:,0])
        if h<10 or h>160: return "KIRMIZI"
        if 36<=h<=85:      return "YEŞİL"
        if 86<=h<=125:     return "MAVİ"
        return None

    def detect_shape(self, roi):
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)
        cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not cnts: return None
        c = max(cnts, key=cv2.contourArea)
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        v = len(approx)
        if v==3: return "ÜÇGEN"
        if v==4: return "KARE"
        return "DAİRE"

    def video_loop(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,780)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        while self.running:
            ret, frame = cap.read()
            if not ret: break
            mode = self.confirmed_mode
            ann = frame.copy()
            if mode in ("Manuel","Mod 1","Mod 2"):
                results = self.model(frame, imgsz=640)[0]
                for box, cls in zip(results.boxes.xyxy.cpu().numpy(), results.boxes.cls.cpu().numpy()):
                    if results.names[int(cls)]!="balloon": continue
                    x1,y1,x2,y2 = map(int, box)
                    roi=frame[y1:y2,x1:x2]
                    if mode=="Mod 2":
                        clr = self.detect_color(roi)
                        role = "DOST" if clr.lower()==self.friend_color.get() else "DÜŞMAN"
                        text=f"{clr} {role}"
                    else:
                        text="balloon"
                    cv2.rectangle(ann,(x1,y1),(x2,y2),(0,255,0),2)
                    cv2.putText(ann,text,(x1,y1-10),cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,255),2)
            else:
                # Mod 3: QR + şekil/renk
                if not self.awaiting_confirmation:
                    data, pts, _ = self.qr_detector.detectAndDecode(frame)
                    if data in ("A","B"):
                        self.detected_letter = data
                        self.confirmed_letter = data
                        self.letter_label.config(text=f"Harf: {data}")
                    # tüm frame'i şekil tespiti için ROI gibi kullan
                    shape = self.detect_shape(frame)
                    color = self.detect_color(frame)
                    if shape and color:
                        self.detected_shape = f"{color} {shape}"
                        self.confirmed_shape = self.detected_shape
                        self.shape_label.config(text=f"Şekil: {self.detected_shape}")
                    if self.confirmed_letter and self.confirmed_shape:
                        self.awaiting_confirmation = True
                # onay çerçevesi zaten açık
            # gösterim
            rgb = cv2.cvtColor(ann, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(Image.fromarray(rgb))
            self.canvas.create_image(0,0,anchor="nw",image=img)
            self.canvas.image=img
        cap.release()

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.video_loop, daemon=True).start()

    def stop(self):
        self.running = False

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()