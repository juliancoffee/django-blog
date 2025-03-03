from django import forms

from .models import Subscription


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ["to_new_posts", "to_engaged_posts"]
        labels = {
            "to_new_posts": "Subscribe to new posts",
            "to_engaged_posts": "Subscribe to updates on engaged posts",
        }
