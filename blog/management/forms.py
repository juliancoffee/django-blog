from django import forms
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.validators import FileExtensionValidator


class ExportDataForm(forms.Form):
    download = forms.BooleanField(required=False)


def validate_size(file: File):
    # 5 megabytes
    MAX_SIZE = 5 * 1024 * 1024
    if file.size > MAX_SIZE:
        raise ValidationError(
            f"File size {file.size / (1024**2)}MB > {MAX_SIZE / (1024**2)}MB"
        )


class ImportDataForm(forms.Form):
    data_file = forms.FileField(
        validators=[
            FileExtensionValidator(allowed_extensions=["json"]),
            validate_size,
        ]
    )
