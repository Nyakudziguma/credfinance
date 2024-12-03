from django import forms
from .models import BulkMessages

class BulkMessageForm(forms.ModelForm):
    class Meta:
        model = BulkMessages
        fields = ['template', 'message', 'csv', 'file']
