# Generated by Django 5.0.3 on 2024-03-19 11:18

import django.db.models.deletion
import users.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_alter_account_account_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='account_number',
            field=models.CharField(default=users.models.increment_account_number, max_length=20, unique=True, verbose_name='Номер счёта'),
        ),
        migrations.AlterField(
            model_name='account',
            name='balance',
            field=models.IntegerField(default=0, verbose_name='Баланс'),
        ),
        migrations.AlterField(
            model_name='account',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]