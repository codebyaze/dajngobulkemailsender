from django.conf import settings
from django.db import models

class EmailList(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use the user model from settings
        on_delete=models.CASCADE,
        related_name='email_lists',  # Reverse relation name
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Email(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Ensure consistency by using the user model from settings
        on_delete=models.CASCADE,
        related_name='emails',  # Reverse relation name, this avoids conflict with the built-in 'email' field
        default=1
    )
    email_address = models.EmailField()
    email_list = models.ForeignKey(
        EmailList,
        on_delete=models.CASCADE,
        related_name='emails' , # Related name for accessing emails in a list
    )
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email_address
