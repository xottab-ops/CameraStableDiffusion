import tkinter as tk
import ttkbootstrap as ttk
import uuid
from tkinter import Toplevel
import cv2
from PIL import Image, ImageTk
import threading
import time
import os
from processing_service.processor import process_image
from storage_service.storage import upload_file_to_s3
from qr_service.qr_generator import generate_qr_code
from logger.logger import log_error, log_info
import configparser
import sys


class CameraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stable Diffusion Camera")
        self.root.configure(bg="#2c3e50")

        self.settings_filename = "settings.ini"
        self.s3_endpoint = ""
        self.s3_bucket_name = ""
        self.stable_diffusion_url = ""
        self.original_photo_dir = ""
        self.edited_photo_dir = ""
        self.init_settings()
        os.makedirs(self.original_photo_dir, exist_ok=True)
        os.makedirs(self.edited_photo_dir, exist_ok=True)

        self.capture_button = ttk.Button(root, text="Take a photo", command=self.take_photo)

        self.retake_button = ttk.Button(root, text="Re-photographing", command=self.reset)
        self.save_button = ttk.Button(root, text="Create image from Stable Diffusion", command=self.save_photo)

        self.label = tk.Label(root)
        self.label.pack(pady=10)
        self.camera = cv2.VideoCapture(0)
        self.capture_button.pack(pady=10)
        self.photo = None
        self.showing_photo = False

        self.update_preview()

    def init_settings(self):
        config = configparser.ConfigParser()

        if not os.path.exists(self.settings_filename):
            log_error("Unable to read settings.ini", "Config file not found.")
            sys.exit(1)

        try:
            config.read(self.settings_filename)

            self.s3_endpoint = config['DEFAULT']['S3_ENDPOINT']
            self.s3_bucket_name = config['DEFAULT']['S3_BUCKET_NAME']
            self.stable_diffusion_url = config['DEFAULT']['STABLE_DIFFUSION_URL']
            self.original_photo_dir = config['DEFAULT']['ORIGINAL_PHOTO_DIR']
            self.edited_photo_dir = config['DEFAULT']['EDITED_PHOTO_DIR']
        except configparser.Error as e:
            log_error("Unable to read settings.ini", str(e))
            sys.exit(1)
        except KeyError as e:
            log_error("Missing configuration key", f"Key missing: {e}")
            sys.exit(1)

    def update_preview(self):
        if not self.showing_photo:
            ret, frame = self.camera.read()
            if ret:
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)

                img = img.resize((int(800 * img.width / img.height), 800), Image.LANCZOS)

                img = ImageTk.PhotoImage(img)
                self.label.config(image=img)
                self.label.image = img
        self.root.after(10, self.update_preview)

    def take_photo(self):
        self.capture_button.config(state=tk.DISABLED)
        threading.Thread(target=self.capture_with_delay).start()
        self.capture_button.pack_forget()

    def capture_with_delay(self):
        time.sleep(3)
        ret, frame = self.camera.read()
        if ret:
            self.photo = frame
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img = img.resize((int(800 * img.width / img.height), 800), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)

            self.label.config(image=img)
            self.label.image = img

            self.retake_button.pack(pady=5)
            self.save_button.pack(pady=5)

            self.showing_photo = True
        else:
            log_error("Error", "Unable to create the image")
        self.capture_button.config(state=tk.NORMAL)

    def reset(self):
        self.retake_button.pack_forget()
        self.save_button.pack_forget()
        self.capture_button.pack(pady=10)
        self.photo = None
        self.showing_photo = False

    def save_photo(self):
        if self.photo is not None:
            photo_name = uuid.uuid4().hex + ".jpg"
            original_file_path = os.path.join(self.original_photo_dir, photo_name)
            cv2.imwrite(original_file_path, self.photo)
            log_info("Image saved", f"Image saved in {original_file_path}")

            edited_image = process_image(original_file_path, self.stable_diffusion_url)

            if edited_image:
                edited_file_path = self.edited_photo_dir + "/" + photo_name
                edited_image.save(edited_file_path)
                log_info("The processed image is saved", f"Image saved in {edited_file_path}")
                s3_url = upload_file_to_s3(edited_file_path, self.s3_bucket_name, self.s3_endpoint)
                if s3_url:
                    self.show_qr_code(s3_url)
            self.reset()
        else:
            log_error("Error", "No image for save")

    def show_qr_code(self, url):
        qr_image = generate_qr_code(url)
        qr_window = Toplevel(self.root)
        qr_window.title("QR Code for download image")

        img = ImageTk.PhotoImage(qr_image)
        qr_label = tk.Label(qr_window, image=img)
        qr_label.image = img
        qr_label.pack()

    def __del__(self):
        self.camera.release()


if __name__ == "__main__":
    main_root = tk.Tk()
    app = CameraApp(main_root)
    main_root.mainloop()
