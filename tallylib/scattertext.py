import pandas as pd
import spacy
import scattertext as st
import re
from collections import Counter
from flashtext import KeywordProcessor
from .scraper import yelpScraper


nlp = spacy.load("en_core_web_sm/en_core_web_sm-2.2.5")

def getYelpWords(yelpScraperResult):
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
    results = {'positive': [{'term': pos_term, 'score': pos_score} for pos_term, pos_score in
                            zip(positive_df['term'], positive_df['score'])],
               'negative': [{'term': neg_term, 'score': neg_score} for neg_term, neg_score in
                            zip(negative_df['term'], negative_df['score'])]}
    return results

def getYelpNouns(yelpScraperResult):
    df = yelpScraperResult
    def customtokensize(text):
        return re.findall("[\w']+", str(text))

    df['tokenized_text'] = df[1].apply(customtokensize)
    # stopwords = ['and','was','were','had','check-in','=','= =','u','want', 'u want', 'cuz','him',"i've",'on', 'her','told','ins', '1 check','I', 'i"m', 'i', ' ', 'it', "it's", 'it.','they', 'the', 'this','its', 'l','they','this',"don't",'the ', ' the', 'it', 'i"ve', 'i"m', '!', '1','2','3','4', '5','6','7','8','9','0','/','.',',']

    stopwords = [',','"','!','-','&','?']

    def filter_stopwords(text):
        nonstopwords = []
        for i in text:
            if i not in stopwords:
                nonstopwords.append(i)
        return nonstopwords
    df['tokenized_text'] = df['tokenized_text'].apply(filter_stopwords)
    df['parts_of_speech_reference'] = df['tokenized_text'].apply(filter_stopwords)
    df['parts_of_speech_reference'] = df['parts_of_speech_reference'].str.join(' ')

    def find_word_segment_combined(x):
        noun_list = []
        doc = nlp(str(x))
        try:
            for token in range(len(doc)):
                sub_list = []
                if doc[token].pos_ == 'NOUN'and doc[token+1].pos_ == 'NOUN':
                        sub_list.append(doc[token])
                        sub_list.append(doc[token+1])
                if len(sub_list) != 0 and sub_list not in noun_list:
                        noun_list.append(sub_list)
        except IndexError as e:
            pass
        return noun_list

    df['word_segments'] = df[1].apply(find_word_segment_combined)
    word_phrases = []
    for i in df['word_segments']:
        for x in i:
            string = ' '.join([str(elem) for elem in x]) 
            word_phrases.append(string)
    keyword_processor = KeywordProcessor(case_sensitive=False)
    for phrase in word_phrases:
        keyword_processor.add_keyword(phrase)
    feature_extractor = FlashTextExtact().set_keyword_processor(keyword_processor)

    df['parse'] = df[1].apply(st.whitespace_nlp_with_sentences)
    corpus = (st.CorpusFromPandas(df,
                                category_col=2,
                                text_col=1,
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
    