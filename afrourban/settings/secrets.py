import os
import base64

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = "django-insecure-9s@(x)g465r$)yt^1+0b^vf2ksz_u3ez05+a!lk1qe&95+vqk3"


def get_secret(name: str, default: str = "", read_option: str = "r") -> str:

    if os.environ.get(name):
        return os.environ.get(name, default)

    try:
        with open(f"/run/secrets/{name}", read_option) as file:
            return file.read()
    except FileNotFoundError:
        return default


def decode_key(encoded_bytes: str) -> str:
    if os.environ.get("DJANGO_ENV") in ["local", "dev"]:
        return encoded_bytes
    decoded_bytes = base64.b64decode(encoded_bytes)
    return decoded_bytes.decode("utf-8")


SECRET_KEY = decode_key(get_secret("SECRET_KEY", read_option="rb"))

DJANGO_SUPERUSER_PASSWORD = get_secret("DJANGO_SUPERUSER_PASSWORD")
DJANGO_SUPERUSER_EMAIL = get_secret("DJANGO_SUPERUSER_EMAIL")
DJANGO_SUPERUSER_USERNAME = get_secret("DJANGO_SUPERUSER_USERNAME")

SQL_ENGINE = get_secret("SQL_ENGINE", "django.db.backends.postgresql")
SQL_DATABASE = get_secret("SQL_DATABASE", "afrourban")
SQL_USER = get_secret("SQL_USER", "afrourban")
SQL_PASSWORD = get_secret("SQL_PASSWORD")
SQL_HOST = get_secret("SQL_HOST")
SQL_PORT = get_secret("SQL_PORT", "5432")
