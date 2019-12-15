from django.shortcuts import render
from api.serializers import WordListSerializer
from api.models import url, WordListAPI
from django.views.generic import TemplateView, ListView
from rest_framework import serializers, viewsets
from rest_framework.decorators import api_view
from api.forms import ApprovalForm
from rest_framework.response import Response
from django.contrib import messages



import tarfile
import numpy as np
import pandas as pd
import spacy
import wget
from spacy.lang.en import English
import scattertext as st
from lxml import html
from requests import Session
from concurrent.futures import ThreadPoolExecutor as Executor
from itertools import count
import requests

def ValuePredictor(yelp_url, from_isbn=False):
    '''Takes a url, scrape site for reviews
    and calculates the term frequencies
    sorts and returns the top 10 as a json object
    containing term, highratingscore, poorratingscore.'''

    base_url = "https://www.yelp.com/biz/" # add business id
    api_url = "/review_feed?sort_by=date_desc&start="
    bid = yelp_url.replace('https://www.yelp.com/biz/','')
    if '?' in yelp_url:#deletes everything after "?" in url
        bid = yelp_url.split('?')[0]

    class Scraper():
        def __init__(self):
            self.data = pd.DataFrame()

        def get_data(self, n, bid=bid):
            with Session() as s:
                with s.get(base_url+bid+api_url+str(n*20)) as resp: #makes an http get request to given url and returns response as json
                    r = dict(resp.json()) #converts json response into a dictionary
                    _html = html.fromstring(r['review_list']) #loads from dictionary

                    dates = _html.xpath("//div[@class='review-content']/descendant::span[@class='rating-qualifier']/text()")
                    reviews = [el.text for el in _html.xpath("//div[@class='review-content']/p")]
                    ratings = _html.xpath("//div[@class='review-content']/descendant::div[@class='biz-rating__stars']/div/@title")

                    df = pd.DataFrame([dates, reviews, ratings]).T

                    self.data = pd.concat([self.data,df])

        def scrape(self): #makes it faster
            # multithreaded looping
            with Executor(max_workers=40) as e:
                list(e.map(self.get_data, range(10)))

    s = Scraper()
    s.scrape()
    df = s.data#converts scraped data into

    nlp.Defaults.stop_words |= {'will','because','not','friends','amazing','awesome','first','he','check-in','=','= =','male','u','want', 'u want', 'cuz','him',"i've", 'deaf','on', 'her','told','told him','ins', 'check-ins','check-in','check','I', 'i"m', 'i', ' ', 'it', "it's", 'it.','they','coffee','place','they', 'the', 'this','its', 'l','-','they','this','don"t','the ', ' the', 'it', 'i"ve', 'i"m', '!', '1','2','3','4', '5','6','7','8','9','0','/','.',','}

    corpus = st.CorpusFromPandas(df,
                             category_col=2,
                             text_col=1,
                             nlp=nlp).build()

    term_freq_df = corpus.get_term_freq_df()
    term_freq_df['highratingscore'] = corpus.get_scaled_f_scores('5.0 star rating')

    term_freq_df['poorratingscore'] = corpus.get_scaled_f_scores('1.0 star rating')
    dp = term_freq_df.sort_values(by= 'poorratingscore', ascending = False)
#     for i in dp.index:
#         if ' ' in i:
#             dp = dp.drop([i])
    df = term_freq_df.sort_values(by= 'highratingscore', ascending = False)
#     for i in df.index:
#         if ' ' in i:
#             df = df.drop([i])
    df = df[['highratingscore', 'poorratingscore']]

    df['highratingscore'] = round(df['highratingscore'], 2)
    df['poorratingscore'] = round(df['poorratingscore'], 2)
    df = df.reset_index(drop=False)
    df = df.head(20)

    dp = dp[['highratingscore', 'poorratingscore']]
    dp['highratingscore'] = round(dp['highratingscore'], 2)
    dp['poorratingscore'] = round(dp['poorratingscore'], 2)
    dp = dp.reset_index(drop=False)
    dp = dp.head(20)
    df = pd.concat([df,dp])
    return df.to_dict('records')



class APIView(TemplateView):
    template_name = "home.html"


class APIListView(ListView):
    model = url

class WordListViewSet(viewsets.ModelViewSet):
    queryset = WordListAPI.objects.all()
    serializer_class = WordListSerializer

@api_view(["POST"])#url gets posted in here
def feedInUrl(request):
    try:
        datafedin = request.data#data fed in will be in dictionary form
        url = datafedin.values()
        return JsonResponse('{}'.format(), safe=False)
    except ValueError as e:
        return Response(e.args[0], status.HTTP_400_BAD_REQUEST)

def cxcontact(request):
    if request.method=='POST':
        form=ApprovalForm(request.POST)
        if form.is_valid():
            url = form['url']
            messages.success(request, 'test')
    form = ApprovalForm()

# def cxcontact(request):
#     if request.method=='POST':
#         serializer = WordListSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             # return Response(serializer.data, status=status.HTTP_201_CREATED)

    return render(request, 'form/index.html',{'form':form})
