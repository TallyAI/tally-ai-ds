# Generated by Django 3.0 on 2019-12-17 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='url',
            name='word_phrase',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]