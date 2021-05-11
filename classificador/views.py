from django.shortcuts import render
from django.conf import settings
from .models import Search, Tweet
from .forms import searchForm

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from requests_oauthlib import OAuth1Session
from nltk.tokenize import TweetTokenizer
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
tweet_tokenizer = TweetTokenizer() 


import tweepy
import pickle
import requests
import numpy as np
import nltk
import pandas as pd
import re

# Create your views here.

def index(request):

    #Carrega o dataset
    dfPolitica = pd.read_csv(settings.MEDIA_ROOT + "/dfPolitica.csv")

    # Removendo os valores duplicados da base de dados de treino e teste:
    dfPolitica.drop_duplicates(['Text'], inplace=True)

    # Separando colunas das bases de dados:
    tweets_politica = dfPolitica['Text']
    sentimento = dfPolitica['Classificacao']

    #Tokens de acesso 
    API_KEY = 'e8N1hBjwDk9c4MZAuthUzkcua'
    API_SECRET = '3ATL4Z0Ocjy1ORo9tIfFb6HJQcI2Ck1i2MUBirJOco89LH51qt'
    ACCESS_TOKEN ='572960821-NK3JWnBXn5ZIMIrxVMxv9k8XLH77meXjmAwOC7D2'
    ACCESS_TOKEN_SECRET ='gJkYzuXdoyxraU4FCN4JKqajpUzR33v2eqCTVeVDtr0Dx'

    auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
    auth.set_access_token(ACCESS_TOKEN , ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)


    #Lista vazia para armazenar tweets
    tweets_list = []
    tweets_screen_name = []

    context = {}

    if request.method == 'POST':
        
        search_query = request.POST.get('search_query')
        search_word = requests.utils.quote(search_query)
        public_tweets = api.search(search_word + ' -filter:retweets', lang='pt', count=100, tweet_mode='extended')

        for tweet in public_tweets:  
            tweets_screen_name.append(tweet.user.screen_name)
            tweets_list.append(tweet.full_text)
        
        def Limpeza_dados(instancia):
            # remove links, pontos, virgulas,ponto e virgulas dos tweets
            instancia = re.sub("http\S+", "", instancia).lower().replace('.','').replace(';','').replace('-','').replace(':','').replace(')','').replace('amg','amigo').replace('amgs', 'amigos').replace('pq', 'porque')
            return (instancia)
        
        def Removing_mentions(text):
            text = re.sub(r"(?:\@|https?\://)\S+", "", text)
            return (text)

        tweets_list = [Limpeza_dados(i) for i in tweets_list]
        tweets_list = [Removing_mentions(i) for i in tweets_list]
       

        # Instancia o objeto que faz a vetorização dos dados de texto:
        vectorizer = CountVectorizer(analyzer="word", tokenizer=tweet_tokenizer.tokenize)

        # Aplica o vetorizador nos dados de texto:
        vec_tweets_politica = vectorizer.fit_transform(tweets_politica)

        vec_tweets = vectorizer.transform(tweets_list)

        #Carrega o modelo treinado
        loaded_model = pickle.load(open(settings.MEDIA_ROOT  + "/modelo_salvo.pkl", 'rb'))

        #Modelo predict
        classificacao = loaded_model.predict(vec_tweets)
        print(classificacao)

        total = 0
        numPos = 0
        numNeg = 0
        

        for tweet_name, tweet, classf in zip (tweets_screen_name, tweets_list,classificacao):
            #Estatísticas
            total += 1
            if classf == 1: 
                numPos += 1 
            else:
                numNeg += 1
            print('[NAME]: ' + tweet_name)
            print ("[TEXTO]" + tweet + "|| [POLARIDADE]: "+ str(classf)) 
            print('\n')
            
        
        mylists = zip(tweets_screen_name, tweets_list, classificacao)
        last_tweet = tweets_list[-1]

        #Sentimento geral
        mediaPos = (numPos/total)*100 
        mediaNeg = (numNeg/total)*100

        #Estatísticas
        print('Porcentagem de comentários positivos: '+str(mediaPos))
        print('Porcentagem de comentários negativos: '+str(mediaNeg))
        print("\n")
        print('Positivos: ' + str(numPos))
        print('Negativos: ' + str(numNeg))


        context = {
            'mediaPos': mediaPos,
            'mediaNeg': mediaNeg,
            'tweet': tweet,
            'classf': classf,
            'tweet_name': tweet_name,
            'numPos': numPos,
            'numNeg': numNeg,
            'mylists': mylists,
            'last_tweet': last_tweet,
            'search_query':search_query,

        }

    return render(request, 'classificador/index.html', context)
                        

        