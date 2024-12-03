# tasks.py
from celery import Celery, shared_task
import csv
import os
import requests
from .models import *
import logging
logger = logging.getLogger(__name__)
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from  balances.models import CompanyBalance, Prices, Transaction
from django.db import transaction


@shared_task
def process_csv_file(bulk_message_id):
    channel_layer = get_channel_layer()

    def send_updated_stats():
        total_messages = MessageResponse.objects.count()
        failed_messages = MessageResponse.objects.filter(status='Failed').count() 
        successful_messages = MessageResponse.objects.filter(status='Successful').count()

        async_to_sync(channel_layer.group_send)(
            "bulk_messaging_stats",
            {
                "type": "chatroom_count_update",
                "total_messages": total_messages,
                "failed_messages": failed_messages,
                "successful_messages": successful_messages,
            }
        )

    try:
        bulk_message = BulkMessages.objects.get(pk=bulk_message_id)
        file_path = f"https://finance.credspace.co.zw/media/{bulk_message.csv}"
        image_path = f"https://finance.credspace.co.zw/media/{bulk_message.file}" if bulk_message.file else None
        template_name = bulk_message.template.value
        message = bulk_message.message
        status = "Successful"

        company_balance = CompanyBalance.objects.get(company=bulk_message.user.company)
        try:
            price = Prices.objects.get(code='BWM01')
            cost_per_message = price.price
        except Prices.DoesNotExist:
            logger.error("Price not found for code BWM01")
            return

        successful_count = 0

        def send_whatsapp_message(phone_number, payload):
            headers = {"Authorization": settings.WHATSAPP_TOKEN}
            response = requests.post(settings.WHATSAPP_URL, headers=headers, json=payload)
            return response.json()

        def create_media_payload(phone_number, template_name, message, image_path):
            return {
                "messaging_product": "whatsapp",
                "recipient_type": "individual", 
                "to": phone_number,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": "en"},
                    "components": [
                        {
                            "type": "header",
                            "parameters": [
                                {
                                    "type": "image",
                                    "image": {"link": image_path}
                                }
                            ]
                        },
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": message
                                }
                            ]
                        },
                        {
                            "type": "button",
                            "sub_type": "quick_reply",
                            "index": "0",
                            "parameters": [
                                {
                                    "type": "payload",
                                    "payload": "PAYLOAD"
                                }
                            ]
                        }
                    ]
                }
            }

        def create_text_payload(phone_number, template_name, message):
            return {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": phone_number,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": "en"},
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": message
                                }
                            ]
                        }
                    ]
                }
            }

        with requests.get(file_path, stream=True) as response:
            response.raise_for_status()
            
            with open('temp_file.csv', 'wb') as temp_file:
                for chunk in response.iter_content(chunk_size=1024):
                    temp_file.write(chunk)

            with open('temp_file.csv', 'r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    phone_number = row['phoneNumber']
                    
                    if template_name in ['image_message', 'document_message', 'video_message']:
                        payload = create_media_payload(phone_number, template_name, message, image_path)
                    else:
                        payload = create_text_payload(phone_number, template_name, message)

                    ans = send_whatsapp_message(phone_number, payload)
                    
                    # Process response
                    if isinstance(ans, dict):
                        status = 'Successful' if list(ans.keys())[0] != 'error' else 'Failed'
                        if status == 'Successful':
                            successful_count += 1

                    try:
                        MessageResponse.objects.create(
                            batch=bulk_message,
                            phone_number=phone_number,
                            response=ans,
                            status=status
                        )
                    except Exception as e:
                        logger.error(f'Message Response Error: {e}')

                    send_updated_stats()

        os.remove('temp_file.csv')

        # Process billing
        total_cost = successful_count * cost_per_message
        with transaction.atomic():
            company_balance.balance -= total_cost
            company_balance.save()

            Transaction.objects.create(
                user=bulk_message.user,
                transaction_type='deduction', 
                amount=total_cost,
                description=f"Deduction for sending {successful_count} messages."
            )

        logger.info(f"Successfully sent {successful_count} messages")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")