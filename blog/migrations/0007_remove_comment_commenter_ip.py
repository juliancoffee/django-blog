# Generated by Django 5.1.3 on 2025-01-30 21:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_comment_proper_ip'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='commenter_ip',
        ),
    ]
