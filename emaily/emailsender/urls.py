from django.urls import path
from . import views

urlpatterns = [
    path('', views.email_dashboard, name='email_dashboard'),
    path('create-email-list/', views.create_email_list, name='create_email_list'),
    path('add-email/<int:list_id>/', views.add_email_to_list, name='add_email_to_list'),
    path('send-email/', views.send_bulk_email, name='send_bulk_email'),  # No list_id here
]