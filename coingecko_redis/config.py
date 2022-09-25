import os


class Config:
    """
    Keeps configuration values
    """

    price_save_interval_sec = float(os.getenv("PRICE_SAVE_INTERVAL") or "60.0")
    redis_host = os.getenv("REDIS_HOST")
    redis_port = os.getenv("REDIS_PORT")
    redis_db = os.getenv("REDIS_DB")


config = Config()
