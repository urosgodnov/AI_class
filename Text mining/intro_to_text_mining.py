import pandas as pd
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from transformers import pipeline 

data=pd.DataFrame({"id":[0,1,2],"sentence":["Today it's a beautiful day!","Great white shark just ate my leg!","You can't be serious :)"]})
     
data
     
nltk.download('punkt_tab')
     
data["sentence"].apply(nltk.word_tokenize)
     
import regex as re
     
data["sentence"].apply(lambda x: re.findall("[\w]+", x))
     

nltk.download('vader_lexicon')
analyzer = SentimentIntensityAnalyzer()
     

sentences=data["sentence"]
for sentence in sentences:
  print(sentence)
  ss = analyzer.polarity_scores(sentence)
  print(ss)

     
# Load a sentiment analysis pipeline
sentiment_model = pipeline("sentiment-analysis")
results = sentiment_model(data["sentence"].tolist())

for i, res in enumerate(results):
    print(f"Text: {data['sentence'].iloc[i]}")  # Changed texts[i] to data['sentence'].iloc[i]
    print(f"Sentiment: {res['label']}, Confidence: {res['score']:.2f}")