import pandas as pd
import plotly.express as px
from collections import OrderedDict, Counter
import pickle
import os
import sys
import datetime
try:
    import twint
finally:
    os.system(
        "pip3 install --upgrade git+https://github.com/twintproject/twint.git@origin/master#egg=twint"
    )
    import twint


all_info = dict()
names = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "June",
        "July",
        "Aug",
        "Sept",
        "Oct",
        "Nov",
        "Dec",
    ]

def scrape(to_search="", rel_date = 150):
    toda = datetime.date.today()
    fin = toda + datetime.timedelta(days=-rel_date)
    tweets_objects = []
    c = twint.Config(
        Since=f"{fin.year}-{fin.month}-{fin.day}",
        Hide_output=True,
        Search=to_search,
        Store_object=True,
        Store_object_tweets_list=tweets_objects,
        Store_csv = True,
        Output = "data2"
    )

    twint.run.Search(c)
    return tweets_objects



def top_tweets(df, all_info):
    df2 = df.nlargest(8, ["likes_count"])
    arr = df2["id"].to_list()
    all_info["tweet_ids"] = arr
    return all_info


def print_top(data_df, col_name, all_info):
    df = data_df[col_name]
    all_ = df.to_list()
    cnt = Counter()
    for lis_ in all_:
        if len(lis_) == 0:
            continue
        for elem in lis_:
            to_add = elem
            if col_name == "mentions":
                to_add = elem["screen_name"]

            cnt[to_add] += 1
    all_info[f"unique {col_name}"] = len(cnt)
    all_info[f"top 10 {col_name}"] = cnt.most_common(10)
    while len(all_info[f"top 10 {col_name}"]) < 10:
        all_info[f"top 10 {col_name}"].append(("", 0))
    return all_info


def get_stats(df, all_info):
    all_info["Twitter Activity"] = len(df.likes_count)
    all_info["Likes Counter"] = df.likes_count.sum()
    all_info["Retweets Counter"] = df.retweets_count.sum()
    return all_info


def plot_daily(df, all_info):
    df["day"] = df["date"].apply(
        lambda x: int(x.split("-")[2])
        if int(x.split("-")[1]) == all_info["month_highest"]
        else -1
    )
    day_data = df["day"].value_counts().to_dict()
    day_data2 = OrderedDict()
    for key in range(1, 32):
        if key not in day_data.keys():
            continue
        else:
            day_data2[key] = day_data[key]
    fig = px.bar(
        x=day_data2.keys(),
        y=day_data2.values(),
        labels={"x": "day", "y": "Activity"},
    )
    fig.update_layout(
        title_text="Number of tweets during conference month", title_x=0.2
    )
    li_ = list(day_data.keys())
    all_info["day_highest"] = li_[1] if li_[0] == -1 else li_[0]
    all_info["day_plot"] = fig
    return all_info


def plot_monthly(df, all_info):
    df["month"] = df["date"].apply(lambda x: names[int(x.split("-")[1]) - 1])
    month_data = df["month"].value_counts().to_dict()
    month_data2 = OrderedDict()
    for key in names:
        if key not in month_data.keys():
            continue
        else:
            month_data2[key] = month_data[key]
    fig = px.bar(
        x=month_data2.keys(),
        y=month_data2.values(),
        labels={"x": "month", "y": "Activity"},
        # title="Twitter Activity in this year",
    )
    fig.update_layout(title_text="Number of Tweets over the year", title_x=0.28)
    all_info["month_highest"] = names.index(list(month_data.keys())[0]) + 1
    all_info["month_plot"] = fig
    return all_info


def process_data(df, all_info):
    all_info = get_stats(df, all_info)
    all_info = print_top(df, "mentions", all_info)
    all_info = print_top(df, "hashtags", all_info)
    all_info = print_top(df, "urls", all_info)
    all_info = plot_monthly(df, all_info)
    all_info = plot_daily(df, all_info)
    all_info = top_tweets(df, all_info)
    return all_info


def clean_data(name, tweet_list, all_info):
    data_df = pd.DataFrame([t.__dict__ for t in tweet_list])
    data_df = data_df.rename(
        columns={"datestamp": "date", "timestamp": "time"}, errors="raise"
    )
    data_df = data_df.drop(
        columns=[
            "conversation_id",
            "datetime",
            "user_id_str",
            "id_str",
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
        ]
    )
    all_info = process_data(data_df, all_info)
    with open(f"./data/clean_{name}.pkl", "wb") as f:
        pickle.dump(data_df, f)
    return all_info

def add_comas(num):
    ans = ""
    pl = 0
    for a in reversed(str(num)):
        if pl == 3:
            ans += ","
        elif pl > 3 and (pl - 3) % 2 == 0:
            ans += ","
        ans += a
        pl += 1
    return ans[::-1]


def run_all(name, all_info):
    all_tweets = scrape(to_search=name, rel_date = 10)
    all_info = clean_data(name, all_tweets, all_info)
    return all_info