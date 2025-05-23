
from django import template
from django.utils import timezone
import datetime

register = template.Library()

@register.filter
def last_seen_text(last_seen):
    """
    يعرض "متصل الآن" إذا كان المستخدم نشطًا خلال 5 دقائق، وإلا يعرض آخر ظهور.
    """
    if not last_seen:
        return "غير معروف"
    delta = timezone.now() - last_seen
    if delta < datetime.timedelta(minutes=5):
        return "متصل الآن"
    else:
        return "آخر ظهور: " + last_seen.strftime("%H:%M - %d/%m/%Y")
