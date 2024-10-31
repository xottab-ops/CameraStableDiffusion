import requests
from PIL import Image
from io import BytesIO
from logger.logger import log_error

#'http://10.61.36.18:7860/'
def process_image(file_path, stable_diffusion_url):
    try:
        with open(file_path, "rb") as file:
            response = requests.post(
                stable_diffusion_url,  # Укажите реальный URL
                files={"file": file}
            )
            if response.status_code == 200:
                return Image.open(BytesIO(response.content))
            else:
                log_error("Ошибка преобразования", f"Код ошибки: {response.status_code}")
    except Exception as e:
        log_error("Ошибка", f"Ошибка при обработке изображения: {e}")
    return None


#