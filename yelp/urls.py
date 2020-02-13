# yelp/urls.py
from django.urls import path
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
# view functions
from .views import hello
from .views import home


urlpatterns = {
    path('', hello, name='hello'),
    path('<slug:business_id>', home, name='home'),
}

urlpatterns = format_suffix_patterns(urlpatterns)