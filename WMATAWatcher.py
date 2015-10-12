import os
import json
from requests_oauthlib import OAuth1
import requests
import datetime
import re
import pandas as pd

# Get Twitter keys from environment variables (pls)

CONSUMER_KEY = os.environ['TWITTER_CONSUMER_KEY']
CONSUMER_SECRET = os.environ['TWITTER_CONSUMER_SECRET']
OAUTH_TOKEN = os.environ['TWITTER_OAUTH_TOKEN']
OAUTH_TOKEN_SECRET = os.environ['TWITTER_OAUTH_TOKEN_SECRET']

auth = OAuth1(CONSUMER_KEY,
              CONSUMER_SECRET,
              OAUTH_TOKEN,
              OAUTH_TOKEN_SECRET)

searches = {
            'h_wmata': {'q': '%23wmata', 'result_type': 'recent',
                        'count': '100'},
            'a_wmata': {'q': '%40wmata', 'result_type': 'recent',
                        'count': '100'},
            'h_unsuckdcmetro': {'q': '%23unsuckdcmetro',
                                'result_type': 'recent', 'count': '100'},
            'a_unsuckdcmetro': {'q': '%40unsuckdcmetro',
                                'result_type': 'recent', 'count': '100'},
            'a_fixwmata': {'q': '%40fixwmata', 'result_type': 'recent',
                           'count': '100'},
            'a_dcmetrosucks': {'q': '%40dcmetrosucks',
                               'result_type': 'recent', 'count': '100'},
            'a_metrorage': {'q': '%40metrorage', 'result_type': 'recent',
                            'count': '100'},
            'a_overhaulmetro': {'q': '%40overhaulmetro',
                                'result_type': 'recent', 'count': '100'},
            'h_metrorailinfo': {'q': '%23metrorailinfo',
                                'result_type': 'recent', 'count': '100'},
            'a_metrorailinfo': {'q': '%40metrorailinfo',
                                'result_type': 'recent', 'count': '100'},
            'h_metrofailinfo': {'q': '%23metrofailinfo',
                                'result_type': 'recent', 'count': '100'},
            'a_metrofailinfo': {'q': '%40metrofailinfo',
                                'result_type': 'recent', 'count': '100'},
            'a_drgridlock': {'q': '%40drgridlock', 'result_type': 'recent',
                             'count': '100'}}


def make_first_request(request_info):
    url_base = 'https://api.twitter.com/1.1/search/tweets.json'
    r = requests.get(url_base, auth=auth, params=request_info)
    tweets = json.loads(r.text)
    return tweets


def make_url_request(request_url):
    r = requests.get(request_url, auth=auth)
    tweets = json.loads(r.text)
    return tweets


def flattenDict(d, result=None):
    # Code courtesy https://gist.github.com/higarmi/6708779
    # I wish I was better at recursion D:
    if result is None:
        result = {}
    for key in d:
        value = d[key]
        if isinstance(value, dict):
            value1 = {}
            for keyIn in value:
                value1[".".join([key, keyIn])] = value[keyIn]
            flattenDict(value1, result)
        elif isinstance(value, (list, tuple)):
            for indexB, element in enumerate(value):
                if isinstance(element, dict):
                    value1 = {}
                    index = 0
                    for keyIn in element:
                        #  newkey = ".".join([key, keyIn])
                        value1[".".join([key, keyIn])] = value[indexB][keyIn]
                        index += 1
                    for keyA in value1:
                        flattenDict(value1, result)
        else:
            result[key] = value
    return result


def find_oldest_tweet(tweets):
    num_tweets = len(tweets['statuses'])
    if num_tweets == 0:
        return pd.Timestamp('1901-01-01 00:00:00').tz_localize('US/Eastern')
    else:
        oldest_tweet = tweets['statuses'][len(tweets['statuses']) - 1]['created_at']
        return pd.Timestamp(oldest_tweet).tz_convert('US/Eastern')


def tweets_by_category(tweet):
    # remove usernames, hyperlinks, numbers, etc.
    # tweets = re.sub('[@][A-Za-z0-9]+','', tweets)
    tweet = re.sub('http://[A-Za-z\.\/0-9]+', '', tweet)
    tweet = re.sub('https://[A-Za-z\.\/0-9]+', '', tweet)
    tweet = re.sub('[0-9]+', '', tweet)
    tweet = tweet.replace('\'', '')
    words = tweet.lower().split()
    delay_words = ['delay', 'delays', 'residual', 'tracking', 'single',
                   'minute', 'minutes']
    line_words = ['red', 'orange', 'blue', 'silver', 'yellow', 'green',
                  'line', 'station', 'train']
