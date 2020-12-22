import os
import sys

import pandas as pd
import twint


def to_dict(tweet_object):
    return {
        "id": tweet_object.id,
        # "date": tweet_object.date,
        "time": tweet_object.time,
        "username":tweet_object.username,
        "name": tweet_object.name,
        "place": tweet_object.place,
        "tweet": tweet_object.tweet,
        "language": tweet_object.language,
        "mentions": tweet_object.mentions,
        "urls": tweet_object.urls,
        "replies_count": tweet_object.replies_count,
        "retweets_count": tweet_object.retweets_count, 
        "likes_count": tweet_object.likes_count,
        "hashtags": tweet_object.hashtags,
        "near": tweet_object.near,
        "geo": tweet_object.geo,
    }


def scrape(to_search=""):
    tweets_objects = []
    c = twint.Config(
        Since="2020-01-01",
        Hide_output=True,
        Search=to_search,
        Store_object=True,
        Store_object_tweets_list=tweets_objects,
        # Limit=10,
        # Store_csv = True,
        # Output = "data"
    )

    twint.run.Search(c)
    # print(all_tweets[0].id)
    return tweets_objects


def process_data(df):
    df["month"] = df["date"].apply(lambda x: x.split("-")[1])
    print(df["month"].value_counts())


def clean_data(tweet_list=None):
    if tweet_list is None:
        data_df = pd.read_csv("data/tweets.csv", header=0)
        data_df = data_df.drop(columns = ["created_at"])
    else:
        # data_df = pd.DataFrame.from_records([to_dict(s) for s in tweet_list])
        data_df = pd.DataFrame([t.__dict__ for t in tweet_list])
        data_df = data_df.drop(columns = ["datetime", "user_id_str", "id_str"])
        data_df = data_df.rename(columns={"datestamp":"date", "timestamp": "time"}, errors="raise")

        # variables = tweet_list[0].keys()
        # df = pd.DataFrame([[getattr(i,j) for j in variables] for i in tweet_list], columns = variables)
        # data_df = pd.DataFrame(tweet_list)
        # print(data_df.head(2))
        # return

    data_df = data_df.drop(
        columns=[
            "conversation_id",
            "user_id",
            "timezone", 
            "reply_to",
            "photos",
            "video",
            "thumbnail",
            "cashtags",
            "link",
            "retweet",
            "retweet_id",
            "retweet_date",
            "user_rt",
            "user_rt_id",
            "quote_url",
            "source",
            "translate",
            "trans_src",
            "trans_dest",
            # "created_at",  # created at is just date + time (available seperately)
        ]
    )
    print(data_df.head(2))
    process_data(data_df)
    data_df.to_csv("./data/clean_data.csv")


if __name__ == "__main__":
    os.system("rm -rf data")
    args = sys.argv
    all_tweets = scrape(to_search=args[1])
    clean_data(all_tweets)
