# tallylib/sql.py
# Local
from yelp.models import YelpReview
from yelp.models import YelpDsTrendyPhrase

def getYelpReviews(business_id, 
                   starting_date, 
                   ending_date):
    sql = f'''
    SELECT uuid, date, text FROM tallyds.review
    WHERE business_id = '{business_id}'
    AND datetime >= '{starting_date}'
    AND datetime <= '{ending_date}';
    '''
    return [[record.date, record.text] for record in YelpReview.objects.raw(sql)]

def getYelpReviewFrequency(business_id,
                   starting_date, 
                   ending_date):
    sql = f'''
    SELECT uuid, date, review_id, stars FROM tallyds.review
    WHERE business_id = '{business_id}'
    AND datetime >= '{starting_date}'
    AND datetime <= '{ending_date}';
    '''
    return [[record.date, record.text, record.stars] for record in YelpReview.objects.raw(sql)]


def getDsTrendyPhrases(business_id, period):
    pass 
    sql = f'''
    SELECT uuid, date, text FROM tallyds.review
    WHERE business_id = '{business_id}'
    LIMIT {period};
    '''
    return [[record.datetime, record.rank, record.keywords] 
        for record in YelpDSTrendyPhrase.objects.raw(sql)]