#    angry_twits_words = ['RT', '@wmata', '@unsuckdcmetro', '@metrorailinfo',
#                         '@metrofailinfo', '@fixwmata', '@dcmetrosucks',
#                         '@fixmetro', '@drgridlock', '#wmata',
#                         '#unsuckdcmetro', '#fixwmata']
    ok_words = ['normal', 'resume', 'resuming']
#    irrelevant_wmata_words = ['bus', 'route']
    delay_related_tweets = 0
    line_related_tweets = 0
#    angry_twits_related_tweets = 0
    ok_related_tweets = 0
#    irrelevant_wmata_tweets = 0
    if any(word in delay_words for word in words):
        delay_related_tweets += 1
    if any(word in line_words for word in words):
        line_related_tweets += 1
#    if any(word in angry_twits_words for word in words):
#        angry_twits_related_tweets += 1
    if any(word in ok_words for word in words):
        ok_related_tweets += 1
#    if any(word in irrelevant_wmata_words for word in words):
#        irrelevant_wmata_tweets += 1
    return [delay_related_tweets, line_related_tweets,
            ok_related_tweets]


def tweets_by_category2(tweet):
    # remove usernames, hyperlinks, numbers, etc.
    # tweets = re.sub('[@][A-Za-z0-9]+','', tweets)
    tweet = re.sub('http://[A-Za-z\.\/0-9]+','', tweet)
    tweet = re.sub('https://[A-Za-z\.\/0-9]+','', tweet)
    tweet = re.sub('[0-9]+', '', tweet)
    tweet = tweet.replace('\'','')                                                       
    words = tweet.lower().split()
    numwords = len(words)
    # define tallies - words related to delays, words related to metro stations or lines, and words related to
    # people tweeting to the various complaint clearinghouses.
    delay_words = ['delay','delays','residual','tracking','single', 'minute', 'minutes', 'min', 'mins', 'midday', 'mid-day', 'wait', 'waiting', 'service']
    line_words = ['red','orange','blue','silver','yellow','green','line','station','train', 'RL', 'OL', 'BL', 'SL', 'YL', 'GL']
    angry_twits_words = ['RT','@wmata','@unsuckdcmetro','@metrorailinfo', '@metrofailinfo', '@fixwmata', '@dcmetrosucks','@fixmetro', '@drgridlock', '#wmata', '#unsuckdcmetro', '#fixwmata']
    ok_words = ['normal', 'resume', 'resuming']
    irrelevant_wmata_words = ['bus', 'route']
    num_delay_words = 0
    num_line_words = 0
    num_ok_words = 0
    for word in words:
        if word in delay_words:
            num_delay_words +=1
        elif word in line_words:
            num_line_words += 1
        elif word in ok_words:
            num_ok_words +=1
    if numwords == 0:
        return [0, 0, 0]
    else:
        return [float(num_delay_words)/numwords, float(num_line_words)/numwords, float(num_ok_words)/numwords]


def categorizeTweets(tS):
    catSums = {'delay': 0, 'line': 0, 'ok': 0}
    wordFracs = {'delay': 0, 'line': 0, 'ok': 0}
    for tweet in tS['text']:
        tweetSum = tweets_by_category(tweet)
        catSums['delay'] += tweetSum[0]
        catSums['line'] += tweetSum[1]
#        catSums['twit'] += tweetSum[2]
        catSums['ok'] += tweetSum[2]
#        catSums['irrel'] += tweetSum[4]
        wordFrac = tweets_by_category2(tweet)
        wordFracs['delay'] = wordFrac[0]
        wordFracs['line'] = wordFrac[1]
        wordFracs['ok'] = wordFrac[2]
    return catSums, wordFracs


def recent_tweet_search(now, timespan):
    search_time = now
    all_search_results = []
    url_base = 'https://api.twitter.com/1.1/search/tweets.json'
    for search_term in searches:
        search_results = make_first_request(searches[search_term])
        if len(search_results) == 0:
            pass
        elif 'errors' in search_results.keys():
            pass
        elif len(search_results['statuses']) == 0:
            pass
        elif 'next_results' not in search_results['search_metadata'].keys():
            all_search_results.append(search_results['statuses'])
            pass
        else:
            all_search_results.append(search_results['statuses'])
            while (search_time < find_oldest_tweet(search_results) + pd.DateOffset(minutes = timespan)):
                next_search_url = search_results['search_metadata']['next_results']
                search_results = make_url_request(url_base + next_search_url)
                all_search_results.append(search_results['statuses'])
    return all_search_results


