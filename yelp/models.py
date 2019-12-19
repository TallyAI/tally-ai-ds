from django.db import models


class Url(models.Model):

    url = models.CharField(max_length=5000)

    def __str__(self):
        return '{}'.format(self.url)























