from django.urls import path, include
from . import views
from rest_framework import routers
from api.views import APIListView, APIView, WordListViewSet, HomeView
from django.conf.urls import url

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'url_input', WordListViewSet)

app_name = "api"

urlpatterns = [
    path('', include(router.urls)),#Whenever Django encounters include(), it chops off whatever part of the URL matched
    # up to that point and sends the remaining string to the included URLconf for further processing.
    # path('form/', views.HomeView, name='index'),
    url('form/', HomeView.as_view(), name='index')#as_view returns a function instead of class, inherets from TemplateView
]
#more info: https://docs.djangoproject.com/en/3.0/topics/http/urls/#url-namespaces