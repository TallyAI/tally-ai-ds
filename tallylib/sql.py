# tallylib/sql.py
import time
from datetime import datetime
from datetime import timedelta
from django.db import connection
# Local
# from yelp.models import AllReview # Django data model
'''
2020-01-10 Pay attention to the indexes created on the tables.
'''


###############################################################
# tallyds.yelp_review
###############################################################
# Query with Django data models
def getReviews(business_id, 
               starting_date, 
               ending_date):
    sql = f'''
    SELECT date, 
           text 
    FROM tallyds.yelp_review
    WHERE business_id = '{business_id}'
    AND datetime >= '{starting_date}'
    AND datetime <= '{ending_date}'
    ORDER BY datetime DESC;
    '''
    # return [[record.date, record.text] 
    #     for record in AllReview.objects.raw(sql)] # query by Django data model
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()
    except Exception as e:
        print(e)


# Query without Django data models
def getReviewCountMonthly(business_id,
                          number_of_months=12):
    sql = f'''
    SELECT extract(year from date)::INTEGER AS year,
           extract(month from date)::INTEGER AS month,
           count(*) AS count
    FROM tallyds.yelp_review AS r
    WHERE business_id = '{business_id}'
    GROUP BY 1, 2
    ORDER BY 1 DESC, 2 DESC
    LIMIT {number_of_months};
    '''
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            # return a tuple
            return cursor.fetchall()
    except Exception as e:
        print(e)

    
def getLatestReviewDate(business_id):
    sql = f'''
    SELECT datetime
    FROM tallyds.yelp_review
    WHERE business_id = '{business_id}'
    ORDER BY datetime DESC
    LIMIT 1;
    '''
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            # return [(datetime.datetime(2018, 10, 14, 0, 0),)]
            return cursor.fetchall()
    except Exception as e:
        print(e)
        return []


def getLatestReviews(business_id, 
                     limit=200):
    sql = f'''
    SELECT date, 
           text,
           stars::INTEGER
    FROM tallyds.yelp_review
    WHERE business_id = '{business_id}'
    ORDER BY datetime DESC
    LIMIT {limit};
    '''
    with connection.cursor() as cursor:
        cursor.execute(sql)
        # return a list of tuples
        return cursor.fetchall()


def updateYelpReviews(business_id, data):
    # data columns: datetime, star, text, review_id, user_id
    if data is None or len(data)==0:
        return 0 # returncode success

    s0 = "INSERT INTO tallyds.yelp_review VALUES "
    s1 = ""
    for d in data:
        d_datetime, d_date, d_time, d_now, d_text = "", "", "", "", ""
        d_datetime = d[0].strftime('%Y-%m-%d %H:%M:%S')
        d_date = d[0].strftime('%Y-%m-%d')
        d_time = d[0].strftime('%H:%M:%S')
        d_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            d_text = d[2].replace("'", "''")
        except Exception as e:
            print(d)
            print(e)
        s1 = s1 + f"""\n    ('{d[3]}', \
'{business_id}', \
'{d[4]}', \
{d[1]}, \
'{d_datetime}', \
'{d_date}', \
'{d_time}', \
'{d_text}', \
'{d_now}'),"""

#     s2 = '''
# ON CONFLICT ON CONSTRAINT yelp_review_pkey
# DO UPDATE SET
#     business_id = excluded.business_id,
#     user_id = excluded.user_id,
#     stars = excluded.stars,
#     datetime = excluded.datetime,
#     date = excluded.date,
#     time = excluded.time,
#     text = excluded.text,
#     timestamp = excluded.timestamp;    
# '''
    s2 = '''
ON CONFLICT ON CONSTRAINT yelp_review_pkey
DO NOTHING;  
'''
    sql= s0 +s1[:-1] + s2
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
    except Exception as e:
        print(e)
        return 1 # returncode 1 = failure
    return 0 # returncode 0 = success