def get_test_variables(tweet_df):
    if len(tweet_df) == 0:
        timestamp = pd.Timestamp(datetime.datetime.now()).tz_localize('US/Eastern')
        hour = timestamp.hour
        dayofweek = timestamp.dayofweek
        month = timestamp.month
        weekofyr = timestamp.weekofyear
        return [0, 0, 0, 0, 0, 0, 0, hour, dayofweek, month, weekofyr]
    else:
        hour = tweet_df.index.hour[-1]
        dayofweek = tweet_df.index.dayofweek[-1]
        month = tweet_df.index.month[-1]
        weekofyr = tweet_df.index.weekofyear[-1]
        numTweets = (len(tweet_df))
        categoryTweetHolder, wordFracHolder = categorizeTweets(tweet_df)
        numDelayTweets = (categoryTweetHolder['delay'])
        numLineTweets = (categoryTweetHolder['line'])
#        numTwitTweets = (categoryTweetHolder['twit'])
        numOKTweets = (categoryTweetHolder['ok'])
#        numIrrelTweets = (categoryTweetHolder['irrel'])
        fracDelayWords = (wordFracHolder['delay'])
        fracLineWords = (wordFracHolder['line'])
        fracOKWords = (wordFracHolder['ok'])
        totalTopicalTweets = float(numDelayTweets + numLineTweets +
                                   numOKTweets)
        if totalTopicalTweets == 0:
            return [0, 0, 0, 0, 0, 0, 0, hour, dayofweek, month, weekofyr]
        else:
            fracDelayTweets = float(numDelayTweets) / totalTopicalTweets
            fracLineTweets = float(numLineTweets) / totalTopicalTweets
    #        fracTwitTweets = float(numTwitTweets) / totalTopicalTweets
            fracOKTweets = float(numOKTweets) / totalTopicalTweets
#            fracIrrelTweets = float(numIrrelTweets) / totalTopicalTweets
            return [fracDelayWords, fracDelayTweets, fracLineTweets, fracOKTweets,
                    fracLineWords, fracOKWords, numTweets, hour, dayofweek, month, weekofyr]


def process_raw_tweets(raw_tweets, firsttime, lasttime):
    td_flat_list = []
    for td in raw_tweets:
        for t in td:
            td_flat_list.append(flattenDict(t))
    td_df = pd.DataFrame(td_flat_list)
    td_df = td_df[['id', 'created_at', 'text']]
    timestamp = td_df['created_at'].values
    ts = [pd.Timestamp(t).tz_convert('US/Eastern') for t in timestamp]
    td_df.index = ts
    td_df = td_df.drop_duplicates(subset='id')
    td_df = td_df.sort('id')
    td_df = td_df[str(firsttime):str(lasttime)]
    return td_df


def produce_test_data():
    t2 = pd.Timestamp(datetime.datetime.now()).tz_localize('US/Eastern')
    t1 = t2 - pd.DateOffset(minutes=2)
    tweets = recent_tweet_search(t2, 2)
    tweet_df = process_raw_tweets(tweets, t1, t2)
    x_test = get_test_variables(tweet_df)
    ts1dt = t1.to_datetime()
    ts2dt = t2.to_datetime()
    if (ts2dt.day != ts1dt.day):
        timestring = ts1dt.strftime("%a %b %d %I:%M %p") + ' - ' + ts2dt.strftime("%a %b %d %I:%M %p")
    else:
        timestring = ts1dt.strftime("%a %b %d %I:%M %p") + ' - ' + ts2dt.strftime("%I:%M %p")
    return timestring, x_test

def debug():
    t2 = pd.Timestamp(datetime.datetime.now()).tz_localize('US/Eastern')
    t1 = t2 - pd.DateOffset(minutes=2)
    derp = recent_tweet_search(t2, 2)
    tweet_df = process_raw_tweets(derp, t1, t2)
    x_test = get_test_variables(tweet_df)
    ts1dt = t1.to_datetime()
    ts2dt = t2.to_datetime()
    if (ts2dt.day != ts1dt.day):
        timestring = ts1dt.strftime("%a %b %d %I:%M %p") + ' - ' + ts2dt.strftime("%a %b %d %I:%M %p")
    else:
        timestring = ts1dt.strftime("%a %b %d %I:%M %p") + ' - ' + ts2dt.strftime("%I:%M %p")
    return timestring, x_test
