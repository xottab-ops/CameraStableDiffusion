import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def log_error(title, message):
    logging.error(f"{title}: {message}")


def log_info(title, message):
    logging.info(f"{title}: {message}")
