import pandas as pd
import numpy as np
import requests
import re
import math


def getYelpPhrases(yelpScraperResult):
    df = yelpScraperResult
    df = df.dropna()
    df['only_alphabets'] = df[1].apply(lambda x: ' '.join(re.findall("[a-zA-Z]+", x)))

    df['word_segments_unpacked'] = df['only_alphabets'].apply(lambda x: x[1:-1].split(' '))#turn string comma separated list per word

    df['word_segments_unpacked'] = df['word_segments_unpacked'].astype(str)

    df['word_segments_unpacked'] = df['word_segments_unpacked'].apply(lambda x: ''.join([str(i) for i in x]))
    df['word_segments_unpacked'] = df['word_segments_unpacked'].str.lower()

    phrase_count = df[['word_segments_unpacked', 2]]

    s= phrase_count.apply(lambda x: pd.Series(x['word_segments_unpacked']),axis=1).stack().reset_index(level=1, drop=True)
    s.name = 'word_segments_unpacked'

    phrase_count = phrase_count.drop('word_segments_unpacked', axis=1).join(s)
    phrase_count = pd.DataFrame(df['word_segments_unpacked'].str.split(',').tolist(), index=df[2]).stack()

    phrase_count = phrase_count.reset_index()[[0, 2]] # var1 variable is currently labeled 0
    phrase_count.columns = ['word_segments_unpacked', 'ratings'] # renaming var1
    phrase_count = phrase_count.reset_index(drop=False)

    replace_dict_phrase_count = {'[':'',']':'','-':'','!':'','.':'',' ':'',"'":''}
    for key in replace_dict_phrase_count.keys():
        phrase_count['word_segments_unpacked'] = phrase_count['word_segments_unpacked'].str.replace(key, replace_dict_phrase_count[key])
        phrase_count['word_segments_unpacked'] = phrase_count['word_segments_unpacked'].str.lower()

    stopwords = ['"','+','@','&','*','\\',')','(','\(','\xa0','0','1','2','3','4','5','6','7','8','9','/','$',"'d","'ll","'m",'+','maybe','from','first','here','only','put','where','got','sure','definitely','food','yet','our','go','since','really','very','two',"n't",'with','if',"'s",'which','came','all','me','(',')','makes','make','were','immediately','get','been','ahead','also','that','one','have','see','what','to','we','had','.',"'re",'it','or','he','she','we','us','how','went','no','"','of','has','by','bit','thing','place','so','ok','and','they','none','was','you',"'ve",'did','be','and','but','is','as','&','you','has','-',':','and','had','was','him','so','my','did','would','her','him','it','is','by','bit','thing','place','[',']','while','check-in','=','= =','want', 'good','husband', 'want','love','something','your','they','your','cuz','him',"i've",'her','told', 'check', 'i"m', "it's",'they', 'this','its','they','this',"don't",'the',',', 'it', 'i"ve', 'i"m', '!', '1','2','3','4', '5','6','7','8','9','0','/','.']
    def filter_stopwords(text):
        for i in str(text):
            if i not in stopwords:
                return str(text)

    #if item in stopwords list partially matches, delete, single letters like 'i' would be deleted from inside individual words if in list
    phrase_count = phrase_count[~phrase_count['word_segments_unpacked'].isin(stopwords)]
    # if the following words fully matches, filter out
    full_match_list = ['i','a','an','am','at','are','in','on','for','','\xa0\xa0','\xa0','\(']
    phrase_count = phrase_count[~phrase_count['word_segments_unpacked'].isin(full_match_list)]

    #pivot table ratings
    phrase_count_pivot = pd.pivot_table(phrase_count, index='word_segments_unpacked', columns='ratings', aggfunc='count', fill_value=0)
    phrase_count_pivot.columns = [''.join(col).strip() for col in phrase_count_pivot.columns.values]#flatten index levels part 1
    phrase_count_pivot = pd.DataFrame(phrase_count_pivot.to_records())#flatten index levels part 2

    #if there are no _# star reviews, add a column of zeros
    required_column_names = ['index1.0 star rating', 'index2.0 star rating','index3.0 star rating','index4.0 star rating','index5.0 star rating']
    for i in required_column_names:
        if i not in phrase_count_pivot.columns:
            phrase_count_pivot[i] = 0

    #replace the original count by getting an exaggerated scaled tally of reviews to calculate score
    phrase_count_pivot['index1.0 star rating'] = phrase_count_pivot['index1.0 star rating']*(-2)
    phrase_count_pivot['index2.0 star rating'] = phrase_count_pivot['index2.0 star rating']*(-1)
    phrase_count_pivot['index3.0 star rating'] = phrase_count_pivot['index3.0 star rating']*(-0.1)
    phrase_count_pivot['index4.0 star rating'] = phrase_count_pivot['index4.0 star rating']*(1)
    phrase_count_pivot['index5.0 star rating'] = phrase_count_pivot['index5.0 star rating']*(2)

    #get a total score from the sum of exaggerated scores
    phrase_count_pivot['score'] = phrase_count_pivot['index1.0 star rating'] + phrase_count_pivot['index2.0 star rating'] + phrase_count_pivot['index3.0 star rating'] + phrase_count_pivot['index4.0 star rating'] + phrase_count_pivot['index5.0 star rating']

    phrase_count_pivot['score'] = phrase_count_pivot['score'].div(phrase_count_pivot['score'].max(), axis=0)#normalize
    phrase_count_pivot['score'] = phrase_count_pivot['score'].round(decimals=4)#round to 4 decimal places
    phrase_count_pivot = phrase_count_pivot.sort_values(by=('score'), ascending=False)
    x,y = phrase_count_pivot.shape#tuple unpacking to get the length of the dataframe

    top_terms_list = []
    for i in range(math.ceil(x/3)):
    # for i in range(100):
        try:
            new_df = df[df[1].str.contains(phrase_count_pivot['word_segments_unpacked'].iloc[i])]#if word appears in review, create a dataframe with each row being the word occurring in a different review
            pos_first_df = new_df.sort_values(by=2, ascending=False)#rank the dataframe with most positive reviews first
            if pos_first_df[1].iloc[0] not in top_terms_list:#get the highest star rating review
                top_terms_list.append(pos_first_df[1].iloc[0])
                top_terms_list.append(pos_first_df[1].iloc[1])
        except IndexError as e:
            pass
    worst_terms_list = [] 
    for i in reversed(range(math.ceil(x/3), x)):
    # for i in range(-50,0):
        try:
            new_df = df[df[1].str.contains(phrase_count_pivot['word_segments_unpacked'].iloc[i])]#if word appears in review, create a dataframe with each row being the word occurring in a different review
            neg_first_df = new_df.sort_values(by=2, ascending=True)#rank the dataframe with worst reviews first
            if neg_first_df[1].iloc[0] not in worst_terms_list:#get the lowest star rating review
                worst_terms_list.append(neg_first_df[1].iloc[0])#prevent duplicates
                worst_terms_list.append(neg_first_df[1].iloc[1])#prevent duplicates
        except IndexError as e:
            pass

    negative_list = []
    # for i in range(-30,0):#take the worst 30 terms
    for i in reversed(range(math.ceil(2*x/3), x)):
        for list_of_words in worst_terms_list:
            word_list = list_of_words.split(' ')
            for word in word_list:
                try: 
                    if phrase_count_pivot['word_segments_unpacked'].iloc[i] == word: #find word occurrence in original comma separated word list of reviews
                        try:
                            index = word_list.index(word)
                            string_from_phrases = ','.join(word_list[max(0,index-5):min(index+5, len(word_list))])
                            negative_list.append(string_from_phrases)
                        except ValueError as e:
                            pass
                except IndexError as e:#if there are less than 30 words after stopword filtering, just get the first word and its occurrence in the original review
                    if phrase_count_pivot['word_segments_unpacked'].iloc[0] == word:
                        try:
                            index = word_list.index(word)
                            string_from_phrases = ','.join(word_list[max(0,index-5):min(index+20, len(word_list))])
                            negative_list.append(string_from_phrases)
                        except ValueError as e:
                            pass
    negative_df = pd.DataFrame(negative_list)
    negative_df = negative_df.reset_index(drop=False)
    negative_df = negative_df.rename(columns={'index':'score', 0 : 'term'})
    negative_df = negative_df.drop_duplicates(subset='term')
    x,y = negative_df.shape#tuple unpacking to get the length of the dataframe
    if x < 10:
        # for i in range(-40,-30):
        for i in reversed(range(math.ceil(x/3), math.ceil(2*x/3))):
            for list_of_words in worst_terms_list:
                word_list = list_of_words.split(' ')
                for word in word_list:
                    try:
                        if phrase_count_pivot['word_segments_unpacked'].iloc[i] == word:
                            try:
                                index = word_list.index(word)
                                string_from_phrases = ','.join(word_list[max(0,index-5):min(index+20, len(word_list))])
                                negative_list.append(string_from_phrases)
                            except ValueError as e:
                                pass
                    except IndexError as e:
                        if phrase_count_pivot['word_segments_unpacked'].iloc[0] == word:
                            try:
                                index = word_list.index(word)
                                string_from_phrases = ','.join(word_list[max(0,index-5):min(index+20, len(word_list))])
                                negative_list.append(string_from_phrases)
                            except ValueError as e:
                                pass
    negative_df_addon = pd.DataFrame(negative_list)
    negative_df_addon = negative_df_addon.reset_index(drop=False)
    negative_df_addon = negative_df_addon.rename(columns={'index':'score', 0 : 'term'})
    negative_df = pd.concat([negative_df, negative_df_addon])
    negative_df['term'] = negative_df['term'].str.replace(',',' ')
    negative_df = negative_df.head(10)


    positive_list = []
    for i in range(math.ceil(x/3)):
    # for i in range(0,30):
        for list_of_words in top_terms_list:
            word_list = list_of_words.split(' ')
            for word in word_list:
                try: 
                    if phrase_count_pivot['word_segments_unpacked'].iloc[i] == word:
                        try:
                            index = word_list.index(word)
                            string_from_phrases = ','.join(word_list[max(0,index-5):min(index+20, len(word_list))])
                            positive_list.append(string_from_phrases)
                        except ValueError as e:
                            pass
                except IndexError as e:
                    if phrase_count_pivot['word_segments_unpacked'].iloc[0] == word:
                        try:
                            index = word_list.index(word)
                            string_from_phrases = ','.join(word_list[max(0,index-5):min(index+20, len(word_list))])
                            positive_list.append(string_from_phrases)
                        except ValueError as e:
                            pass
    positive_df = pd.DataFrame(positive_list)
    positive_df = positive_df.reset_index(drop=False)
    positive_df = positive_df.rename(columns={'index':'score', 0 : 'term'})
    positive_df = positive_df.drop_duplicates(subset='term')
    x,y = positive_df.shape#tuple unpacking to get the length of the dataframe
    # for i in range(30,40):
    for i in range((math.ceil(x/3))+1, math.ceil(x/1.5)):
        for list_of_words in top_terms_list:
            word_list = list_of_words.split(' ')
            for word in word_list:
                try:
                    if phrase_count_pivot['word_segments_unpacked'].iloc[i] == word:
                        try:
                            index = word_list.index(word)
                            string_from_phrases = ','.join(word_list[max(0,index-5):min(index+20, len(word_list))])
                            positive_list.append(string_from_phrases)
                        except ValueError as e:
                            pass
                except IndexError as e:
                    if phrase_count_pivot['word_segments_unpacked'].iloc[0] == word:
                        try:
                            index = word_list.index(word)
                            string_from_phrases = ','.join(word_list[max(0,index-5):min(index+20, len(word_list))])
                            positive_list.append(string_from_phrases)
                        except ValueError as e:
                            pass
    positive_df_addon = pd.DataFrame(positive_list)
    positive_df_addon = positive_df_addon.reset_index(drop=False)
    positive_df_addon = positive_df_addon.rename(columns={'index':'score', 0 : 'term'})
    positive_df = pd.concat([positive_df, positive_df_addon])
    positive_df['term'] = positive_df['term'].str.replace(',',' ')
    positive_df = positive_df.head(10)


    results = {'positive': [{'term': pos_term, 'score': pos_score} for pos_term, pos_score in zip(positive_df['term'], positive_df['score'])], 'negative': [{'term': neg_term, 'score': neg_score} for neg_term, neg_score in zip(negative_df['term'], negative_df['score'])]}
    return results