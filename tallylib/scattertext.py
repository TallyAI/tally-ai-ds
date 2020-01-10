import pandas as pd
import spacy
import scattertext as st
import re
from collections import Counter
from flashtext import KeywordProcessor
from .scraper import yelpScraper

nlp = spacy.load("./down_sm/en_core_web_sm-2.1.0/en_core_web_sm/en_core_web_sm-2.1.0")
# nlp = spacy.load("en_core_web_sm/en_core_web_sm-2.2.5")

def getYelpWordsReviewFreq(yelpScraperResult):
    df = yelpScraperResult

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

    df = df.rename(columns = {0:'date', 2:'stars',1:'text'})
    df['date'] = df['date'].str.replace('\n','')
    df['date'] = df['date'].str.replace(' ','')
    df['date'] = df['date'].astype('datetime64[ns]')
    ratingDict = {'5.0 star rating':5,'4.0 star rating':4, '3.0 star rating':3, '2.0 star rating':2, '1.0 star rating':1}
    df['stars'] = df['stars'].map(ratingDict) 
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['week_number_of_year'] = df['date'].dt.week
    bydate = df.groupby(['year', 'month','week_number_of_year']).mean()
    bydate = pd.DataFrame(bydate.to_records())#flatten groupby column
    bydate = bydate.iloc[::-1]
    bydate = bydate.head(8)
    bydate['cumulative_avg_rating'] = bydate['stars'].mean()

    results = {'viztype0':{'positive': [{'term': pos_term, 'score': pos_score} 
                            for pos_term, pos_score in zip(positive_df['term'], positive_df['score'])], 
                        'negative': [{'term': neg_term, 'score': neg_score} 
                                        for neg_term, neg_score in zip(negative_df['term'], negative_df['score'])]},
                'viztype3':{'const star_data': [{'date': term, 'cumulative_avg_rating': current_rating, 'weekly_avg_rating': week_rating}
                                        for term, current_rating, week_rating in zip(bydate['week_number_of_year'], bydate['cumulative_avg_rating'], bydate['stars'])]}
                }
    return results


def getYelp3Words(yelpScraperResult):
    df = yelpScraperResult
    def customtokensize(text):
        return re.findall("[\w']+", str(text))

    df['tokenized_text'] = df[1].apply(customtokensize)
    stopwords = ['and','was','were','had','check-in','=','= =','u','want', 'u want', 'cuz','him',"i've",'on', 'her','told','ins', '1 check','I', 'i"m', 'i', ' ', 'it', "it's", 'it.','they', 'the', 'this','its', 'l','they','this',"don't",'the ', ' the', 'it', 'i"ve', 'i"m', '!', '1','2','3','4', '5','6','7','8','9','0','/','.',',']

    def filter_stopwords(text):
        nonstopwords = []
        for i in text:
            if i not in stopwords:
                nonstopwords.append(i)
        return nonstopwords
    df['tokenized_text'] = df['tokenized_text'].apply(filter_stopwords)
    df['parts_of_speech_reference'] = df['tokenized_text'].apply(filter_stopwords)
    df['parts_of_speech_reference'] = df['parts_of_speech_reference'].str.join(' ')

    def find_noun_noun(x):
        noun_list = []
        doc = nlp(str(x))
        try:
            for token in range(len(doc)):
                sub_list = []
                if doc[token].pos_ == 'NOUN'and doc[token+1].pos_ == 'NOUN':
                    sub_list.append(doc[token-1])
                    sub_list.append(doc[token])
                    sub_list.append(doc[token+1])
                if len(sub_list) != 0 and sub_list not in noun_list:
                    noun_list.append(sub_list)
        except IndexError as e:
            pass
        return noun_list

    def find_adj_noun(x):
        adj_noun_list = []
        doc = nlp(str(x))
        try:
            for token in range(len(doc)):
                sub_list = []
                if doc[token].pos_ == 'ADJ'and doc[token+1].pos_ == 'NOUN':
                    sub_list.append(doc[token-1])
                    sub_list.append(doc[token])
                    sub_list.append(doc[token+2])
                if len(sub_list) != 0 and sub_list not in adj_noun_list:
                    adj_noun_list.append(sub_list)
        except IndexError as e:
            pass
        return adj_noun_list

    def find_the(x):
        the_list = []
        doc = nlp(str(x))
        try:
            for token in range(len(doc)):
                sub_list = []
                if doc[token].text == 'the' or doc[token].text == 'a' or doc[token].text == 'an':
                    sub_list.append(doc[token+1])
                    sub_list.append(doc[token+2])
                    sub_list.append(doc[token+3])
                    # sub_list.append(doc[token+4])
                if len(sub_list) != 0 and sub_list not in the_list:
                    the_list.append(sub_list)
        except IndexError as e:
            pass
        return the_list

    df['word_segments_nn'] = df['parts_of_speech_reference'].apply(find_noun_noun)
    df['word_segments_adjn'] = df['parts_of_speech_reference'].apply(find_adj_noun)
    df['word_segments_the'] = df['parts_of_speech_reference'].apply(find_the)

    noun_noun_phrases = []
    string = ''
    for i in df['word_segments_nn']:
        for x in i:
            string = ' '.join([str(elem) for elem in x]) 
            noun_noun_phrases.append(string)
    adj_noun_phrases = []
    for i in df['word_segments_adjn']:
        for x in i:
            string = ' '.join([str(elem) for elem in x]) 
            adj_noun_phrases.append(string)
    the_phrases = []
    for i in df['word_segments_the']:
        for x in i:
            string = ' '.join([str(elem) for elem in x]) 
        the_phrases.append(string)

    all_phrases = noun_noun_phrases + adj_noun_phrases + the_phrases
    class FlashTextExtact(st.FeatsFromSpacyDoc):
        '''
        '''
        def set_keyword_processor(self, keyword_processor):
            '''
            :param keyword_processor: set, phrases to look for
            :return: self
            '''
            self.keyword_processor_ = keyword_processor
            return self

        def get_feats(self, doc):
            '''
            Parameters
            ----------
            doc, Spacy Doc
            Returns
            -------
            Counter noun chunk -> count
            '''
            return Counter(self.keyword_processor_.extract_keywords(str(doc)))
    keyword_processor = KeywordProcessor(case_sensitive=False)

    for phrase in all_phrases:
        keyword_processor.add_keyword(phrase)
    feature_extractor = FlashTextExtact().set_keyword_processor(keyword_processor)

    df['parse'] = df['parts_of_speech_reference'].apply(st.whitespace_nlp_with_sentences)
    corpus = (st.CorpusFromPandas(df,
                                category_col=2,
                                text_col='parts_of_speech_reference',
                                nlp=st.whitespace_nlp_with_sentences,
                                feats_from_spacy_doc=feature_extractor)
            .build())

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
    return results
    