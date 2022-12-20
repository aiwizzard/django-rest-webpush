from socket import fromshare
from django import forms

from rest_webpush import models


class WebPushForm(forms.Form):
    status_type = forms.ChoiceField(
        choices=[("subscribe", "subscribe"), ("unsubscribe", "unsubscribe")]
    )

    def save_or_delete(self, subscription, user, status_type):
        # Ensure get_or_create matches exactly
        data = {"user": user}

        data["subscription"] = subscription

        (
            push_info,
            _,
        ) = models.PushInformation.objects.get_or_create(**data)

        # If unsubscribe is called, that means need to delete the browser
        # and notification info from the server
        if status_type == "unsubscribe":
            push_info.delete()
            subscription.delete()


class SubscriptionForm(forms.Form):
    class Meta:
        model = models.SubscriptionInfo
        fields = ("endpoint", "auth", "p256dh", "browser")

    def get_or_save(self):
        subscription, _ = models.SubscriptionInfo.get_or_create(**self.cleaned_data)
        return subscription
