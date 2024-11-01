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

        self.batch_size = 2
        self.payload = {
            "prompt": "IT neon style, futuristic, high contrast, cyberpunk, high resolution, 4k",
            "sampler": "Euler a",
            "seed": 1,
            "steps": 50,
            "width": 512,
            "height": 512,
            "denoising_strength": 0.5,
            "n_iter": 1,
            "batch_size": self.batch_size
        }
        # self.payload = {
        #     "prompt": "cyberpunk atmosphere, neon lights, futuristic cityscape, dark and rainy, high contrast, neon reflections on wet surfaces, sci-fi vibe",
        #     "negative_prompt": "",
        #     "seed": -1,
        #     "subseed": -1,
        #     "subseed_strength": 0,
        #     "seed_resize_from_h": -1,
        #     "seed_resize_from_w": -1,
        #     "sampler_name": "string",
        #     "batch_size": 1,
        #     "n_iter": 1,
        #     "steps": 50,
        #     "cfg_scale": 7,
        #     "width": 512,
        #     "height": 512,
        #     "restore_faces": "true",
        #     "tiling": "true",
        #     "do_not_save_samples": "false",
        #     "do_not_save_grid": "false",
        #     "eta": 0,
        #     "denoising_strength": 0.75,
        #     "s_min_uncond": 0,
        #     "s_churn": 0,
        #     "s_tmax": 0,
        #     "s_tmin": 0,
        #     "s_noise": 0,
        #     "override_settings": {},
        #     "override_settings_restore_afterwards": "true",
        #     "refiner_checkpoint": "string",
        #     "refiner_switch_at": 0,
        #     "disable_extra_networks": "false",
        #     "firstpass_image": "string",
        #     "comments": {},
        #     "resize_mode": 0,
        #     "image_cfg_scale": 0,
        #     "mask": "string",
        #     "mask_blur_x": 4,
        #     "mask_blur_y": 4,
        #     "mask_blur": 0,
        #     "mask_round": "true",
        #     "inpainting_fill": 0,
        #     "inpaint_full_res": "true",
        #     "inpaint_full_res_padding": 0,
        #     "inpainting_mask_invert": 0,
        #     "initial_noise_multiplier": 0,
        #     "latent_mask": "string",
        #     "force_task_id": "string",
        #     "sampler_index": "Euler",
        #     "include_init_images": "false",
        #     "script_name": "string",
        #     "script_args": [],
        #     "send_images": "true",
        #     "save_images": "false",
        #     "alwayson_scripts": {},
        # }

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
            edited_file_path = self.edited_photo_dir + "/" + photo_name
            cv2.imwrite(original_file_path, self.photo)
            log_info("Image saved", f"Image saved in {original_file_path}")

            process_image(original_file_path, edited_file_path, self.stable_diffusion_url, **self.payload)

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
