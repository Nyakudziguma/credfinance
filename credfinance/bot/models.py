from django.db import models

class Intent(models.Model):
    tag = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)  

    def __str__(self):
        return self.tag

class Pattern(models.Model):
    intent = models.ForeignKey(Intent, related_name="patterns", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.intent.tag} - {self.text}"

class Response(models.Model):
    intent = models.ForeignKey(Intent, related_name="responses", on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return f"{self.intent.tag} - {self.text}"
