import json
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

class CV(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=True)
    summary = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    linkedin_profile = models.URLField(blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    _skills = models.TextField(db_column='skills', blank=True)  # تخزين المهارات كـ JSON
    languages = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def skills(self):
        if not self._skills:
            return []
        try:
            return json.loads(self._skills)
        except json.JSONDecodeError:
            return []

    @skills.setter
    def skills(self, value):
        if isinstance(value, str):
            self._skills = value
        else:
            self._skills = json.dumps(value)

    def __str__(self):
        return f"{self.user.username}'s CV"

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def get_other_participant(self, user):
        return self.participants.exclude(id=user.id).first()

class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages'
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()

    @staticmethod
    def get_messages_between_users(user1, user2):
        conversation = Conversation.objects.filter(participants=user1).filter(participants=user2).first()
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(user1, user2)
        return conversation.messages.all().order_by('timestamp')

    @staticmethod
    def get_conversations_for_user(user):
        conversations = Conversation.objects.filter(participants=user).prefetch_related('messages', 'participants')
        
        conversation_data = []
        for conv in conversations:
            other_user = conv.get_other_participant(user)
            if not other_user:
                continue
                
            last_message = conv.messages.order_by('-timestamp').first()
            unread_count = conv.messages.filter(
                sender=other_user,
                receiver=user,
                is_read=False
            ).count()
            
            conversation_data.append({
                'user': other_user,
                'last_message': last_message.content if last_message else '',
                'last_message_time': last_message.timestamp if last_message else None,
                'unread_count': unread_count
            })
        
        conversation_data.sort(key=lambda x: x['last_message_time'] or timezone.now(), reverse=True)
        return conversation_data

class Notification(models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_notifications'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save()

    @staticmethod
    def create_notification(recipient, title, message, link=None):
        return Notification.objects.create(
            recipient=recipient,
            title=title,
            message=message,
            link=link
        ) 