from django import forms


class ImportDataForm(forms.Form):
    data_file = forms.FileField()
