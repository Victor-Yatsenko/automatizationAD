import settings
import requests
import json
from create_user.info_for_create_user import PowerAutomateData


def send_message(data: PowerAutomateData, password):
    message = f"""
**✅ В AD створено нового користувача** \n
**🐣 Ім'я:** {data.full_name_ua} | {data.full_name_en} \n
**🏢 Відділ:** {data.department} \n
**💼 Посада:** {data.title_en} | {data.title_ua} \n
**🔑 Пароль:** {password}
"""

    headers = {'Content-Type': 'application/json'}
    payload = {'text': message}

    response = requests.post(settings.TEAMS_WEBHOOK_URL, data= json.dumps(payload), headers=headers)
    