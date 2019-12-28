from django.urls import path, include
from rest_framework import routers
# from yelp.views import HomeView
from django.conf.urls import url
from . import views

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()

app_name = "yelp"
urlpatterns = [
    #path('', include(router.urls)),#Whenever Django encounters include(), it chops off whatever part of the URL matched
    # up to that point and sends the remaining string to the included URLconf for further processing.
    path('<slug:business_id>', views.profile)#as_view returns a function instead of class, inherets from TemplateView
]
#more info: https://docs.djangoproject.com/en/3.0/topics/http/urls/#url-namespaces