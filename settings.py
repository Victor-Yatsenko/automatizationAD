import os
from loguru import logger
import dotenv


# logs
logger.enable(__name__)
logger.add(".LOGS/log_{time:DD}.{time:MM}.{time:YYYY}.log",
           level="WARNING",
           rotation="1 month",
           retention="3 month",
           compression="zip",
           encoding="utf-8",
           format="{time:DD.MM.YYYY at HH:mm:ss} | {level} | file {file}:{line} | {message}"
           )
logger.opt(raw=True).info("\n""\n\n")


# env
try:
    logger.info("Отримання змінних оточення")
    dotenv.load_dotenv()
    CLIENT_ID     = os.environ["CLIENT_ID"]
    TENANT_ID     = os.environ["TENANT_ID"]
    CLIENT_SECRET = os.environ["CLIENT_SECRET"]
    LAST_ID_FILE  = os.environ.get("LAST_ID_FILE", "last_id.txt")
    POWER_AUTOMATE_SECRET_TOKEN  = os.environ["POWER_AUTOMATE_SECRET_TOKEN"]
    HOST = os.environ["HOST"]
    PORT = os.environ["PORT"]
    CREATE_USER_URL = os.environ["CREATE_USER_URL"]
    ENABLE_USER_URL = os.environ["ENABLE_USER_URL"]
except Exception as e:
    print(logger.critical(f"Змінні оточення {e} не отримано, перевірте файл .env"))

