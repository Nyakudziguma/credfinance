from django.conf import settings
import requests

def MainMenu(phoneNumber, message):
    headers = {"Authorization": settings.WHATSAPP_TOKEN}
    payload = {"messaging_product": "whatsapp",
               "recipient_type": "individual",
               "to": phoneNumber,
               "type": "interactive",
               "interactive": {
                    "type": "button",
                    "body": {
                    "text": message
                    },
                    "action": {
                    "buttons": [
                        {
                        "type": "reply",
                        "reply": {
                            "id": "faqs",
                            "title": "💬 Ask me Anything"
                        }
                        },
                        {
                        "type": "reply",
                        "reply": {
                            "id": "live_chat",
                            "title": "🗨️ Talk to Agent"
                        }
                        }
                    ]
                    }
                }
                }
                        
               
    response = requests.post(settings.WHATSAPP_URL, headers=headers, json=payload)
    ans = response.json()
    print(ans)