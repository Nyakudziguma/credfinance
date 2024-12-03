from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import json
from django.http import JsonResponse, HttpResponse
from .functions import WhatsappChatHandling
from django.contrib.auth.decorators import login_required
from .models import Pattern
from django.core.paginator import Paginator
from .messageFunctions import getMessageStatus
class WebhookView(APIView): 
    permission_classes = [AllowAny]
    def post(self, request):
        print(">>>>>>>>>>>>>>> Incoming data <<<<<<<<<<<<<<<<<<")
        data = json.loads(request.body)
        print(f"{data}")
        if 'object' in data and 'entry' in data:
            app_id = "443727948816080"
            if data['object'] == 'whatsapp_business_account':
                try:
                    for entry in data['entry']:
                        entry_id = entry.get('id')
                        if entry_id == app_id:
                            fromId = entry['changes'][0]['value']['messages'][0]['from']
                            phoneId = entry['changes'][0]['value']['metadata']['phone_number_id']
                            profileName = entry['changes'][0]['value']['contacts'][0]['profile']['name']
                            
                            messageID = entry['changes'][0]['value']['messages'][0]['id']
                            

                            if 'text' in entry['changes'][0]['value']['messages'][0]:
                                text = entry['changes'][0]['value']['messages'][0]['text']['body']
                            else:
                                text = None
                            if 'button' in entry['changes'][0]['value']['messages'][0]:
                                button = entry['changes'][0]['value']['messages'][0]['button']['payload']
                            else:
                                button = None
                            if 'image' in entry['changes'][0]['value']['messages'][0]:
                                image_id = entry['changes'][0]['value']['messages'][0]['image']['id']

                            else:
                                image_id = None
                            if 'document' in entry['changes'][0]['value']['messages'][0]:
                                document_id = entry['changes'][0]['value']['messages'][0]['document']['id']

                            else:
                                document_id = None

                            message = entry['changes'][0]['value']['messages'][0]
                            reply_data = None
                            selected_id = None
                            if 'interactive' in message:

                                if message['interactive']['type'] == 'button_reply':
                                    selected_id = message['interactive']['button_reply']['id']

                                
                                elif message['interactive']['type'] == 'list_reply':  
                                    selected_id = message['interactive']['list_reply']['id']
                                
                                elif message['interactive']['type'] == 'nfm_reply':
                                    interactive_data = message['interactive']
                                    reply_data = json.loads(interactive_data['nfm_reply']['response_json'])
                                    flow_token = reply_data.get('flow_token') 
                            else:
                                selected_id = None
                                reply_data = None

                                
                            image = f"https://graph.facebook.com/v20.0/{image_id}"
                            document = f"https://graph.facebook.com/v20.0/{document_id}"
                            
                            WhatsappChatHandling(fromId, message, profileName, phoneId, text, image, selected_id, data, document, button, reply_data)
                            status = getMessageStatus(messageID)
                            print(status)

                except Exception as e:
                   print(e)
        
        return HttpResponse('success', status=200)
    
    def get(self, request, *args, **kwargs):
        verify_token='badecb419530e1c3ee6f46bde4e66bb2e4867a4fa3ae1634bb14fee7269588a7a4bba9d358803356b89ae8f997e256100c2223d7598c74e91893d61a1a175dj6b'
        form_data = request.query_params
        mode = form_data.get('hub.mode')
        token = form_data.get('hub.verify_token')
        challenge = form_data.get('hub.challenge')
        print(f"{challenge}")
        return HttpResponse(challenge, status=200)


@login_required
def faqs(request):
    responses = Pattern.objects.prefetch_related('intent__responses').all()
    paginator = Paginator(responses, 100)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'apps/faqs.html', {'page_obj': page_obj})
