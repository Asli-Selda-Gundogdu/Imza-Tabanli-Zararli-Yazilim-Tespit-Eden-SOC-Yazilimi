from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from plyer import notification
import os
import hashlib as hlib
import tkinter as tk
from tkinter import messagebox
import queue
import threading

# Ana Tkinter kök penceresi
root = tk.Tk()
root.withdraw()  # Ana pencereyi gizle

# Thread'ler arasında mesaj göndermek için kuyruk
message_queue = queue.Queue()

# Yeni dosya eklendiğinde çalışacak olay sınıfı
class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:  # Sadece dosyaları kontrol et
            filename = os.path.basename(event.src_path)
            print(f"Yeni dosya indirildi: {filename}")
            # Dosyanın hash değerini kontrol et
            threading.Thread(target=check_file, args=(event.src_path,)).start()

def hash_file(filename):
    h = hlib.sha256()
    with open(filename, 'rb') as file:
        chunk = file.read(1024)
        while chunk:
            h.update(chunk)
            chunk = file.read(1024)
    return h.hexdigest()

# Ana thread'de mesaj kutusunu gösterme
def process_messages():
    while not message_queue.empty():
        msg_type, title, message = message_queue.get()
        if msg_type == "error":
            messagebox.showerror(title, message)
        elif msg_type == "warning":
            messagebox.showwarning(title, message)
        elif msg_type == "info":
            show_safe_message(title, message)  # Güvenli dosya mesajını burada gösteriyoruz
    root.after(100, process_messages)  # 100 ms sonra tekrar kontrol et

# Güvenli dosya mesajını gösteren fonksiyon
def show_safe_message(title, message):
    # Güvenli dosya bulunduğunda gösterilecek özel pop-up penceresi
    safe_window = tk.Toplevel(root)
    safe_window.title("Dosya Güvenliği")
    safe_window.geometry("300x150")
    safe_window.configure(bg="lightgreen")  # Arka plan rengini yeşil yapıyoruz

    label = tk.Label(safe_window, text=message, fg="green", bg="lightgreen", font=("Arial", 14))
    label.pack(pady=20)

    button = tk.Button(safe_window, text="Tamam", command=safe_window.destroy, bg="white", fg="black", font=("Arial", 10))
    button.pack()

    print("Güvenli dosya mesajı pop-up'ı gösterildi.")  # Bu sadece fonksiyonun çalışıp çalışmadığını kontrol etmek için

def show_danger_message(title, message):
    # Güvenli olmayan dosya bulunduğunda gösterilecek özel pop-up penceresi
    danger_window = tk.Toplevel(root)
    danger_window.title("Güvenlik Uyarısı")
    danger_window.geometry("300x150")
    danger_window.configure(bg="red")  # Arka plan rengini kırmızı yapıyoruz

    label = tk.Label(danger_window, text=message, fg="white", bg="red", font=("Arial", 12, "bold"))
    label.pack(pady=20)

    button = tk.Button(danger_window, text="Tamam", command=danger_window.destroy, bg="white", fg="black", font=("Arial", 12))
    button.pack()

    print("Güvenli olmayan dosya mesajı pop-up'ı gösterildi.")

# Dosya kontrolü
def check_file(file_path):
    try:
        hash_value = hash_file(file_path)
        print(f"Seçilen dosyanın hash değeri: {hash_value}")

        file_name = 'dataset.txt'
        if not os.path.exists(file_name):
            message_queue.put(("error", "Hata", f"Hash dosyası bulunamadı: {file_name}"))
            return

        with open(file_name, 'r') as file:
            contents = file.read()

        if hash_value in contents:
            show_danger_message("Güvenlik Uyarısı", "Dosya GÜVENLİ DEĞİLDİR!")  # Sadece kırmızı uyarı pop-up'ı
            notification.notify(
                title="Uyarı",
                message="Dosya zararlı olabilir!",
                app_name="Dosya İzleyici",
                timeout=5
            )
        else:
            show_safe_message("Dosya Güvenliği", "Dosyanız Güvenlidir.")  # Güvenli dosya mesajı
            notification.notify(
                title="Bilgi",
                message="Dosya güvenlidir.",
                app_name="Dosya İzleyici",
                timeout=5
            )
    except Exception as e:
        print(f"Bir hata oluştu: {e}")
        message_queue.put(("error", "Hata", f"Bir hata oluştu:\n{e}"))

# İzlemek istediğiniz klasör ("İndirilenler" klasörünün yolu)
indirilenler_klasoru = os.path.expanduser("~/Downloads")

# Observer oluştur ve başlat
event_handler = NewFileHandler()
observer = Observer()
observer.schedule(event_handler, indirilenler_klasoru, recursive=False)
observer.start()

print(f"{indirilenler_klasoru} klasörü izleniyor. Yeni dosyalar için uyarı alacaksınız...")

# Ana thread'de mesaj kuyruğunu işle
root.after(100, process_messages)

try:
    root.mainloop()
except KeyboardInterrupt:
    observer.stop()
observer.join()