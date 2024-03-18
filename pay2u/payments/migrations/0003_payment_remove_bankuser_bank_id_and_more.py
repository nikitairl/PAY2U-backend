# Generated by Django 5.0.3 on 2024-03-18 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_alter_bank_inn'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('amount', models.IntegerField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('receipt', models.CharField(max_length=32)),
                ('document', models.FileField(upload_to='documents')),
            ],
        ),
        migrations.RemoveField(
            model_name='bankuser',
            name='bank_id',
        ),
        migrations.RemoveField(
            model_name='bankuser',
            name='user_id',
        ),
        migrations.DeleteModel(
            name='Bank',
        ),
        migrations.DeleteModel(
            name='BankUser',
        ),
    ]