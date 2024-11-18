import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
# Initialize Django before importing your WebSocket URLs
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credfinance.settings')
django.setup()

# Now import your WebSocket URLs after Django is set up
django_asgi_application = get_asgi_application()

from credfinance import routing

application = ProtocolTypeRouter({
    "http": django_asgi_application,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
        URLRouter(
            (routing.websocket_urlpatterns)
        ))
    ),
})