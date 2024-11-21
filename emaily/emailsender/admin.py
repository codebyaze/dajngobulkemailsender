from django.contrib import admin
from .models import EmailList, Email

@admin.register(EmailList)
class EmailListAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')  # Display these fields in the admin panel
    search_fields = ('name',)  # Add a search bar for the 'name' field
    ordering = ('-created_at',)  # Order by creation date descending


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('email_address', 'email_list', 'added_at')  # Display these fields
    list_filter = ('email_list',)  # Filter by the associated email list
    search_fields = ('email_address', 'email_list__name')  # Search by email or list name
    ordering = ('-added_at',)  # Order by addition date descending
