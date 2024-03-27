import validators
from urllib.parse import urlparse


def normalize_url(url):
    parsed_url = urlparse(url)
    normalize_url = f'{parsed_url.scheme}://{parsed_url.netloc}'
    return normalize_url


def validate(url):
    errors = []
    if len(url) > 255:
        errors.append("URL превышает 255 символов")
    if not validators.url(url):
        errors.append("Некорректный URL")
    if not url:
        errors.append("URL обязателен")
    return errors
