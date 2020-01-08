from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from rest_framework import generics
from .serializers import YelpYelpScrapingSerializer
from .models import YelpYelpScraping
from tallylib.scattertext import getYelpWords, getYelpNouns
from tallylib.no_nlp_long_phrases import getYelpPhrases
from tallylib.scraper import yelpScraper

import requests
import json


def index(request):
    return HttpResponse("Hello, world. You're at the Yelp Scraping app index page.")

def getPosNegPhrases(request, business_id):
    yelpScraperResult = yelpScraper(business_id)
    # result = json.dumps(getYelpWords(yelpScraperResult))
    # result = json.dumps(getYelpPhrases(yelpScraperResult))
    result = json.dumps(getYelpNouns(yelpScraperResult))
    return HttpResponse(result)


class YelpYelpScrapingCreateView(generics.ListCreateAPIView):
    """This class defines the create behavior of our rest api."""
    queryset = YelpYelpScraping.objects.all()
    serializer_class = YelpYelpScrapingSerializer

    def perform_create(self, serializer):
        """Save the post data when creating a new bucketlist."""
        serializer.save()


class YelpYelpScrapingDetailsView(generics.RetrieveUpdateDestroyAPIView):
    """This class handles the http GET, PUT and DELETE requests."""

    queryset = YelpYelpScraping.objects.all()
    serializer_class = YelpYelpScrapingSerializer
