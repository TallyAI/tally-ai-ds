# tallylib/textrank.py
import pandas as pd
import spacy
import pytextrank
from datetime import datetime
from datetime import timedelta
from django.db import connection
# Local 
from tallylib.sql import getReviews
from tallylib.sql import getLatestReviewDate


# viztype1
def yelpTrendyPhrases(business_id, 
                      periods=12,
                      bagging_periods=3, 
                      days_per_period=30,
                      topk=10
                      ):  
    '''
    1. Get Yelp review texts
    2. Bag review texts within certain period, e.g. 6 peridos (180 days)
    3. Use Textrank to get scores
    4. Return JSON format for the frontend visualization
    '''
    ##################################
    # Get reivews from database
    ##################################
    # review data from database is already in datetime descending order.
    data = getLatestReviewDate(business_id) # [(datetime.datetime(2018, 10, 14, 0, 0),)]
    if len(data) == 0:
        return []
    else:
        current_date = data[0][0]
    past_date = current_date - timedelta(days=(days_per_period + bagging_periods) * periods - 1)
    reviews = getReviews(business_id, 
                         starting_date=past_date,
                         ending_date=current_date)
    if reviews == []:
        return []
    # Here using pandas dataframe is not a good practice.
    # However there is not enough time to change right now.
    df_reviews = pd.DataFrame(reviews, columns=['date', 'text'])
    reviews.clear(); del reviews
    df_reviews['date']= pd.to_datetime(df_reviews['date']) 

    ##################################
    # NLP processing
    ##################################
    '''
    1.
    In Google Colab, running 6 period bagging for some business would need:
    CPU times: user 24.5 s, sys: 520 ms, total: 25 s; Wall time: 25 s
    https://colab.research.google.com/drive/1r4uvFA6RNV35lO3JcYoO5Psz_EVhmNu0
    2.
    spacy.load() or en_core_web_sm.load() might cause the following error:
    'utf-8' codec can't decode byte 0xde in position 0: invalid continuation byte
    '''
    # load a spaCy model, depending on language, scale, etc.
    nlp = spacy.load("en_core_web_sm")
    # cutomize lemmatizer 
    # https://spacy.io/api/lemmatizer
    # ...
    textrank = pytextrank.TextRank()
    nlp.add_pipe(textrank.PipelineComponent, name="textrank", last=True)

    keywords = []
    for period in range(periods):
        # e.g. [starting_date, ending_date] = 180 days
        #      or ending_date - staring_date = 179 days
        ending_date = current_date - timedelta(days=days_per_period * period)
        starting_date = ending_date - timedelta(days=days_per_period * bagging_periods -1)
        
        condition = ((df_reviews['date']>=starting_date) &
                    (df_reviews['date']<=ending_date))
        df_texts = df_reviews[condition][['text', 'date']]
        text = " ".join(df_texts['text'].to_list())
        doc = nlp(text)
        for i,p in enumerate(doc._.phrases):
            keywords.append([ending_date, p.rank, p.text])
            if i >= topk * 1.5: 
                break  

    del [df_reviews]
    df_keywords = pd.DataFrame(keywords, 
                               columns=['date', 'rank', 'keywords'])
    keywords_topk = (df_keywords['keywords']
                        .value_counts()
                        .index[:topk]
                        .tolist())
    df_keywords = (df_keywords[df_keywords['keywords']
                        .isin(keywords_topk)])
 
    ##################################
    # Formatting for JSON output
    ##################################
    result, row = [], dict()
    date_last = ''
    for _, review in df_keywords.iterrows():
        if review['date'] != date_last:
            if row:
                result.append(row)
            date_last = review['date']
            row = dict()
            row['date'] = review['date'].strftime("%Y-%m-%d")
            row['data'] = []
        data = dict()
        data['phrase'] = review['keywords']
        data['rank'] = review['rank']
        row['data'].append(data)
    result.append(row)

    del [df_keywords]
    result = result[::-1]

    return result # return a list of dictionaries


    