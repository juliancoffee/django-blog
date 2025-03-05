from django import forms


class UpdateEmailForm(forms.Form):
    # NOTE:
    # Emails aren't unique in Django by default.
    #
    # To change this, we'd need to use custom User model, which we don't do
    # at the moment.
    #
    # If we would want to make them truly unique, we'd need to do that in a
    # model in the first place, because any validation here would be subject
    # to race conditions.
    email = forms.EmailField()
