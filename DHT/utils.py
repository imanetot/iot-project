from django.conf import settings
from twilio.rest import Client
import requests


def send_telegram(message):
    """
    Envoie un message via Telegram Bot

    Configuration requise dans settings.py:
    TELEGRAM_BOT_TOKEN = 'votre_bot_token'
    TELEGRAM_CHAT_ID = 'votre_chat_id'
    """
    try:
        bot_token = settings.TELEGRAM_BOT_TOKEN
        chat_id = settings.TELEGRAM_CHAT_ID

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"  # ou "Markdown" si vous préférez
        }

        response = requests.post(url, data=data)

        if response.status_code == 200:
            return True
        else:
            print(f"Erreur Telegram: {response.text}")
            return False

    except Exception as e:
        print(f"Erreur lors de l'envoi du message Telegram: {e}")
        return False


def send_whatsapp(message):
    """
    Envoie un message via WhatsApp (Twilio)

    Configuration requise dans settings.py:
    TWILIO_ACCOUNT_SID = 'votre_account_sid'
    TWILIO_AUTH_TOKEN = 'votre_auth_token'
    TWILIO_WHATSAPP_FROM = 'whatsapp:+14155238886'  # Numéro Twilio
    TWILIO_WHATSAPP_TO = 'whatsapp:+212XXXXXXXXX'   # Votre numéro
    """
    try:
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        whatsapp_from = settings.TWILIO_WHATSAPP_FROM
        whatsapp_to = settings.TWILIO_WHATSAPP_TO

        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_=whatsapp_from,
            body=message,
            to=whatsapp_to
        )

        print(f"WhatsApp message SID: {message.sid}")
        return True

    except Exception as e:
        print(f"Erreur lors de l'envoi du message WhatsApp: {e}")
        return False


def send_sms(message, phone_number=None):
    """
    Envoie un SMS via Twilio (optionnel)

    Configuration requise dans settings.py:
    TWILIO_ACCOUNT_SID = 'votre_account_sid'
    TWILIO_AUTH_TOKEN = 'votre_auth_token'
    TWILIO_PHONE_NUMBER = '+1234567890'  # Numéro Twilio
    TWILIO_SMS_TO = '+212XXXXXXXXX'      # Numéro destinataire
    """
    try:
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        from_number = settings.TWILIO_PHONE_NUMBER
        to_number = phone_number or settings.TWILIO_SMS_TO

        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_=from_number,
            body=message,
            to=to_number
        )

        print(f"SMS message SID: {message.sid}")
        return True

    except Exception as e:
        print(f"Erreur lors de l'envoi du SMS: {e}")
        return False