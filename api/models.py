from django.db import models
from django.core.validators import int_list_validator

# Create your models here.
class url(models.Model):
    id = models.IntegerField(primary_key=True)
    url = models.CharField(max_length=5000)


    def __str__(self):
        return '{}'.format(self.url)

class WordListAPI(models.Model):
    id = models.IntegerField(primary_key=True)
    word_phrase = models.CharField(max_length=50)
    high_rating_score = models.DecimalField(max_digits=3, decimal_places=2)
    low_rating_score = models.DecimalField(max_digits=3, decimal_places=2)





















