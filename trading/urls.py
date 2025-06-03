from django.urls import path
from .views import trigger_bot, bot_status

urlpatterns = [
    path('run/', trigger_bot, name='run_bot'),
    path('status/', bot_status, name='bot_status'),
]