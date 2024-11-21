from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import ChatRoom

@receiver(post_save, sender=ChatRoom)
@receiver(post_delete, sender=ChatRoom)
def update_chatroom_count(sender, **kwargs):
    total_chatrooms = ChatRoom.objects.count()
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "dashboard_stats",
        {
            "type": "chatroom_count_update",
            "total_chatrooms": total_chatrooms,
        },
    )
