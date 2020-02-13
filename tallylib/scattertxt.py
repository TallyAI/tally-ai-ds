import re
import sys
from datetime import datetime
import pandas as pd
import spacy
# import scattertext as st
import pytextrank
import numpy as np
# Local imports
# from tallylib.scraper import yelpScraper # Deleted on 2020-01-13
from tallylib.sql import getLatestReviews


# viztype0 (Top 10 Positive/Negative Phrases)
def getReviewPosNegPhrases(df_reviews, topk=10):

    if df_reviews.empty:
        return pd.DataFrame(), pd.DataFrame()

    df = df_reviews.copy() # columns=['date', 'text', 'stars']
    df_high = df[df['stars']==5]
    if len(df_high)==0:
        df_high = df[df['stars']==4]
    df_poor = df[df['stars']==1]
    if len(df_poor)==0:
        df_poor = df[df['stars']==3]
  
    nlp = spacy.load("en_core_web_sm")
    textrank = pytextrank.TextRank()
    nlp.add_pipe(textrank.PipelineComponent, name="textrank", last=True)

    columns = ['term', 'score']

    text = " ".join(df_high['text'])
    doc = nlp(text)
    phrases = []
    for i, p in enumerate(doc._.phrases):
        phrases.append([p.text, p.rank])
        if i >= topk: break
    df_high = pd.DataFrame(phrases, columns=columns)

    text = " ".join(df_poor['text'])
    doc = nlp(text)
    phrases = []
    for i, p in enumerate(doc._.phrases):
        phrases.append([p.text, p.rank])
        if i >= topk: break
    df_poor = pd.DataFrame(phrases, columns=columns)
 
    # positive dataframe, negative dataframe 
    return df_high, df_poor


# viztype3
def getYelpWordsReviewFreq(df_reviews):
  
    if df_reviews.empty:
        return pd.DataFrame()

    df = df_reviews.copy()
    df.columns = ['date', 'stars']

    # get 'weekly_avg_rating', 'cumulative_avg_rating'
    df['year'] = df['date'].dt.year
    df['week_number_of_year'] = df['date'].dt.week
    df = df.drop('date', axis=1)
    gb = df.groupby(['year', 'week_number_of_year'])
    df = gb.mean().reset_index().rename(columns={"stars":"weekly_avg_rating"})
    df['count'] = gb.count().values
    df = df.tail(8)
    df['cumulative_avg_rating'] = df['weekly_avg_rating'].cumsum()/df['count'].cumsum()

    # get the date of last day of the week
    lst = []
    for _, row in df.iterrows():
        text = str(row['year'].astype(int)) + '-W' + \
               str(row['week_number_of_year'].astype(int)) + '-6'
        date_of_week = datetime.strptime(text, "%Y-W%W-%w").strftime('%Y-%m-%d')
        lst.append(date_of_week)
    df['date_of_week'] = lst

    return df


# get viztype 0 and 3 for the endpoint ?viztype=0
def getDataViztype0(business_id):
    ''' Deleted on 2020-01-13
    # do web scraping 
    yelpScraperResult = yelpScraper(business_id)
    '''
    data = getLatestReviews(business_id, limit=200)
    if len(data)==0:
        return {}
    df_reviews = pd.DataFrame(data, columns=['date', 'text', 'stars'])
    del data
    df_reviews['date'] = pd.to_datetime(df_reviews['date'])

    # viztype0
    df_positive, df_negative = getReviewPosNegPhrases(df_reviews)
    positive, negative = [], []
    if not df_positive.empty:
        positive = [{'term': row[0], 'score': row[1]} 
            for row in df_positive[['term', 'score']].values]
    if not df_negative.empty:
        negative = [{'term': row[0], 'score': row[1]} 
            for row in df_negative[['term', 'score']].values]
    viztype0 = {
        'positive': positive, 
        'negative': negative
    }
    del [df_positive, df_negative]

    # viztype3
    df_bydate = getYelpWordsReviewFreq(df_reviews.drop('text', axis=1))
    viztype3 = {}
    if df_bydate is not None and not df_bydate.empty:
        viztype3 = {
            'star_data': [{'date': row[0], 
                           'cumulative_avg_rating': row[1], 
                           'weekly_avg_rating': row[2]}
            for row in df_bydate[['date_of_week', 'cumulative_avg_rating', 'weekly_avg_rating']].values]
        }
    del [df_bydate]

    # API data formatting
    results = {
        'viztype0': viztype0,
        'viztype3': viztype3
        }

    return results