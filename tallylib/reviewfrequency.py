import pandas as pd
from datetime import datetime
from datetime import timedelta
from django.db import connection
from tallylib.sql import getYelpReviewFrequency


def getReviewFrequencyResults(business_id):
    current_date = datetime.strptime('2018-11-30', '%Y-%m-%d')
    past_date = datetime.strptime('2000-11-30', '%Y-%m-%d')
    reviews = getYelpReviewFrequency(business_id,
                             starting_date=past_date,
                             ending_date=current_date)
    # if reviews == []:
        
    df = pd.DataFrame(reviews, columns=['date', 'text','stars'])
    df['date']= pd.to_datetime(df['date']) 
    # df['date'] = df['date'].str.replace('\n','')
    # df['date'] = df['date'].str.replace(' ','')
    df['date'] = df['date'].astype('datetime64[ns]')
    # ratingDict = {'5.0 star rating':5,'4.0 star rating':4, '3.0 star rating':3, '2.0 star rating':2, '1.0 star rating':1}
    # df['stars'] = df['stars'].map(ratingDict) 
    df['current_rating'] = df['stars'].mean()
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['week_number_of_year'] = df['date'].dt.week
    bydate = df.groupby(['year', 'month','week_number_of_year']).mean()
    bydate = pd.DataFrame(bydate.to_records())#flatten groupby column
    bydate = bydate.iloc[::-1]
    results = {'const star_data': [{'name': term, 'current_rating': current_rating, 'week_rating': week_rating}
                            for term, current_rating, week_rating in zip(bydate['week_number_of_year'], bydate['current_rating'], bydate['stars'])]}
    return results