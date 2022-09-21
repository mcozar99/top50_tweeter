import pandas as pd
import tweepy
from keys import consumer_key_public, consumer_key_private, access_token_public, access_token_private
import time
import random
from datetime import datetime

def login():
    auth = tweepy.OAuth1UserHandler(consumer_key_public, consumer_key_private, access_token_public, access_token_private)
    api = tweepy.API(auth)
    return api

def tweet_something(text, api, media=None):
   """
   Given a text it tweets it
   :param text: text to tweet
   :param api: tweepy object
   :param media: if pictures are needed, pass a list
   :return: tweet object
   """
   if media == None:
       return api.update_status(text)
   else:
       ids = []
       for item in media:
            ids.append(api.media_upload(item).media_id)
       return api.update_status(status=text, media_ids=ids)

def thread(tweet, text, api, media = None):
    """
    Given a thread, it tweets making a thread
    :param tweet: tweet to thread
    :param text: text of the tweet
    :param api: tweepy object
    :return: tweet published
    """
    if media == None:
        thread_tweet = api.update_status(status=text,
                                         in_reply_to_status_id=tweet.id,
                                         auto_populate_reply_metadata=True)
    else:
        ids = []
        for item in media:
            ids.append(api.media_upload(item).media_id)
        thread_tweet = api.update_status(status=text,
                                         in_reply_to_status_id=tweet.id,
                                         media_ids=ids,
                                         auto_populate_reply_metadata=True)
    return thread_tweet

def search_users(query, api):
    """Devuelve tan solo un resultado"""
    return api.search_users(query)[0]

def get_account_followers(screen_name, page, api):
    """
    Gets a list of users of some account
    """
    return api.get_follower_ids(screen_name=screen_name, cursor=page)

def follow(user_id, api):
    """follows someone on twitter"""
    return api.create_friendship(user_id=user_id)

def get_followers_of_account(username, max_number, api):
    ids = []
    for page in tweepy.Cursor(api.get_follower_ids, screen_name=username).pages():
        ids.extend(page)
        time.sleep(60)
        if len(ids) > max_number:
            break
    return ids

def automatic_follows(number_of_follows, api, path='data/users.csv'):
    """
    Given a path to a csv of user ids, it selects interesting follows according to the profile activity and discards other accounts,
    we can only follow 400 people per day, but it does it porportionally
    - Condiciones: creado hace al menos 2 meses, mas de 50 followers y mas de 50 seguidos, actividad hace al menos una semana
    """
    i = 0
    user_list = pd.read_csv(path).id.to_list()
    sleep_time_user = 1
    sleep_time_follow = 15
    valid_users = pd.read_csv('data/valid_users.csv')
    while i < number_of_follows:
        id = random.choice(user_list)
        try:
            user = api.get_user(user_id=id)
            time.sleep(sleep_time_user)
            try:
                if user.followers_count > 10 and user.friends_count > 60 \
                        and time.time() - datetime.timestamp(user.status.created_at) < 60*60*24*2:#7 \
                        #and time.time() - datetime.timestamp(user.created_at) < 60*60*24*7*4*2:
                    print('User %s is a valid follow'%user.screen_name)
                    follow(id, api)
                    time.sleep(sleep_time_follow)
                    sleep_time_user = 0
                    valid_users.loc[len(valid_users), :] = [id]
                    user_list.remove(id)
                    i+=1
                else:
                    sleep_time_user = 1
                    user_list.remove(id)
                    print('User %s discarded'%user.screen_name)
            except:
                continue
            if len(user_list) == 0:
                break
        except Exception as e:
            print('ERROR')
            print(str(e))
            print('Sleeping 1 minute')
            time.sleep(60)
            continue
        valid_users.to_csv('data/valid_users.csv', index = False)
        df = pd.DataFrame({'id': user_list})
        df.to_csv(path, index = False)