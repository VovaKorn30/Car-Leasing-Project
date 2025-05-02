
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_index, name='chat_index'),
]
