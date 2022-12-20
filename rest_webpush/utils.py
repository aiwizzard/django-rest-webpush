import json
import time

from django.conf import settings
from django.forms.models import model_to_dict
from pywebpush import WebPushException, webpush


def process_subscription_data(post_data):
    """Process the subscription data according to out model"""
    subscription_data = post_data.pop("subscription", {})
    # As our dataset saves the auth and p256dh keys in seperate field,
    # we need to refactor it and insert the auth and p256dh keys in the same dictionary.
    keys = subscription_data.pop("keys", {})
    subscription_data.update(keys)
    # Insert the browser name
    subscription_data["browser"] = post_data.pop("browser")
    return subscription_data


def send_notification_to_user(user, payload, ttl=0):
    # Get all the push_info of the user.
    payload = json.dumps(payload)
    push_infos = user.webpush_info.select_related("subscription")
    for push_info in push_infos:
        _send_notification(push_info.subscription, payload, ttl)


def _send_notification(subscription, payload, ttl=0):
    subscription_data = _process_subscription_info(subscription)

    vapid_data = {}

    webpush_settings = getattr(settings, "WEB_PUSH_SETTINGS")
    vapid_private_key = webpush_settings.get("VAPID_PRIVATE_KEY")
    vapid_admin_email = webpush_settings.get("VAPID_ADMIN_EMAIL")

    # Vapid keys are optional, and mandatory only for chrome
    # If Vapid key is provided, include vapid key and claims
    if vapid_private_key:
        vapid_data = {
            "vapid_private_key": vapid_private_key,
            "vapid_claims": {
                "sub": f"mailto:{vapid_admin_email}",
                "exp": int(time.time()) + 24 * 60 * 60,
            },
        }
    try:
        req = webpush(
            subscription_info=subscription_data, data=payload, ttl=ttl, **vapid_data
        )
        return req
    except WebPushException as e:
        # If the subscription is expired, delete it.
        if e.response.status_code == 410:
            subscription.delete()
        if e.response and e.response.json():
            extra = e.response.json()
            print(
                f"Remote service replied with a {extra.code}:{extra.errno}, {extra.message}"
            )
        else:
            # Its other type of exception!
            raise e


def _process_subscription_info(subscription):
    subscription_data = model_to_dict(subscription, exclude=["browser", "id"])
    endpoint = subscription_data.pop("endpoint")
    p256dh = subscription_data.pop("p256dh")
    auth = subscription_data.pop("auth")

    return {"endpoint": endpoint, "keys": {"p256dh": p256dh, "auth": auth}}
