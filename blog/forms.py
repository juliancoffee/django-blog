from django import forms


class CommentForm(forms.Form):
    # I wonder how max_length will interact with comment_text's length in db.
    # I wouldn't be surprised if these have different validation logic, at least
    # when it comes to browser behaviour.
    #
    # NOTE: unless you explicitly empty the label,
    # Django will generate it for you.
    comment = forms.CharField(max_length=200, label="")