def getYelpReviews2(location='Phoenix',
                    categories='cafe,coffee',
                    limit=20000):
    '''get Yelp reviews by location and categories'''
    sql = f'''
    SELECT r FROM tallyds.yelp_business AS b
    JOIN tallyds.yelp_review AS r
    ON b.business_id = r.business_id
    WHERE location = '{location}'
    AND categories = '{categories}'
    LIIMT {limit};
    '''
    try: 
        with connection.cursor() as cursor:
            cursor.execute(sql)
            # return a list of texts
            return [r[0] for r in cursor.fetchall()]
    except Exception as e:
        print(e)

###############################################################
# tallyds.yelp_reivew_log
###############################################################
def getLatestYelpReviewLog(business_id):
    sql = f'''
    SELECT datetime
    FROM tallyds.yelp_review_log
    WHERE business_id = '{business_id}'
    ORDER BY datetime DESC
    LIMIT 1;
    '''
    with connection.cursor() as cursor:
        cursor.execute(sql)
        # return a list of tuples
        return cursor.fetchall()


def insertYelpReviewLog(business_id,
                        date):
    sql = f"""
    INSERT INTO tallyds.yelp_review_log VALUES
    (
        '{business_id}',
        '{date.strftime('%Y-%m-%d')}',
        CURRENT_TIMESTAMP
    )
    ON CONFLICT ON CONSTRAINT yelp_review_log_pkey
    DO UPDATE SET
        datetime = excluded.datetime,
        timestamp = excluded.timestamp
    ;
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
    except Exception as e:
        print(e)


###############################################################
# tallyds.job_log
###############################################################
def getJobLogs(business_id,
               limit=100):
    # uuid, 
    # business_id,
    # job_type,
    # job_status,
    # timestamp,
    # job_message
    sql = f'''
    SELECT *
    FROM tallyds.job_log
    WHERE business_id = '{business_id}'
    ORDER BY timestamp DESC
    LIMIT {limit};
    '''
    with connection.cursor() as cursor:
        cursor.execute(sql)
        # return a list of tuples
        return cursor.fetchall()


def insertJobLogs(business_id,
                  job_type,
                  job_status,
                  job_message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql = f'''\
    INSERT INTO tallyds.job_log
    VALUES (
        uuid_generate_v4(), 
	    '{business_id}',
	    {job_type},
	    {job_status},
	    '{timestamp}',
        '{job_message}'
    );'''
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
    except Exception as e:
        print(str(e))
        return 1 # returncode failure
    return 0 # returncode success


def getFailedJobLogs(job_type=0, # 0: triggered by task or job, 1: triggered by end users
                     timestamp=datetime.now().strftime('%Y-%m-%d')):
    sql = f"""
    SELECT DISTINCT ON (business_id) business_id, job_status
    FROM tallyds.job_log 
    WHERE timestamp >= '{timestamp}'
    ORDER BY business_id, timestamp DESC;
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            # return a list of business IDs
            return [r[0] for r in cursor.fetchall() if r[1]==1]
    except Exception as e:
        print(str(e))
        return []


###############################################################
# tallyds.job_config
###############################################################
def getJobConfig():
    sql = """
    SELECT * FROM tallyds.job_config;
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        return  cursor.fetchall() # return a list of tuples


###############################################################
# tallyds.tally_business
###############################################################
def getTallyBusiness():
    '''Businesses selected by Tally users'''
    sql = '''
    SELECT business_id
    FROM tallyds.tally_business;
    '''
    with connection.cursor() as cursor:
        cursor.execute(sql)
        # return a list of strings
        return [r[0] for r in cursor.fetchall()]


def isTallyBusiness(business_id):
    sql = f"""
    SELECT business_id
    FROM tallyds.tally_business
    WHERE business_id = '{business_id}';
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            # return a list of strings
            return len(cursor.fetchall()) > 0
    except Exception as e:
        print(e)
        return False


