import uuid

from django.db import models
from django.contrib.auth import get_user_model


# Get current auth user.
User = get_user_model()


class SubscriptionInfo(models.Model):
    browser = models.CharField(max_length=100)
    endpoint = models.URLField(max_length=500)
    auth = models.CharField(max_length=100)
    p256dh = models.CharField(max_length=100)


class PushInformation(models.Model):
    user = models.ForeignKey(
        User,
        related_name="webpush_info",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    subscription = models.ForeignKey(
        SubscriptionInfo, related_name="webpush_info", on_delete=models.CASCADE
    )
