from django.db import models
from django.conf import settings
from django.core.validators import int_list_validator
from django.contrib.auth.models import User

# Create your models here.
class url(models.Model):
    id = models.IntegerField(primary_key=True, )
    url = models.CharField(max_length=5000)
    date = models.DateTimeField(auto_now=True)#saved on first input into database
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)


    def __str__(self):
        return '{}'.format(self.url)

class WordListAPI(models.Model):
    id = models.IntegerField(primary_key=True)
    word_phrase = models.CharField(max_length=50)
    high_rating_score = models.DecimalField(max_digits=3, decimal_places=2)
    low_rating_score = models.DecimalField(max_digits=3, decimal_places=2)





















