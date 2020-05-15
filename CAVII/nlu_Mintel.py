
# coding: utf-8

# In[2]:



import pandas as pd
import numpy as np
import json
from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1   import Features, EntitiesOptions, KeywordsOptions

nlu_config ={
  "url": "https://gateway.watsonplatform.net/natural-language-understanding/api",
  "username": "19b036d4-80b8-4fde-aa9a-30fb9d4d43e0",
  "password": "kK4YIIvP3bgK"
}

    
natural_language_understanding = NaturalLanguageUnderstandingV1(
  username='19b036d4-80b8-4fde-aa9a-30fb9d4d43e0',
  password='kK4YIIvP3bgK',
  version='2018-03-16')


def nlu_value(txt1):
    response = natural_language_understanding.analyze(
        text=txt1,
        features=Features(
            emotion=EmotionOptions(
                emotion=True,
                sentiment=True,
                limit=2),
            keywords=KeywordsOptions(
                emotion=True,
                sentiment=True,
                limit=2)))
    #print(json.dumps(response, indent=2))
    result = json.dumps(response, indent=2)
    return result


PI_data_file = "C://Users//Geerthi Mahendran//Documents//Code//Mintel//Mintelpi_attr_complete data_3.xlsx"
data = pd.read_excel(PI_data_file)
data_sentiment_set = set(data['item_id'])
data_sentiment_set = list(data_sentiment_set)

data = data.dropna()
data = data.reset_index()


for i in data_sentiment_set:
    data_current = data.loc[data['item_id'] == i]
    # data_current = data_current.reset_index()
    # print(data_current)
    data_current['sentiment'] = data_current.apply(lambda row: nlu_value(row.verbatim), axis=1)
    SENTIMENT = []
    #SENTIMENT_VALUE = []

    data_current = data_current.reset_index()

    for j in range(0, len(data_current)):
        sent = data_current['sentiment'][j]
        SENTIMENT.append(sent)

    data_current['SENTIMENT'] = SENTIMENT

    #Sentiment Value
    #data_current['SENTIMENT_VALUE'] = SENTIMENT_VALUE


    #OVERALL_SENTIMENT_VALUE = sum(SENTIMENT_VALUE) / len(data_current)

    #if (OVERALL_SENTIMENT_VALUE <= 2):
    #    sentiment_product = "V.Negative"
    #elif (OVERALL_SENTIMENT_VALUE <= 3 and OVERALL_SENTIMENT_VALUE >= 2):
    #    sentiment_product = "Negative"
    #elif (OVERALL_SENTIMENT_VALUE <= 4 and OVERALL_SENTIMENT_VALUE >= 3):
    #    sentiment_product = "Neutral"
    #elif (OVERALL_SENTIMENT_VALUE <= 5 and OVERALL_SENTIMENT_VALUE >= 4):
    #    sentiment_product = "Positive"
    #else:
    #    sentiment_product = "V.Positive"

#print(OVERALL_SENTIMENT_VALUE)

#print(sentiment_product)


#print(json.dumps(response, indent=2))

