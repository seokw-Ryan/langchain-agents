import gpt_twitter_api
import twitter_api

tweet = gpt_twitter_api.make_tweet()

twitter_api.post(tweet)