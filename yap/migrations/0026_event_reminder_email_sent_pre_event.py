# Generated by Django 3.0.6 on 2020-06-03 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('yap', '0025_auto_20200602_1945'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='reminder_email_sent_pre_event',
            field=models.BooleanField(default=False),
        ),
    ]