import qrcode
from logger.logger import log_info


def generate_qr_code(url):
    qr = qrcode.make(url)
    log_info("QR Code was generated", f"URL in QR Code: {url}")
    return qr
