from django.conf import settings
import requests
from .models import *
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from .utils import *
from io import BytesIO
from django.core.files import File
from datetime import datetime, timedelta

headers = {
        'Authorization':  settings.WHATSAPP_TOKEN
    }

def sendWhatsAppMessage(phoneNumber,message, token, meta_url):
    headers = {"Authorization": token}
    payload = {"messaging_product": "whatsapp",
               "recipient_type": "individual",
               "to": phoneNumber,
               "type": "text",
               "text": {"body": message}
               }
    response = requests.post(meta_url, headers=headers, json=payload)
    ans = response.json()
    print("Response: ", ans)

def sendWhatsAppImages(fromId, tutorial_image, caption):
    headers = {"Authorization": settings.WHATSAPP_TOKEN}
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": fromId,
        "type": "image",
        "image": {
            "link": tutorial_image,
            "caption": caption
        }
    }

    response = requests.post(settings.WHATSAPP_URL, headers=headers, json=payload)
    ans = response.json

def sendWhatsAppDocument(fromId, document_file, caption):
    headers = {"Authorization": settings.WHATSAPP_TOKEN}
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": fromId,
        "type": "document",
        "document": {
            "link": f"",
            "filename": document_file,
            "caption":caption
        }
    }

    response = requests.post(settings.WHATSAPP_URL, headers=headers, json=payload)
    ans = response.json
    print("Response: ", ans)


def getMessageStatus(messageID):
    url = settings.WHATSAPP_URL
    headers = {
        "Authorization": settings.WHATSAPP_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": messageID
    }
    response = requests.post(url, headers=headers, json=payload)
    
    print("Response Status Code: ", response.status_code)
    print("Response JSON: ", response.json())
    return response.json()