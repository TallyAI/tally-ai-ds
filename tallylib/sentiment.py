# tallylib/sentiment.py
import json
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
# Local imports
from tallylib.sql import getLatestReviews


def tokenizer(doc):
    return [token for token in simple_preprocess(doc) 
            if token not in STOPWORDS]


def getRelationScores(business_id):
    # date, text, stars
    reviews = getLatestReviews(business_id=business_id)
    reviews = [r[1] for r in reviews]


######################################################  
# get Yelp review sentiment scores      
######################################################    
def yelpReviewSentiment(business_id):
    # API JSON format
    result = '''\
[
    {"subject":"Subject 1", "data1":45, "data2":70, "maxValue":150},
    {"subject":"Subject 2", "data1":75, "data2":95, "maxValue":150},
    {"subject":"Subject 3", "data1":20, "data2":50, "maxValue":150},
    {"subject":"Subject 4", "data1":65, "data2":85, "maxValue":150},
    {"subject":"Subject 5", "data1":35, "data2":45, "maxValue":150}
]
'''
    # reviews = getLatestReviews(business_id)
    
    return json.loads(result)




