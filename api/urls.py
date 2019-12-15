from django.urls import path, include
from . import views
from rest_framework import routers
from api.views import APIListView, APIView, WordListViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'url_input', WordListViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('form/', views.cxcontact, name='index'),
]
