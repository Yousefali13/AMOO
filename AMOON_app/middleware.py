from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

class UpdateLastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated:
            now = timezone.now()
            last_seen = request.user.last_seen
            
            if (now - last_seen) > timedelta(minutes=5):
                User.objects.filter(pk=request.user.pk).update(last_seen=now)
        
        return response