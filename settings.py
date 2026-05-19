import os
from loguru import logger
import dotenv


# logs
logger.enable(__name__)
logger.add(".LOGS/log_{time:DD}.{time:MM}.{time:YYYY}.log",
           level="INFO",
           rotation="1 month",
           retention="3 month",
           compression="zip",
           encoding="utf-8",
           format="{time:DD.MM.YYYY at HH:mm:ss} | {level} | file {file}:{line} | {message}"
           )
logger.opt(raw=True).info("\n""\n\n")


try:
    # env
    logger.info("Отримання змінних оточення")
    dotenv.load_dotenv()
    CLIENT_ID     = os.environ["CLIENT_ID"]
    TENANT_ID     = os.environ["TENANT_ID"]
    CLIENT_SECRET = os.environ["CLIENT_SECRET"]
    POWER_AUTOMATE_SECRET_TOKEN  = os.environ["POWER_AUTOMATE_SECRET_TOKEN"]
    HOST = os.environ["HOST"]
    PORT = os.environ["PORT"]
    CREATE_USER_URL = os.environ["CREATE_USER_URL"]
    DISABLE_USER_URL = os.environ["DISABLE_USER_URL"]
    SENDER_EMAIL = os.environ["SENDER_EMAIL"]
    RECIPIENT_EMAIL = os.environ["RECIPIENT_EMAIL"]
    TEAMS_WEBHOOK_URL = os.environ["TEAMS_WEBHOOK_URL"]

    # no env variables
    PATCH_EASY_START_FRONT_OFFICE_DOCX = "create_user\\easy-start-docx\\easy-start-front-office.docx"
    PATCH_EASY_START_BACK_OFFICE_DOCX = "create_user\\easy-start-docx\\easy-start-back-office.docx"
    AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
    SCOPES = ["https://graph.microsoft.com/.default"]
except Exception as e:
    logger.critical(f"Змінні оточення {e} не отримано, перевірте файл .env")

