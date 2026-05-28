import uvicorn
import settings
import json
from settings import logger
from fastapi import FastAPI, Header, HTTPException
import create_user.info_for_create_user as info_for_create_user
import create_user.send as send


app = FastAPI()


@app.post(f"{settings.CREATE_USER_URL}")
async def create_user_in_AD(
    data: info_for_create_user.PowerAutomateData,
    x_secret_token: str = Header(None)
):
    # Валідація токена
    if x_secret_token != settings.POWER_AUTOMATE_SECRET_TOKEN:
        logger.critical(f"Відмовлено: Невірний токен ({x_secret_token})")
        raise HTTPException(status_code=403, detail="Invalid token")

   
    ps_result = info_for_create_user.prepare_user_info(data)
    

    # Аналізуємо результат виконання PS скрипта та відправляємо лист керівнику
    if ps_result.returncode == 0:
        output_data = {}
        for line in ps_result.stdout.splitlines():
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                try:
                    output_data = json.loads(line)
                    break
                except json.JSONDecodeError:
                    continue
        

        user_password = output_data.get("UserPassword")
        manager_email = output_data.get("ManagerEmail")
        if user_password:
            logger.info("Відправка повідомлення в Тімс")
            send.send_message_to_teams(data, user_password)
            logger.info("Повідомлення успішно відправлено!")

            # Відправляємо листи (керівнику та копію)
            logger.info("Відправка листа")
            send.send_email(data, user_password, manager_email)
            logger.info("Лист успішно відправлено!")
        else:
            logger.warning("Пароль не знайдено в PowerShell виводі, лист та повідомлення не відправлено.")


        return { #повертаємо результат для Power Automate (щоб скрипт завершив роботу)
            "status": "Успіх",
            "user": data.full_name_en, 
            "message": "Користувач успішно створений в AD та лист відправлено керівнику.",
        }
    else:
        raise HTTPException(
            status_code=500,
            detail={"message": "PowerShell script failed", "error": ps_result.stderr}
        )



if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
