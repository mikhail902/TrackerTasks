import requests
from django.conf import settings


def send_telegram_message(chat_id, text):
    """Отправка сообщения в Telegram"""
    token = settings.TELEGRAM_BOT_TOKEN
    if not token or not chat_id:
        return None

    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        return response.json()
    except requests.RequestException:
        return None