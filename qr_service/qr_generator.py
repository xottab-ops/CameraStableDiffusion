import qrcode
from logger.logger import log_info


def generate_qr_code(url):
    qr = qrcode.make(url)
    log_info("QR код сгенерирован", f"Ссылка в QR коде: {url}")
    return qr
