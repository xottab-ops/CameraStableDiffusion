import random

import requests
import base64
import json
import urllib.request
from PIL import Image
from io import BytesIO
from logger.logger import log_error


def encode_file_to_base64(path):
    with open(path, 'rb') as file:
        return base64.b64encode(file.read()).decode('utf-8')


def decode_and_save_base64(base64_str, save_path):
    with open(save_path, "wb") as file:
        file.write(base64.b64decode(base64_str))


def call_api(webui_server_url, api_endpoint, **payload):
    data = json.dumps(payload).encode('utf-8')
    request = urllib.request.Request(
        f'{webui_server_url}/{api_endpoint}',
        headers={'Content-Type': 'application/json'},
        data=data,
    )
    response = urllib.request.urlopen(request)
    return json.loads(response.read().decode('utf-8'))


def process_image(original_file_path: str, edited_file_path: str, stable_diffusion_url: str, **payload: str):
    try:
        with open(original_file_path, "rb") as file:
            payload["init_images"] = [
                encode_file_to_base64(original_file_path)
            ]
            payload["seed"] = random.randint(1, 9999999999)
            response = call_api(stable_diffusion_url, 'sdapi/v1/img2img', **payload)
            for index, image in enumerate(response.get('images')):
                decode_and_save_base64(image, edited_file_path)
    except Exception as e:
        log_error("Error", f"Error in image processing: {e}")
    return None


#