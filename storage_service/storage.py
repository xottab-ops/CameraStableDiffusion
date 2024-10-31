from logger.logger import log_info, log_error
import boto3
import uuid


def upload_file_to_s3(file_path, bucket_name, endpoint_url):
    s3 = boto3.client(
        's3',
        endpoint_url=endpoint_url)
    object_name = file_path.split("/")[-1]
    try:
        s3.upload_file(file_path, bucket_name, object_name)
        s3_url = f"https://storage.yandexcloud.net/{bucket_name}/{object_name}"
        log_info("Загрузка успешна", f"Файл загружен в S3: {s3_url}")
        return s3_url
    except Exception as e:
        log_error("Ошибка загрузки в S3", str(e))
        return None


    