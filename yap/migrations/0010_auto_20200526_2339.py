# Generated by Django 3.0.6 on 2020-05-26 23:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yap', '0009_event_end_time'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='first_name',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='last_name',
        ),
    ]
