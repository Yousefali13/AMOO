from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Message
from django.contrib.auth.models import User

@login_required
def messages_list(request):
    conversations = Message.get_conversations_for_user(request.user)
    return render(request, 'messages_list.html', {
        'conversations': conversations
    })

@login_required
def get_company_users(request):
    # الحصول على مستخدمي نفس الشركة باستثناء المستخدم الحالي
    users = User.objects.filter(
        company=request.user.company
    ).exclude(
        id=request.user.id
    ).select_related('profile')

    users_data = [{
        'id': user.id,
        'full_name': user.get_full_name(),
        'profile_image': user.profile.image.url if hasattr(user, 'profile') and user.profile.image else None,
        'department': user.profile.department if hasattr(user, 'profile') else ''
    } for user in users]

    return JsonResponse({'users': users_data})

@login_required
def chat_view(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    messages = Message.get_messages_between_users(request.user, other_user)
    
    # تحديث حالة القراءة للرسائل
    Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)

    return render(request, 'chat.html', {
        'messages': messages,
        'other_user': other_user
    })

@login_required
def send_message(request, user_id):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        receiver = get_object_or_404(User, id=user_id)
        content = request.POST.get('content')

        if content:
            message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content
            )

            return JsonResponse({
                'status': 'success',
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'timestamp': message.timestamp.strftime('%H:%M'),
                    'is_sender': True
                }
            })

    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_messages(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    last_message_id = request.GET.get('last_id')
    
    messages_query = Message.get_messages_between_users(request.user, other_user)
    if last_message_id:
        messages_query = messages_query.filter(id__gt=last_message_id)

    messages_data = [{
        'id': msg.id,
        'content': msg.content,
        'timestamp': msg.timestamp.strftime('%H:%M'),
        'is_sender': msg.sender == request.user
    } for msg in messages_query]

    return JsonResponse({'messages': messages_data}) 