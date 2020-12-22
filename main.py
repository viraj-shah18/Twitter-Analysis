import os
import twint
import pandas as pd
import sys

def scrape(to_search=""):
    # Configure
    c = twint.Config()
    # c.Since("2019-12-31")
    # c.Until("2020-10-31")

    c.Search = to_search
    c.Output = "data"
    # c.Lang = "en"

    c.Limit = 10
    c.Store_csv = True

    twint.run.Search(c)


def clean_data():
    data_df = pd.read_csv("data/tweets.csv", header=0)
    data_df = data_df.drop(
        columns=[
            "conversation_id",
            "timezone",
            "cashtags",
            "photos",
            "video",
            "user_rt_id",
            "user_rt",
            "retweet_id",
            "reply_to",
            "retweet_date",
            "translate",
            "trans_src",
            "trans_dest",
            "thumbnail",
            "retweet",
            "quote_url",
            "source",
            "link",
            "user_id",
            "created_at"  # created at is just date + time (available seperately)
        ]
    )
    # print(data_df.keys())
    # # print("\n" + "-" * 125 + "\n")
    # print(data_df.head(2))
    # process_data(data_df)
    data_df.to_csv("./data/clean_data.csv")

if __name__ == "__main__":
    os.system("rm -rf data")
    args = sys.argv
    print(args)
    scrape(to_search = args[1])
    clean_data()
