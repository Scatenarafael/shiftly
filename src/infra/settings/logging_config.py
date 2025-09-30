from loguru import logger

logger.add("/logs/app.log", format="{time:YYYY-MM-DD HH:mm:ss.SSSSSS!UTC} [{level}] {message}", filter=lambda record: "app" in record["extra"], rotation="5 MB", retention=2, level="DEBUG")

app_logger = logger.bind(app=True)
