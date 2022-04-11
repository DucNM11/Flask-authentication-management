#!/usr/bin/env python3

from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pandas as pd
import sqlalchemy
import coinsentiment
import datetime
from decouple import Config, RepositoryEnv

DOTENV_FILE = '../.env'
env_config = Config(RepositoryEnv(DOTENV_FILE))
twitter_secret = env_config('TWITTER_SECRET')


def get_data():
    """Getting data from coinmarketcap API
    Authentication values will be stored in .env file that ignored by git for security reason
    """
    # Authentication configuration
    KEY = env_config('COINMARKETCAP_API_KEY')
    PASSWORD = env_config.get("PASSWORD")
    PUBLIC_IP_ADDRESS = env_config.get("PUBLIC_IP_ADDRESS")
    DBNAME = env_config.get("DBNAME")
    PROJECT_ID = env_config.get("PROJECT_ID")
    INSTANCE_NAME = env_config.get("INSTANCE_NAME")

    engine = sqlalchemy.create_engine(
        f'mysql+mysqldb://root:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}?unix_socket=/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}'
    )

    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {'start': '1', 'limit': '20', 'convert': 'GBP'}
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': KEY,
    }

    session = Session()
    session.headers.update(headers)
    client = coinsentiment.setupclient(twitter_secret)
    # Get data from coinmarketcap api
    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        df = pd.json_normalize(data['data'])
        df = df[[
            'id',
            'name',
            'symbol',
            'slug',
            'num_market_pairs',
            'date_added',
            'cmc_rank',
            'last_updated',
            'quote.GBP.price',
            'quote.GBP.volume_24h',
            'quote.GBP.volume_change_24h',
            'quote.GBP.percent_change_1h',
            'quote.GBP.percent_change_24h'
        ]]
        
        print(df.columns)    
        df.columns = ['id','name','symbol','slug','num_market_pairs','date_added','cmc_rank','last_updated','quote_GBP_price','quote_GBP_volume_24h','quote_GBP_volume_change_24h','quote_GBP_percent_change_1h','quote_GBP_percent_change_24h']
        for idx, row in df.iterrows():
            try:
                starttime = datetime.datetime.now() - datetime.timedelta(hours = 2)
                clean_tweets = coinsentiment.searchtweets(client, starttime, row["symbol"])
                btc_tweets = coinsentiment.searchtweets(client, starttime, "BTC")
                sentiment = coinsentiment.getaveragesentiment(clean_tweets)
                popularity = coinsentiment.getpopularity(clean_tweets, btc_tweets)
        
                df.loc[idx, "sentiment"] = sentiment
                df.loc[idx, "popularity"] = popularity
            except:
                df.loc[idx, "sentiment"] = 0.0
                df.loc[idx, "popularity"] = 0.0
        
        df.to_sql(con=engine, name='coinmarket', if_exists='replace')
        
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)


if __name__ == '__main__':
    get_data()