import gpt_twitter_api
import tweeter_bot.twitter_api as twitter_api

tweet = gpt_twitter_api.make_tweet()

twitter_api.post(tweet)