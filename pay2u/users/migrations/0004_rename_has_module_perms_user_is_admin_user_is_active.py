# Generated by Django 5.0.3 on 2024-03-14 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_has_module_perms'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='has_module_perms',
            new_name='is_admin',
        ),
        migrations.AddField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
