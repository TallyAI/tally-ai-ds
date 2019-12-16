from django.shortcuts import render, redirect
from api.serializers import WordListSerializer
from api.models import Url, WordListAPI
from django.views.generic import TemplateView, ListView
from rest_framework import serializers, viewsets
from rest_framework.decorators import api_view
from api.forms import ApprovalForm
from rest_framework.response import Response
from django.contrib import messages
from django.http import JsonResponse


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


nlp = spacy.load("./down_sm/en_core_web_sm-2.1.0/en_core_web_sm/en_core_web_sm-2.1.0")

def ValuePredictor(yelp_url, from_isbn=False):
    '''Takes a url, scrape site for reviews
    and calculates the term frequencies
    sorts and returns the top 10 as a json object
    containing term, highratingscore, poorratingscore.'''

    base_url = "https://www.yelp.com/biz/"  # add business id
    api_url = "/review_feed?sort_by=date_desc&start="
    bid = yelp_url.replace('https://www.yelp.com/biz/', '')
    if '?' in yelp_url:  # deletes everything after "?" in url
        bid = yelp_url.split('?')[0]

    class Scraper():
        def __init__(self):
            self.data = pd.DataFrame()

        def get_data(self, n, bid=bid):
            with Session() as s:
                with s.get(base_url + bid + api_url + str(
                        n * 20)) as resp:  # makes an http get request to given url and returns response as json
                    r = dict(resp.json())  # converts json response into a dictionary
                    _html = html.fromstring(r['review_list'])  # loads from dictionary

                    dates = _html.xpath(
                        "//div[@class='review-content']/descendant::span[@class='rating-qualifier']/text()")
                    reviews = [el.text for el in _html.xpath("//div[@class='review-content']/p")]
                    ratings = _html.xpath(
                        "//div[@class='review-content']/descendant::div[@class='biz-rating__stars']/div/@title")

                    df = pd.DataFrame([dates, reviews, ratings]).T

                    self.data = pd.concat([self.data, df])

        def scrape(self):  # makes it faster
            # multithreaded looping
            with Executor(max_workers=40) as e:
                list(e.map(self.get_data, range(10)))

    s = Scraper()
    s.scrape()
    df = s.data  # converts scraped data into

    nlp.Defaults.stop_words |= {'will', 'because', 'not', 'friends', 'amazing', 'awesome', 'first', 'he', 'check-in',
                                '=', '= =', 'male', 'u', 'want', 'u want', 'cuz', 'him', "i've", 'deaf', 'on', 'her',
                                'told', 'told him', 'ins', 'check-ins', 'check-in', 'check', 'I', 'i"m', 'i', ' ', 'it',
                                "it's", 'it.', 'they', 'coffee', 'place', 'they', 'the', 'this', 'its', 'l', '-',
                                'they', 'this', 'don"t', 'the ', ' the', 'it', 'i"ve', 'i"m', '!', '1', '2', '3', '4',
                                '5', '6', '7', '8', '9', '0', '/', '.', ','}

    corpus = st.CorpusFromPandas(df,
                                 category_col=2,
                                 text_col=1,
                                 nlp=nlp).build()

    term_freq_df = corpus.get_term_freq_df()
    term_freq_df['highratingscore'] = corpus.get_scaled_f_scores('5.0 star rating')

    term_freq_df['poorratingscore'] = corpus.get_scaled_f_scores('1.0 star rating')
    dp = term_freq_df.sort_values(by='poorratingscore', ascending=False)
    #     for i in dp.index:
    #         if ' ' in i:
    #             dp = dp.drop([i])
    df = term_freq_df.sort_values(by='highratingscore', ascending=False)
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
    df = pd.concat([df, dp])
    return df.to_dict('records')


class APIView(TemplateView):
    template_name = "home.html"


class APIListView(ListView):
    model = Url


class WordListViewSet(viewsets.ModelViewSet):
    queryset = WordListAPI.objects.all()
    serializer_class = WordListSerializer


class HomeView(TemplateView):
    template_name = 'form/index.html'

    def get(self, request):
        form = ApprovalForm()
        url_submitted = Url.objects.all().order_by('-date')

        args = {'form':form,'url_submitted':url_submitted}
        return render(request, self.template_name, args)

    def post(self, request):
        form = ApprovalForm(request.POST)#fill the form out with data received in request
        # if request.method=='POST': #pass my post information in
        #     form=ApprovalForm(request.POST)
        if form.is_valid():  # checks if there is some content in form
            url = form.save(commit=False)#I want to do something first before saving for good
            url.user = request.user
            url.save()

            to_predict = form.cleaned_data['url']  # Form.cleaned_data accesses the data after checking if is_valid is true, cleaning CharField to string
            text = ValuePredictor(to_predict)
            results = JsonResponse(text, safe=False)
            form = ApprovalForm()
            return redirect('api/form:index')#redirects to homepage, this also worked api/form:index

        args = {'form': form, 'text': text}
        return render(request, self.template_name, args)

# def cxcontact(request):
#     if request.method=='POST':
#         serializer = WordListSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             # return Response(serializer.data, status=status.HTTP_201_CREATED)

# return render(request, 'form/index.html',{'form':form})
