import tkinter as tk

def start_callback():
    print("BAŞLATILDI")

root = tk.Tk()
root.geometry("500x200")
canvas = tk.Canvas(root, bg="black")
canvas.pack(fill="both", expand=True)

# Oval şekil (başlat butonu gibi)
oval = canvas.create_oval(20, 30, 150, 70, fill="green", outline="white", width=2)

# Yazı
text = canvas.create_text(85, 50, text="BAŞLAT", fill="white", font=("Arial", 14, "bold"))

# Oval şekle tıklama efekti ekle
def on_click(event):
    print("BAŞLATILDI")  # yerine start_callback() çağrısı olur
canvas.tag_bind(oval, "<Button-1>", on_click)
canvas.tag_bind(text, "<Button-1>", on_click)

root.mainloop()
