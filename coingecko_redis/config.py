import os


class Config:
    """
    Keeps configuration values
    """
    price_save_interval_sec = os.getenv("PRICE_SAVE_INTERVAL")
    redis_host = os.getenv("REDIS_HOST")
    redis_port = os.getenv("REDIS_PORT")
    redis_db = os.getenv("REDIS_DB")


config = Config()
