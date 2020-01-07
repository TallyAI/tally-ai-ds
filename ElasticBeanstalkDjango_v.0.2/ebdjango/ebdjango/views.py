from django.shortcuts import render
from yelp.models import business_id_test1, scraping_test1
from django.views.generic import TemplateView, ListView
from yelp.forms import ApprovalForm
from django.http import JsonResponse, HttpResponse
from yelp.py_scraper import yelpScraper
import requests
import json
import pandas as pd
import spacy
import scattertext as st
# from yelp.models import business_id_test1, scraping_test1

nlp = spacy.load("./down_sm/en_core_web_sm-2.1.0/en_core_web_sm/en_core_web_sm-2.1.0")




class APIView(TemplateView):
    template_name = "home.html"


class APIListView(ListView):
    model = business_id_test1


class HomeView(TemplateView):
    template_name = 'form/index.html'

    def get(self, request):
        form = ApprovalForm()
        url_submitted = business_id_test1.objects.all()

        args = {'form':form,'url_submitted':url_submitted}
        return render(request, self.template_name, args)

    def post(self, request):
        form = ApprovalForm(request.POST)#fill the form out with data received in request
        if form.is_valid():  # checks if there is some content in form
            form.save()
            to_predict = form.cleaned_data['url']  # Form.cleaned_data accesses the data after checking if is_valid is true, cleaning CharField to string
            text = yelpScraper(to_predict)
            text= JsonResponse(text, safe=False)
            form = ApprovalForm()
            return text
        args = {'form': form, 'text': text}
        return render(request, self.template_name, args)

def profile(request, business_id):
    # return HttpResponse('<h1> test {}.</h1>'.format(business_id))
    API_KEY = '-Io9W4bQSEfc3BxAwTvOV3B-aU9oS5j0F7LB7mWTXA79cRlMEmJzI7b_xIlqzSZd4b6IHiOlfp5APBsWNJt8cQRTV61u-r7DTKBCy1QTt91H9jjNjAEi0P6pjCTwXXYx'
    HEADERS = {'Authorization': f'Bearer {API_KEY}'}

    BUSINESS_ID = business_id
    URL = f'https://api.yelp.com/v3/businesses/{BUSINESS_ID}/reviews'
    req = requests.get(URL, headers=HEADERS)
    parsed = json.loads(req.text)
    reviews = parsed['reviews']
    reviews_json = []
    for review in reviews:
        output = {'id': review['id'], 'time': review['time_created'], 'text': review['text'], 'rating': review['rating']}
        reviews_json.append(output)

    # nlp_prediction = yelpScraper(BUSINESS_ID)
    df = yelpScraper(BUSINESS_ID)
    nlp.Defaults.stop_words |= {'will','because','not','friends','amazing','awesome','first','he','check-in','=','= =','male','u','want', 'u want', 'cuz','him',"i've", 'deaf','on', 'her','told','told him','ins', 'check-ins','check-in','check','I', 'i"m', 'i', ' ', 'it', "it's", 'it.','they','coffee','place','they', 'the', 'this','its', 'l','-','they','this','don"t','the ', ' the', 'it', 'i"ve', 'i"m', '!', '1','2','3','4', '5','6','7','8','9','0','/','.',','}

    corpus = st.CorpusFromPandas(df,
                             category_col=2,
                             text_col=1,
                             nlp=nlp).build()

    term_freq_df = corpus.get_term_freq_df()
    term_freq_df['highratingscore'] = corpus.get_scaled_f_scores('5.0 star rating')

    term_freq_df['poorratingscore'] = corpus.get_scaled_f_scores('1.0 star rating')
    dh = term_freq_df.sort_values(by= 'highratingscore', ascending = False)
    dh = dh[['highratingscore', 'poorratingscore']]
    dh = dh.reset_index(drop=False)
    dh = dh.rename(columns={'highratingscore': 'score'})
    dh = dh.drop(columns='poorratingscore')
    positive_df = dh.head(10)
    negative_df = dh.tail(10)
    results = {'positive': [{'term': pos_term, 'score': pos_score} for pos_term, pos_score in
                            zip(positive_df['term'], positive_df['score'])],
               'negative': [{'term': neg_term, 'score': neg_score} for neg_term, neg_score in
                            zip(negative_df['term'], negative_df['score'])]}

    result = json.dumps(results, indent=2)
    # for object in result:
    #     foo = MyScrapedThing.objects.create(name=object)
    #     # foo = MyScrapedThing(key=object.key, value=object.val)
    #     foo.save()
    # MyScrapedThing.objects.all()
    # biz_id.save()


    data = request.POST
    for i in df[1]:
        insert_reviews = scraping_test1.objects.create(business_id=BUSINESS_ID, text=df[1].astype(str))



    return HttpResponse(result)

