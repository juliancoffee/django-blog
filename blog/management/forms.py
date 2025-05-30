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
        size_in_mb = file.size / (1024**2)
        max_size_in_mb = MAX_SIZE / (1024**2)
        raise ValidationError(
            f"File size {size_in_mb:.1f}MB > {max_size_in_mb:.1f}MB",
            code="file_size_exceeded",
        )


class ImportDataForm(forms.Form):
    # NOTE: files don't go to cleaned data, so you can't really run form
    # validation in this case.
    # You can do field validation, thankfully.
    data_file = forms.FileField(
        validators=[
            FileExtensionValidator(allowed_extensions=["json"]),
            validate_size,
        ]
    )
