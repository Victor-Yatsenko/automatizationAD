from create_user.info_for_create_user import PowerAutomateData
import requests
import json
import msal
import base64
import subprocess
import settings
from settings import logger
from docxtpl import DocxTemplate
from docx2pdf import convert
from pathlib import Path


def send_message_to_teams(data: PowerAutomateData, password):
    message = f"""
**✅ В AD створено нового користувача** \n
**🐣 Ім'я:** {data.full_name_ua} | {data.full_name_en} \n
**🏢 Відділ:** {data.department} \n
**💼 Посада:** {data.title_en} | {data.title_ua} \n
**🔑 Пароль:** {password}
"""

    headers = {'Content-Type': 'application/json'}
    # payload = {'text': message}
    payload = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "22C55E", # Зелений колір смужки збоку картки (можна змінити)
        "summary": "Створено нового користувача", # Обов'язкове поле для нових вебхуків
        "sections": [
            {
                "text": message
            }
        ]
    }

    response = requests.post(settings.TEAMS_WEBHOOK_URL, data=json.dumps(payload), headers=headers)

    # Додатковий блок для дебагу (щоб бачити, якщо щось піде не так)
    # if response.status_code not in (200, 202):
    #     logger.info(f"Помилка відправки в Teams. Статус: {response.status_code}, Відповідь: {response.text}")
    # else:
    #     logger.error("Повідомлення успішно відправлено!")



def get_base64_content(file_path):
    with open(file_path, "rb") as file:
        return base64.b64encode(file.read()).decode("utf-8")



def send_email(data: PowerAutomateData, user_password: str, manager_email: str):
    # Підготовка данних для листа
    full_name_ua_str = data.full_name_ua
    full_name_en_str = data.full_name_en
    front_or_back_office = data.front_or_back_office
    full_name_en = full_name_en_str.split()
    first_name_en = full_name_en[0] if len(full_name_en) > 1 else ""
    last_name_en  = full_name_en[1] if len(full_name_en) > 0 else ""

    # Формуємо docx документ
    if front_or_back_office == "Front office": PATCH_EASY_START_DOCX = settings.PATCH_EASY_START_FRONT_OFFICE_DOCX
    elif front_or_back_office == "Back office": PATCH_EASY_START_DOCX = settings.PATCH_EASY_START_BACK_OFFICE_DOCX

    context = {"name": f"{f"{first_name_en}.{last_name_en}"}", "password": user_password}
    base_easy_start_docx = DocxTemplate(PATCH_EASY_START_DOCX)
    base_easy_start_docx.render(context)
    base_easy_start_docx.save(f"create_user\\easy-start-docx\\easy-start-{full_name_ua_str}.docx")
    logger.info("Файл docx сформовано")
    

    # Конвертуємо документ в PDF а docx видаляємо
    libreoffice_path = r"C:\\Program Files\\LibreOffice\\program\\soffice.com"
    docx_file_path = Path(f"create_user\\easy-start-docx\\easy-start-{full_name_ua_str}.docx")
    output_dir = docx_file_path.parent
    command = [
        libreoffice_path,
        "--headless",
        "--convert-to", "pdf",
        str(docx_file_path),
        "--outdir", str(output_dir)
    ]
    # 3. Запускаємо процес конвертації
    try:
        # capture_output=True приховає зайвий вивід у консоль, 
        # check=True викине помилку, якщо щось піде не так
        subprocess.run(command, check=True, capture_output=True)
        print("PDF успішно згенеровано!")
        
        # 4. Видаляємо вихідний .docx файл, як у вас і було
        docx_file_path.unlink(missing_ok=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Помилка при конвертації LibreOffice: {e.stderr.decode(errors='ignore')}")
    except FileNotFoundError:
        print(f"Не знайдено LibreOffice за шляхом: {libreoffice_path}. Перевірте, чи він встановлений на віртуалці.")

    # convert(f"create_user\\easy-start-docx\\easy-start-{full_name_ua_str}.docx", f"create_user\\easy-start-docx\\easy-start-{full_name_ua_str}.pdf")
    # path_to_delete_file = Path(f"create_user\\easy-start-docx\\easy-start-{full_name_ua_str}.docx")
    # path_to_delete_file.unlink(missing_ok=True)


    # Шлях до файлу, який хочемо прикріпити
    file_to_attach = f"create_user\\easy-start-docx\\easy-start-{full_name_ua_str}.pdf"
    encoded_file = get_base64_content(file_to_attach)
    
    logger.success("PDF файл сформовано")


    html_content = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif;">
        <p>Вітаю!</p>
        <p>До команди приєдрунється новий співробітник.</p>
        <p>У вкладені стартова інструкція для {full_name_ua_str}.</p>
        <p>Гарного дня!</p>
    </div>
    """


    send = msal.ConfidentialClientApplication(
        settings.CLIENT_ID,
        authority=settings.AUTHORITY,
        client_credential=settings.CLIENT_SECRET,
    )

    result = send.acquire_token_silent(settings.SCOPES, account=None)
    if not result:
        result = send.acquire_token_for_client(scopes=settings.SCOPES)

    if "access_token" in result:
        access_token = result["access_token"]

    endpoint = f"https://graph.microsoft.com/v1.0/users/{settings.SENDER_EMAIL}/sendMail"

    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    email = {
        "message":{
            "subject": f"Вихід нового співробітника ({full_name_ua_str})",
            "body": {
                "contentType": "HTML",
                "content": html_content
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": manager_email
                    }
                }
            ],
            "ccRecipients": [ # відправка копії листа 
                {
                    "emailAddress": {
                        "address": settings.RECIPIENT_EMAIL
                    }
                }
            ],
            "attachments": [
                {
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": f"easy-start-{full_name_ua_str}.pdf",
                    # "contentType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  якщо всетаки буде docx
                    "contentType": "application/pdf",
                    "contentBytes": encoded_file
                }
            ]
        },
        "saveToSentItems": "true"
    }

    response = requests.post(endpoint, headers=headers, json=email)
    if response.status_code == 202:
        logger.success("Листи відправлено")
        # Видаляємо pdf файл після відправки
        path_to_delete_file = Path(file_to_attach)
        path_to_delete_file.unlink(missing_ok=True)

    else:
        logger.error(f"Помилка відправлення листа: {response.status_code} - {response.text}")
