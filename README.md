import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog
import hashlib as hlib
import os
from PIL import ImageTk, Image

# Dosya hash hesaplama
def hash_file(filename):
    h = hlib.sha256()
    with open(filename, 'rb') as file:
        chunk = file.read(1024)
        while chunk:
            h.update(chunk)
            chunk = file.read(1024)
    return h.hexdigest()

# Özel mesaj kutusu
def custom_messagebox(title, message, bg_color="white"):
    msg_window = tk.Toplevel()
    msg_window.title(title)
    msg_window.configure(bg=bg_color)
    msg_window.geometry("300x150")
    msg_window.resizable(False, False)

    label = tk.Label(msg_window, text=message, bg=bg_color, fg="black", font=("Arial", 12), wraplength=280)
    label.pack(pady=20)

    btn_close = tk.Button(msg_window, text="Tamam", command=msg_window.destroy, bg="white", fg="black")
    btn_close.pack(pady=10)

    # `mainloop()` kaldırıldı. Tkinter zaten ana olay döngüsünü yönetiyor.
    msg_window.grab_set()

# Dosya kontrolü
def check_file(file_path):
    try:
        hash_value = hash_file(file_path)
        print(f"Seçilen dosyanın hash değeri: {hash_value}")

        file_name = 'dataset.txt'
        if not os.path.exists(file_name):
            custom_messagebox("Hata", f"Hash dosyası bulunamadı: {file_name}", bg_color="red")
            return

        with open(file_name, 'r') as file:
            contents = file.read()

        if hash_value in contents:
            custom_messagebox("Uyarı", "İndirdiğiniz Dosya Zararlı!!", bg_color="red")
        else:
            custom_messagebox("Bilgi", "Dosyanız Güvenli!", bg_color="lightgreen")
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
        custom_messagebox("Hata", f"Bir hata oluştu:\n{e}", bg_color="red")

# Ana ekran
def file_selection_screen():
    def drop_file(event):
        file_path = event.data.strip()  # Sürüklenen dosya yolunu al
        file_path = file_path.strip("{}")  # `{}` karakterlerinden temizle (bazı platformlarda gerekebilir)
        if os.path.isfile(file_path):
            check_file(file_path)
        else:
            custom_messagebox("Hata", "Sürüklenen dosya geçerli değil!", bg_color="red")

    def select_file():
        file_path = filedialog.askopenfilename(
            title="Bir dosya seçin",
            filetypes=(("Tüm Dosyalar", "*.*"),)
        )
        if file_path:
            check_file(file_path)

    # Ana pencereyi oluştur
    file_window = TkinterDnD.Tk()
    file_window.title("Dosya Kontrolü")
    file_window.geometry("400x300")
    file_window.resizable(False, False)

    # Arka plan resmini yükle
    bg_image = Image.open("final_tighter_shield_pattern.png")
    bg_image = bg_image.resize((400, 300))
    bg_photo = ImageTk.PhotoImage(bg_image)

    # Canvas oluştur
    canvas = tk.Canvas(file_window, width=400, height=300)
    canvas.pack(fill="both", expand=True)

    # Arka plan resmini canvas'a yerleştir
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")

    # Canvas'a yazı ekle ve ortala
    canvas.create_text(
        200, 100,
        text="Dosyanızı sürükleyin veya bir dosya seçin.",
        font=("Arial", 13, "bold"),
        fill="black",
        width=350
    )

    # Dosya seçme butonu
    btn_select_file = tk.Button(
        file_window,
        text="Dosya Seç",
        command=select_file,
        bg="white",
        font=("Arial", 12)
    )
    btn_select_file.place(relx=0.5, rely=0.65, anchor="center")

    # Drag and Drop fonksiyonları
    file_window.drop_target_register(DND_FILES)
    file_window.dnd_bind('<<Drop>>', drop_file)

    file_window.mainloop()

if __name__ == "__main__":
    file_selection_screen()
