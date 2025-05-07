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
        self.friend_buttons = {}
        self.enemy_buttons  = {}
        self.root = root
        self.root.title("Hava Savunma Kontrol Paneli")
        self.root.configure(bg="black")
        self.root.geometry("1920x1080")
        self.running = False


        # Mode state
        self.mode = tk.StringVar(value="Manuel")
        self.confirmed_mode = "Mod 1"
        self.awaiting_letter = False
        self.detected_letter = None
        self.confirmed_letter = None

        # Color state
        self.friend_color = tk.StringVar(value="yesil")
        self.enemy_color  = tk.StringVar(value="kirmizi")

        # Tesseract config
        try:
            pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        except:
            pass

        # 1) Live view canvas
        self.canvas = tk.Canvas(root, bg="black", width=780, height=475,
                                highlightthickness=2, highlightbackground="gray")
        self.canvas.place(x=30, y=30)

        # 2) Mode selection frame
        self.mode_frame = tk.Frame(root, bg="black", highlightthickness=0, highlightbackground="darkred",
                                   width=900, height=140)
        self.mode_frame.place(x=30, y=580)
        for i, m in enumerate(["Manuel","Mod 1","Mod 2","Mod 3"]):
            tk.Radiobutton(self.mode_frame, text=m, variable=self.mode, value=m,
                           font=("Arial",16)).place(x=0 + i*175, y=5, width=150, height=40)

        self.btn_ok = tk.Button(self.mode_frame, text="✔", fg="green", font=("Arial",20),
                                command=self.confirm_mode)
        self.btn_no = tk.Button(self.mode_frame, text="✖", fg="red",   font=("Arial",20),
                                command=self.reject_mode)
        self.btn_ok.place_forget()
        self.btn_no.place_forget()
        self.mode.trace_add("write", self.on_mode_change)

        # 5) Friend/enemy frame top-right
        self.fe_frame = tk.LabelFrame(root, text="Dost / Düşman Seçimi (5)", bg="black",
                                      fg="limegreen", labelanchor="n", bd=2)
        for i, clr in enumerate(["kirmizi","yesil","mavi"]):
            btn_f = tk.Radiobutton(self.fe_frame, text=clr.title()+" Dost",
                                variable=self.friend_color, value=clr,
                                font=("Arial",12), command=self.check_fe_conflict,
                                bg="black", fg="white", selectcolor="black")
            btn_f.place(x=10, y=10+i*40)
            self.friend_buttons[clr] = btn_f

            btn_e = tk.Radiobutton(self.fe_frame, text=clr.title()+" Düşman",
                                variable=self.enemy_color, value=clr,
                                font=("Arial",12), command=self.check_fe_conflict,
                                bg="black", fg="white", selectcolor="black")
            btn_e.place(x=160, y=10+i*40)
            self.enemy_buttons[clr] = btn_e


        # 6) Letter confirm frame mid-right
        self.letter_frame = tk.LabelFrame(root, text="Harf Onay (6)", bg="black",
                                          fg="dodgerblue", labelanchor="n", bd=2)
        self.letter_label = tk.Label(self.letter_frame, text="—", font=("Arial", 28))
        self.shape_label  = tk.Label(self.letter_frame, text="—", font=("Arial", 20), fg="orange")
        self.btn_letter_ok = tk.Button(self.letter_frame, text="Onayla",
                                        font=("Arial",16), command=self.confirm_letter_and_shape)
        self.letter_label.pack(pady=5)
        self.shape_label.pack(pady=5)
        self.btn_letter_ok.pack(pady=10)
        self.letter_frame.place_forget()

        # 3+4) Control buttons below modes
        y_btn = 700
        self.btn_start = tk.Button(root, text="BAŞLAT", font=("Arial",14), command=self.start)
        self.btn_stop  = tk.Button(root, text="DURDUR", font=("Arial",14), command=self.stop)
        self.btn_reset = tk.Button(root, text="RESET",  font=("Arial",14),
                                    bg="purple", fg="white", command=self.reset_system)
        self.btn_start.place(x=30, y=y_btn, width=150, height=40)
        self.btn_stop .place(x=205, y=y_btn, width=150, height=40)
        self.btn_reset.place(x=380, y=y_btn, width=150, height=40)

        # YOLO model & OCR
        self.model = YOLO("best6.pt")
        self.ocr_conf = r"--oem 3 --psm 6"

    def on_mode_change(self, *args):
        idx = ["Manuel","Mod 1","Mod 2","Mod 3"].index(self.mode.get())
        x0 = idx*175
        self.btn_ok.place(in_=self.mode_frame, x=x0,     y=60, width=70, height=30)
        self.btn_no.place(in_=self.mode_frame, x=x0+80, y=60, width=70, height=30)

    def confirm_mode(self):
        self.confirmed_mode = self.mode.get()
        self.btn_ok.place_forget()
        self.btn_no.place_forget()
        self.fe_frame.place_forget()
        self.letter_frame.place_forget()
        if self.confirmed_mode == "Mod 2":
            self.fe_frame.place(x=1000, y=50, width=320, height=160)
        if self.confirmed_mode == "Mod 3":
            self.letter_frame.place(x=1000, y=300, width=300, height=180)
            self.awaiting_letter = False
            self.detected_letter = None
            self.confirmed_letter = None

    def reject_mode(self):
        self.mode.set(self.confirmed_mode)
        self.btn_ok.place_forget()
        self.btn_no.place_forget()

    def reset_system(self):
        # Force stop and restart camera loop
        self.running = False
        time.sleep(0.1)
        self.mode.set("Mod 1")
        self.confirmed_mode = "Mod 1"
        self.btn_ok.place_forget()
        self.btn_no.place_forget()
        self.fe_frame.place_forget()
        self.letter_frame.place_forget()
        # Restart if needed
        if not self.running:
            self.start()

    def check_fe_conflict(self):
        dost = self.friend_color.get()
        dusman = self.enemy_color.get()

        # Dost ile çakışan düşman seçeneklerini devre dışı bırak
        for clr, btn in self.enemy_buttons.items():
            if clr == dost:
                btn.config(state="disabled")
            else:
                btn.config(state="normal")

        # Düşman ile çakışan dost seçeneklerini devre dışı bırak
        for clr, btn in self.friend_buttons.items():
            if clr == dusman:
                btn.config(state="disabled")
            else:
                btn.config(state="normal")


    def confirm_letter_and_shape(self):
        if self.awaiting_confirmation and self.detected_letter and self.detected_shape:
            self.confirmed_letter = self.detected_letter
            self.confirmed_shape  = self.detected_shape
            self.awaiting_confirmation = False
            self.letter_frame.place_forget()


    def detect_color(self, roi):
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        h = np.mean(hsv[:,:,0])
        if h<10 or h>160: return "kirmizi"
        if 36<=h<=85:      return "yesil"
        if 86<=h<=125:     return "mavi"
        return "belirsiz"

    def detect_shape(self, roi):
        """ROI içindeki en büyük konturu alıp poli­gonunu köşe sayısına göre sınıflandırır."""
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)
        cnts, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not cnts:
            return None
        c = max(cnts, key=cv2.contourArea)
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.04 * peri, True)
        verts = len(approx)
        if verts == 3:
            return "üçgen"
        elif verts == 4:
            x, y, w, h = cv2.boundingRect(approx)
            ar = w / float(h)
            return "kare" if 0.9 <= ar <= 1.1 else "dikdörtgen"
        else:
            return "daire"

    def video_loop(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 780)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break
            ann = frame.copy()
            results = self.model(frame, imgsz=640)[0]

            for box, cls in zip(results.boxes.xyxy.cpu().numpy(), results.boxes.cls.cpu().numpy()):
                x1, y1, x2, y2 = map(int, box)
                if results.names[int(cls)] != "balloon":
                    continue

                # ROI oluştur
                roi = frame[y1:y2, x1:x2]

                # Şekil tespiti yap
                shape = self.detect_shape(roi)

                # Renk tespiti yap
                color = self.detect_color(roi)

                # Yazıyı oluştur
                text = ""
                if color:
                    text += color
                if shape:
                    if text:
                        text += " "
                    text += shape

                mode = self.confirmed_mode
                if mode in ("Manuel", "Mod 1"):
                    text = "balloon"
                elif mode == "Mod 2":
                    roi = frame[y1:y2, x1:x2]
                    clr = self.detect_color(roi)
                    role = "DOST" if clr == self.friend_color.get() else (
                        "DÜŞMAN" if clr == self.enemy_color.get() else "?")
                    text = f"balloon ({clr}, {role})"
                else:
                    if not self.awaiting_confirmation:
                        roi = frame[y1:y2, x1:x2]
                        txt = pytesseract.image_to_string(roi, config=self.ocr_conf).strip()
                        txt = "".join(c for c in txt if c.isalpha())
                        if txt in ("A", "B"):
                            self.detected_letter = txt
                            self.letter_label.config(text=f"Harf: {txt}")

                        clr = self.detect_color(roi)
                        self.detected_shape = f"{clr} BALON"
                        self.shape_label.config(text=f"Şekil: {self.detected_shape}")

                        if self.detected_letter and self.detected_shape:
                            self.awaiting_confirmation = True
                            self.letter_frame.place(x=1420, y=300, width=300, height=180)
                            continue
                    if self.awaiting_letter:
                        text = f"Onay bekleniyor: {self.detected_letter}"
                    else:
                        text = f"Harf: {self.confirmed_letter or '-'}"

                cv2.rectangle(ann, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(ann, text, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

            rgb = cv2.cvtColor(ann, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(Image.fromarray(rgb))
            self.canvas.create_image(0, 0, anchor="nw", image=img)
            self.canvas.image = img

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