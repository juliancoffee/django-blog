from django import forms


class ExportDataForm(forms.Form):
    download = forms.BooleanField(required=False)


class ImportDataForm(forms.Form):
    data_file = forms.FileField()
