import requests
import json

# URL-адрес, который вы получили в настройках Teams Webhook
webhook_url = 'https://tsumkyiv.webhook.office.com/webhookb2/471f3abf-db00-4433-afc2-2f36542785ac@dfebf89c-885d-4b59-97a4-0f78f27983a0/IncomingWebhook/92f2d4f1ab8e452cbb7bc084d52fb517/0ad795cc-ecf1-47c0-8e55-a0f8777ccc6a/V2rmg4dhEy2hYla6z3PHOrOmrYtGVcMRJJptOy1OuClKc1'

# Функция отправки простого текстового сообщения
def send_teams_message(message):
    headers = {'Content-Type': 'application/json'}
    payload = {'text': message}
    
    response = requests.post(
        webhook_url, 
        data=json.dumps(payload), 
        headers=headers
    )
    
    if response.status_code == 200:
        print("Сообщение успешно отправлено!")
    else:
        print(f"Ошибка при отправке. Код статуса: {response.status_code}")

# Пример использования
send_teams_message("Привет! Это автоматическое сообщение из Python.")

✅ В AD створено нового користувача

🗿🐣Ім'я: Петренко Петро | Petro Petrenko

🏢 Відділ: Управління інформаційних технологій

💼 Посада: test title | тестова посада

🔑 Пароль: 8x-Gw9vb