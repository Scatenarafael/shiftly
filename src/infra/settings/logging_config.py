import os

from loguru import logger

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)


logger.add(os.path.join(LOG_DIR, "app.log"), format="{time:YYYY-MM-DD HH:mm:ss.SSSSSS!UTC} [{level}] {message}", filter=lambda record: "app" in record["extra"], rotation="5 MB", retention=2, level="DEBUG")

app_logger = logger.bind(app=True)
