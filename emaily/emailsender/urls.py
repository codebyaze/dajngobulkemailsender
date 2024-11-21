from django.urls import path
from . import views

urlpatterns = [
    path('create-email-list/', views.create_email_list, name='create_email_list'),
    path('add-email-to-list/<int:list_id>/', views.add_email_to_list, name='add_email_to_list'),
    path('send-bulk-email/', views.send_bulk_email, name='send_bulk_email'),

]
