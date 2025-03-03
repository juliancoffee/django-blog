from django import forms


class SubscribeForm(forms.Form):
    to_new_posts = forms.BooleanField(
        label="Subscribe to new posts", required=False
    )
    to_engaged_posts = forms.BooleanField(
        label="Subscribe to updates on engaged posts",
        required=False,
    )
