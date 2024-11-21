from django.db import models

class EmailList(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="List Name")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Email(models.Model):
    email_list = models.ForeignKey(EmailList, on_delete=models.CASCADE, related_name='emails')
    email_address = models.EmailField(unique=True, verbose_name="Email Address")
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email_address
