# Define a function to return the sentiment score of a comment
from textblob import TextBlob
def sentiment_score(comment):
    score = round(TextBlob(comment).sentiment.polarity, 3) 
    # the more negative the ouput value the, the more negative the sentiment of the comment
    return score


# (optional) Define a function to return cleanedu up text blobs
# import re
# import nltk
# from nltk.corpus import stopwords

# def clean_text(text):
#     REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
#     BAD_SYMBOLS_RE = re.compile('[^0-9a-z #+_]')
#     STOPWORDS = set(stopwords.words('english'))
#     text = text.lower() # lowercase text
#     text = REPLACE_BY_SPACE_RE.sub(' ', text) # replace REPLACE_BY_SPACE_RE symbols by space in text. substitute the matched string in REPLACE_BY_SPACE_RE with space.
#     text = BAD_SYMBOLS_RE.sub('', text) # remove symbols which are in BAD_SYMBOLS_RE from text. substitute the matched string in BAD_SYMBOLS_RE with nothing. 
#     text = text.replace('x', '')
#     text = ' '.join(word for word in text.split() if word not in STOPWORDS) # remove stopwords from text
#     return text


# Query HackerNews dataset for top contributors
def name_lister(df, cutoff): #df should contain by and comments features
    # query for only those commenters with at least 100 comments
    df2 = pd.DataFrame(df.by.value_counts()).reset_index()
    df2 = df2[df2.by >= cutoff]  # cutoff is minimum number of comments per user
    df2 = df2.rename(columns={'index': 'by', 'by': 'amount'})
    names_list = df2.by
    return names_list


# Define a function to return hackers'
#  respective aggregate saltiness ranks
def salt_scorer_mk1(names_list, df): 
    salt_list = []
    df = df[['text', 'by']].dropna()
    for name in names_list:
        comments_list = (df[df.by == name].reset_index()).text
        score_list = []
        for comment in comments_list:
            score = round(TextBlob(comment).sentiment.polarity, 3)
            score_list.append(score)
        saltiness = sum(score_list)/len(score_list)
        salt_list.append(saltiness)
    name_scores = pd.DataFrame(list(zip(names_list, salt_list)), columns = ['name', 'hacker_salt_score'])
    return name_scores


# Rank commenters based on their respective aggregate saltiness
def ranker(df):
    df = df.sort_values(by='hacker_salt_score') # lower values equate to higher saltiness
    df['rank'] = df['hacker_salt_score'].rank()
    return df #a dataset including ranks of hackers 


# Define a function to return a comprehensive tiddy dataset
def salt_scorer_mk2(df, ranked_df):
    # to get ranked_df: ranker(salt_scorer_mk1(name_lister(df, cutoff), df))
    
    df = df[['id','text', 'by']].dropna() 
    # TODO Generate data for an additional 4 features: 
    #  user_rank, comment_saltiness, user_comment_rank, sarcasm
    
    hacker_list = ranked_df.name
    hacker_rank = 1
    
    #prep a table for storage
    full_table = pd.DataFrame(columns = ['id', 'hacker', 'hacker_salt_ranking',
                                       'comment', 'comment_saltiness_score'])
                                        #,'hacker_specific_comment_rank'])
    
    for i in hacker_list:
        comment_list = (df[df.by == i].reset_index()).text
        id_list = (df[df.by == i].reset_index()).id
        name_list = (df[df.by == i].reset_index()).by
        
        comment_salt_score_list = []
        hacker_salt_rank_list = []
        #hacker_specific_comment_rank_list = []
        
        for comment in comment_list:
            score = round(TextBlob(comment).sentiment.polarity, 3)
            comment_salt_score_list.append(score)
            
            hacker_salt_rank_list.append(hacker_rank)
        
        hacker_rank += 1

        part_table = pd.DataFrame(list(zip(id_list, name_list, hacker_salt_rank_list,
                                      comment_list, comment_salt_score_list)),
                             columns = ['id', 'hacker', 'hacker_salt_ranking',
                                       'comment', 'comment_saltiness_score'])
                                        #'hacker_specific_comment_rank'])
        
        full_table = pd.concat([full_table, part_table])
        
    return full_table
# Example run: salt_scorer_mk2(df, ranker(salt_scorer_mk1(name_lister(df, 5000), df)))


# Installs for LSTM below
# !pip install tensorflow
# from tensorflow.keras.preprocessing.sequence import pad_sequences
# from tensorflow.keras.preprocessing.text import Tokenizer
# import re

# # Define a model-maker function for sarcasm_judge function (see below)
# def model_maker():
#     # Instantiate the dataset for modeling
#     sarcasm = pd.read_json('./Sarcasm_Headlines_Dataset.json', lines=True)
#     sarcasm = sarcasm[['headline','is_sarcastic']]

#     # Keep only valid entries for training
#     sarcasm['headline'] = sarcasm['headline'].apply(lambda x: x.lower())
#     sarcasm['headline'] = sarcasm['headline'].apply((lambda x: re.sub('[^a-zA-z0-9\s]','',x)))

#     # Set max-features, sequence x, and pad sequences
#     for idx,row in sarcasm.iterrows():
#         row[0] = row[0].replace('rt',' ')
    
#     max_fatures = 2000
#     tokenizer = text.Tokenizer(num_words=max_fatures, split=' ')
#     tokenizer.fit_on_texts(sarcasm['headline'].values)
#     x = tokenizer.texts_to_sequences(sarcasm['headline'].values)
#     x = pad_sequences(x)
#     y = pd.get_dummies(sarcasm['is_sarcastic']).values

#     # Train/test split
#     x_train, x_test, y_train, y_test = train_test_split(x,y, test_size = 0.20, random_state = 8)

#     # Set model parameters
#     embed_dim = 128
#     lstm_out = 196

#     # Instantiate the model, add layers, compile
#     model = Sequential()
#     model.add(Embedding(max_fatures, embed_dim,input_length = x.shape[1]))
#     model.add(SpatialDropout1D(0.4))
#     model.add(LSTM(lstm_out, dropout=0.2, recurrent_dropout=0.2))
#     model.add(Dense(2,activation='softmax'))
#     model.compile(loss = 'binary_crossentropy', optimizer='adam',metrics = ['accuracy'])
    
#     # Train the model 
#     batch_size = 32
#     history = model.fit(x_train, y_train, 
#                         epochs = 5,
#                         batch_size=batch_size,
#                         verbose = 0)

#     return model


# # Define a function to see if a comment is sarcastic
# def sarcasm_judge(comment, sarcasm_model = model_maker()): # takes string formatted comment
#     comment = [comment]
#     comment = tokenizer.texts_to_sequences(comment)
#     comment = pad_sequences(comment, maxlen=29, dtype='int32', value=0)
    
#     sarcastic = sarcasm_model.predict(comment, batch_size=1, verbose=0)[0]
#     if np.argmax(sarcastic) == 0:
#         return 0
#     elif np.argmax(sarcastic) == 1:
#         return 1
