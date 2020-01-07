from django.db import models
from django.contrib.auth.models import User
import uuid
import pytz
from django.db import models
from timezone_field import TimeZoneField
import datetime
from django.utils.timezone import now
date = datetime.date.today()


class business_id_test1(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    biz_id = models.CharField(max_length=5000)

    def __str__(self):
        return '{}'.format(self.biz_id)

class TimeFieldWithoutTimezone(models.Field):
    def db_type(self, connection):
        return 'timestamp'

class scraping_test1(models.Model):
    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    
    uuid = models.UUIDField( 
         primary_key = True, 
         default = uuid.uuid4, 
         editable = False, unique=True)
    review_id = models.CharField(max_length=5000, blank=True)
    business_id = models.CharField(max_length=30, blank=True)
    id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    stars = models.FloatField(max_length=10, null=True, blank=True)
    # datetime = TimeFieldWithoutTimezone()
    datetime = models.DateTimeField(default=datetime.datetime.now())
    date = models.DateField(default=date.today)
    time = models.TimeField(auto_now_add=True, blank=True)
    text = models.CharField(max_length=100000, blank=True)
#     timestamp = TimeZoneField()
# my_inst = scraping_test1(
#     timestamp = pytz.UTC,
#     )

# my_inst.full_clean()  # validates against pytz.common_timezones
# my_inst.save()        # values stored in DB as strings

# tz = my_inst.timestamp  # values retrieved as pytz objects
# repr(tz) 




















