"""
Most of the code in this module is adapted from https://github.com/safwanrahman/django-webpush.git
"""


import json

from  rest_framework import decorators, response, status
from rest_webpush import utils, forms

@decorators.api_view(http_method_name=["POST"])
def save_info(request):
    # Parse the  json object from post data. return 400 if the json encoding is wrong
    try:
        post_data = json.loads(request.body.decode("utf-8"))
    except ValueError:
        return response.Response(status=status.HTTP_400_BAD_REQUEST)

    # Process the subscription data to match with the model
    subscription_data = utils.process_subscription_data(post_data)
    subscription_form = forms.SubscriptionForm(subscription_data)

    # pass the data through WebpushForm for validation purpose
    web_push_form = forms.WebPushForm(post_data)

    # Check if subscription info and the webpush info both are valid
    if subscription_form.is_valid() and web_push_form.is_valid():
        # Get the cleaned data in order to get status_type and group_name
        web_push_data = web_push_form.cleaned_data
        status_type = web_push_data.pop("status_type")

        # We need the user to subscribe for a notification
        if request.user.is_authenticated:
            # Save the subscription info with subscription data
            # as the subscription data is a dictionary and its valid
            subscription = subscription_form.get_or_save()
            web_push_form