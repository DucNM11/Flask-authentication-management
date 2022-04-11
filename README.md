# Cloud Computing Mini Project ECS781P

![arch](https://user-images.githubusercontent.com/37650605/162621233-fa1fcb96-ce28-469e-81b4-0aa590e137ec.jpeg)

# External APIs
The Crypto Summariser aims to consolidate information from multiple external sources and provide it to the user in a single call. At the moment, we have implemented two data sources using the CoinMarketCap and Twitter public APIs. This data is collected and pushed to a Cloud SQL instance, ready to serve to the user. 

We start by querying the top 20 coins, by current market cap, from the CoinMarketCap API where we retrieve the coin metadata:(symbol, name, rank etc.) as well as some basic financial infomration: ['quote_GBP_price','quote_GBP_volume_24h','quote_GBP_volume_change_24h','quote_GBP_percent_change_1h','quote_GBP_percent_change_24h'].

With this list of top coins, we additionaly use the Twitter API to get the current sentiment and popularity of the coin. This is implemented by retrieving the latest 100 tweets which mention the coin's name:
```
response = client.search_recent_tweets(
        searchstring,
        max_results=100,
    )
    tweets = response.data
```
We then filter for english-only tweets, remove stopwords and perform some basic sentiment analysis, using the NLTK library, to get a current average sentiment:

```
def getaveragesentiment(tweets):
    """for a list of tweets, get the average sentiment of each 
        tweet. 
    """
    
    tweetsentiment = 0
    sia = SentimentIntensityAnalyzer()
    for tweet in tweets:
        sentiment = sia.polarity_scores(tweet.text)
        tweetsentiment = tweetsentiment + sentiment["pos"] - sentiment["neg"]

    tweetsentiment = tweetsentiment / len(tweets)

    return tweetsentiment
```

Additionally, we compute a popiarity score, which is a measure of the frequency of Tweets - the inverse of the amount of time between the 1st and 100th most recent Tweets. This is then normalised by the frequency of bitcoin tweets, such that values over 1 are being tweeted about more frequently that bitcoin, and below 1 is less frequently.

Once the table has been populated with both sources of info, it is pushed to the cloud sql instance, ready to be served to the user of our Crypto Summariser app. In this proof of concept, we have simply run the code in advance to populate the table in the database, however in production we would run this as a cron job e.g. every 5 mins to provide the most up-to-date info to the user:

```
5 * * * * ./coinmarketapi.py
````

    