def insertTallyBusiness(business_ids):
    if business_ids is None or len(business_ids) == 0:
        return 0

    s1 = ""
    for business_id in business_ids:
        s1 = s1 + f"('{business_id}', CURRENT_TIMESTAMP),"

    sql = f"""
    INSERT INTO tallyds.tally_business VALUES
    {s1[:-1]}
    ON CONFLICT ON CONSTRAINT tally_business_pkey
    DO NOTHING;
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            return 0 # success
    except Exception as e:
        print(e)
        return 1 # error


###############################################################
# tallyds.ds_vizdata
###############################################################
def updateVizdata(business_id,
                  viztype,
                  vizdata):
    if vizdata is None or len(vizdata) == 0:
        return 0
        
    sql=f'''\
    INSERT INTO tallyds.ds_vizdata VALUES
    (
        '{business_id}',
        {viztype},
        current_timestamp,
        '{vizdata.replace("'", "''")}'
    )
    ON CONFLICT ON CONSTRAINT ds_vizdata_pkey
    DO UPDATE SET
        timestamp = excluded.timestamp,
        vizdata = excluded.vizdata
    ;
    '''
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            return 0 # success
    except Exception as e:
        print(e)
        return 1 # failure


def getVizdataTimestamp(business_id,
                        viztype):
    sql=f'''
    SELECT timestamp
    FROM tallyds.ds_vizdata
    WHERE business_id = '{business_id}'
    AND viztype = {viztype}
    LIMIT 1; 
    '''
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql) 
            return cursor.fetchall() # return a list of tuples
    except Exception as e:
        print(e)
        return 0


def getLatestVizdata(business_id,
                     viztype,
                     days=14):
    timestamp = datetime.now() - timedelta(days=days)
    sql=f'''
    SELECT vizdata, 
           timestamp
    FROM tallyds.ds_vizdata
    WHERE business_id = '{business_id}'
    AND viztype = {viztype}
    AND timestamp >= '{timestamp.strftime('%Y-%m-%d')}'; 
    '''
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql) 
            # return a list of tuples
            return cursor.fetchall()
    except Exception as e:
        print(e)   
        return []


def deleteVizdata(business_id):
    sql = """
    DELETE FROM tallyds.ds_vizdata 
    WHERE business_id = '{business_id}';
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql) 
            return 0 # success
    except Exception as e:
        print(e)
        return 1 # failure


###############################################################
# tallyds.ds_vizdata_log
###############################################################
def insertVizdataLog(business_id,
                     viztype,
                     triggeredby):
    sql=f'''
    INSERT INTO tallyds.ds_vizdata_log
    VALUES (
        uuid_generate_v4(),
        '{business_id}',
        {viztype},
        '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}',
        {triggeredby}
    );
    '''
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql) 
            return 0 # success
    except Exception as e:
        print(e)
        return 1 # failure


###############################################################
# tallyds.yelp_business
###############################################################
def insertYelpBusiness(businesses):       
    s1 = """
    INSERT INTO tallyds.yelp_business 
    (business_id, city, timestamp, location, categories) 
    VALUES
    """
    s2 = ""
    for b in businesses:
        # business_id, city, timestamp, location, categories
        s2 = s2 + f"('{b[0]}', '{b[1]}', CURRENT_TIMESTAMP, '{b[2]}', '{b[3]}'),"
    s3 = """\
    ON CONFLICT ON CONSTRAINT yelp_business_pkey
    DO UPDATE SET
        timestamp = excluded.timestamp,
        location = excluded.location,
        categories = excluded.categories;
    """
    sql = s1 + s2[:-1] + s3
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql) 
            return 0 # success
    except Exception as e:
        print(e)
        return 1 # failure


def getYelpBusinessIDs(location='Phoenix',
                       categories='cafe,coffee'):
    sql = f"""
    SELECT business_id
    FROM tallyds.yelp_business
    WHERE location = '{location}'
    AND categories = '{categories}';
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql) 
            # return a list of business IDs
            return [r[0] for r in cursor.fetchall()] 
    except Exception as e:
        print(e)
        return []