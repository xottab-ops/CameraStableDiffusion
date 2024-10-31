import requests
from PIL import Image
from io import BytesIO
from logger.logger import log_error


def process_image(file_path, stable_diffusion_url):
    try:
        with open(file_path, "rb") as file:
            response = requests.post(
                stable_diffusion_url,
                files={"file": file}
            )
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
            else:
                log_error("Conversion error", f"Status Error: {response.status_code}")
    except Exception as e:
        log_error("Error", f"Error in image processing: {e}")
    return None


#