# Generated by Django 3.0 on 2019-12-17 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20191217_1348'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='url',
            name='date',
        ),
        migrations.RemoveField(
            model_name='url',
            name='user',
        ),
        migrations.AlterField(
            model_name='url',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]