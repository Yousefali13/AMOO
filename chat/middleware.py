from django.utils import timezone
from datetime import timedelta
from AMOON_app.models import CustomUser

class UpdateLastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            # تحديث حقل last_seen مرة كل 5 دقائق لتجنب عملية حفظ مفرطة
            if (timezone.now() - request.user.last_seen) > timedelta(minutes=5):
                request.user.last_seen = timezone.now()
                request.user.save(update_fields=['last_seen'])
        return response
