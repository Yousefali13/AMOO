from django.urls import path
from . import views

urlpatterns = [
    # ... existing urls ...
    path('messages/', views.messages_list, name='messages_list'),
    path('messages/get-company-users/', views.get_company_users, name='get_company_users'),
    path('messages/chat/<int:user_id>/', views.chat_view, name='chat_view'),
    path('messages/send/<int:user_id>/', views.send_message, name='send_message'),
    path('messages/get/<int:user_id>/', views.get_messages, name='get_messages'),
] 