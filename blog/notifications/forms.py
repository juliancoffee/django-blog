from django import forms


# TODO: look into ModelForm?
#
# This would allow us using "instance"
#
# And ideally typed using django-stubs
class SubscribeForm(forms.Form):
    to_new_posts = forms.BooleanField(
        label="Subscribe to new posts", required=False
    )
    to_engaged_posts = forms.BooleanField(
        label="Subscribe to updates on engaged posts",
        required=False,
    )
