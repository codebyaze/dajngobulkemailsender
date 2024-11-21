
from django.contrib import admin
from django.urls import path, include
import emailsender.views as views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name='homepage'), 
    path('email/', include('emailsender.urls')), 
    path('users/', include('users.urls')),
]
