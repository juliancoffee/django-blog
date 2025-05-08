from django import forms

from .utils import MAX_COMMENT_LENGTH, MAX_POST_LENGTH


class CommentForm(forms.Form):
    # I wonder how max_length will interact with comment_text's length in db.
    # I wouldn't be surprised if these have different validation logic, at least
    # when it comes to browser behaviour.
    #
    # NOTE: unless you explicitly empty the label,
    # Django will generate it for you.
    comment = forms.CharField(
        widget=forms.Textarea, max_length=MAX_COMMENT_LENGTH, label=""
    )


class PostForm(forms.Form):
    post = forms.CharField(
        widget=forms.Textarea, max_length=MAX_POST_LENGTH, label=""
    )
