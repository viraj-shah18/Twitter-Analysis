import pandas as pd
import plotly.express as px
from collections import OrderedDict, Counter
import pickle
import os
import sys
import datetime
import csv
import twint
import re
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import datetime

month_names = [
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


def get_codes():
    lang_codes = dict()
    with open("lang_codes.csv", mode="r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        next(csv_reader)
        for row in csv_reader:
            lang_codes[row[1]] = row[0]
    return lang_codes


def scrape(to_search="", rel_date=5):
    toda = datetime.date.today()
    fin = toda + datetime.timedelta(days=-rel_date)
    tweets_objects = []
    if to_search == "#ACL2020":
        to_search = "#acl2020nlp"
    c = twint.Config(
        Since=f"{fin.year}-{fin.month}-{fin.day}",
        Hide_output=True,
        Search=to_search,
        Store_object=True,
        Store_object_tweets_list=tweets_objects,
        Limit=10000
        # Store_csv = True,
        # Output = "data2"
    )

    twint.run.Search(c)
    return tweets_objects


def top_recent_tweets(df, all_info, info="tweets"):
    df["date2"] = df["date"].apply(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d"))
    delta = datetime.timedelta(days=-30)
    df["recent"] = df["date2"].apply(lambda x: x >= (datetime.datetime.now() + delta))
    recent_df = df.loc[df["recent"] == True]
    df2 = recent_df.nlargest(8, ["likes_count"])
    arr = df2["id"].to_list()
    all_info["recent_tweet_ids"] = arr

    df2 = recent_df.nlargest(12, ["retweets_count"])
    arr = df2["id"].to_list()
    final_arr = []
    top_rtweet_ = set(all_info["recent_tweet_ids"])
    for a in arr:
        if a not in top_rtweet_:
            final_arr.append(a)
    all_info["recent_retweet_ids"] = final_arr


def top_tweets(df, all_info):
    df2 = df.nlargest(8, ["likes_count"])
    arr = df2["id"].to_list()
    all_info["tweet_ids"] = arr


def top_retweets(df, all_info):
    df2 = df.nlargest(16, ["retweets_count"])
    arr = df2["id"].to_list()
    final_arr = []
    top_tweet_ = set(all_info["tweet_ids"])
    for a in arr:
        if a not in top_tweet_:
            final_arr.append(a)
    all_info["retweet_ids"] = final_arr


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


def get_stats(df, all_info):
    all_info["Twitter Activity"] = len(df.likes_count)
    all_info["Likes Counter"] = df.likes_count.sum()
    all_info["Retweets Counter"] = df.retweets_count.sum()


def plot_daily(df, all_info):
    df["day"] = df["date"].apply(
        lambda x: int(x.split("-")[2])
        if f"{month_names[int(x.split('-')[1]) - 1]}, {x.split('-')[0][-2:]}"
        == all_info["month_highest"]
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
        title_text=f"Daily tweet count for month with highest number of tweets ({all_info['month_highest']})",
        title_x=0.08,
    )
    li_ = list(day_data.keys())
    all_info["day_highest"] = li_[1] if li_[0] == -1 else li_[0]
    all_info["day_plot"] = fig


def plot_monthly(df, all_info):
    df["month"] = df["date"].apply(
        lambda x: f"{month_names[int(x.split('-')[1]) - 1]}, {x.split('-')[0][-2:]}"
    )
    month_data = df["month"].value_counts().to_dict()
    yr = datetime.date.today().year
    month_data2 = OrderedDict()

    for year in range(yr - 2, yr + 1):
        for month in month_names:
            key = f"{month}, {str(year)[-2:]}"
            if key not in month_data.keys():
                continue
            else:
                month_data2[key] = month_data[key]
    fig = px.bar(
        x=month_data2.keys(),
        y=month_data2.values(),
        labels={"x": "month", "y": "Activity"},
    )
    fig.update_layout(title_text="Number of Tweets over the year", title_x=0.28)
    all_info["month_highest"] = list(month_data.keys())[0]
    all_info["month_plot"] = fig


def lang_pie(df, all_info):
    lang_code = get_codes()
    lang_count = df["lang"].value_counts().to_dict()
    del lang_count["en"]
    try:
        del lang_count["und"]
    except:
        _ = 0
    x = []
    y = []
    for k, v in lang_count.items():
        if k not in lang_code.keys():
            x.append("unknown")
        else:
            x.append(lang_code[k])
        y.append(v)
    fig = px.pie(names=x, values=y)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        title_text="Languages (Except English) identified by twitter", title_x=0.15
    )
    all_info["lang_pie"] = fig


def remove_spam(uc2, all_info):
    to_remove = []
    for k, v in uc2.items():
        if v > (0.15 * all_info["Twitter Activity"]):
            to_remove.append(k)
    for key in to_remove:
        uc2.pop(key)
    return uc2


def count_users(df, all_info):
    user_count = df["username"].value_counts().to_dict()
    uc2 = OrderedDict(sorted(user_count.items(), key=lambda x: x[1], reverse=True)[:20])
    uc2 = remove_spam(uc2, all_info)
    fig = px.bar(
        x=uc2.keys(),
        y=uc2.values(),
        labels={"x": "Username", "y": "Total Number of Tweets"},
    )
    fig.update_layout(
        title_text="Maximum total tweets from a single username", title_x=0.15
    )
    all_info["count_users"] = fig


def get_xml(name):
    url = f"https://raw.githubusercontent.com/acl-org/acl-anthology/master/data/xml/{name}.xml"
    r = requests.get(url, stream=True, allow_redirects=True)
    if r.status_code != 200:
        return -1
    with open(f"./xml/{name}.xml", "wb") as f:
        f.write(r.content)


def parse_xml(paper):
    name = paper.split("-")[0]
    if not os.path.exists(f"./xml/{name}.xml"):
        rc = get_xml(name)
        if rc == -1:
            return

    with open(f"./xml/{name}.xml") as f:
        soup = BeautifulSoup(f, "lxml")

    tit = soup.find("url", text=paper).parent.title
    if tit is None:
        return None
    title = tit.text
    regex = r"<.*?>"
    result = re.sub(regex, "", title)
    return result


def get_title(all_info):
    for paper in all_info["top_papers"]:
        if paper == "":
            continue
        result = parse_xml(paper)
        if result:
            all_info["top_paper_names"].append(result)
    for _ in range(len(all_info["top_paper_names"]), 10):
        all_info["top_paper_names"].append("")


def capture_strings(lis, cnt, reward):
    pattern = re.compile(r"^https?://www\.aclweb\.org/anthology/(.*?)/?(\.pdf)?$")
    for link in lis:
        match = re.match(pattern, link)
        if match:
            cnt[match.group(1)] += 5 + reward


def get_paper(df, all_info):
    df["reward_count"] = (
        df["likes_count"] + df["replies_count"] * 3 + df["retweets_count"] * 2
    )

    cnt = Counter()
    for row in df.itertuples():
        capture_strings(row.urls, cnt, row.reward_count)

    all_info["top_papers"] = list()
    for item in cnt.most_common(10):
        if item[1] < 20:
            break
        else:
            all_info["top_papers"].append(item[0])

    for _ in range(len(all_info["top_papers"]), 10):
        all_info["top_papers"].append("")
    all_info["total_paper_mentions"] = len(cnt)
    all_info["top_paper_names"] = list()
    get_title(all_info)


def process_data(df, all_info):
    get_stats(df, all_info)
    print_top(df, "mentions", all_info)
    print_top(df, "hashtags", all_info)
    print_top(df, "urls", all_info)
    plot_monthly(df, all_info)
    plot_daily(df, all_info)
    top_tweets(df, all_info)
    top_recent_tweets(df, all_info)
    top_retweets(df, all_info)
    lang_pie(df, all_info)
    count_users(df, all_info)
    get_paper(df, all_info)


def clean_data(name, tweet_list, first_run=False):
    data_df = pd.DataFrame([t.__dict__ for t in tweet_list])
    if not (data_df.empty):

        data_df = data_df.rename(columns={"datestamp": "date", "timestamp": "time"})
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
                "geo",
                "near",
                "place",
                # "tweet",
            ]
        )
    if first_run:
        data_df.to_pickle(f"./data/{name}.pkl")
        return data_df

    with open(f"./data/{name}.pkl", "rb") as f:
        ori_df = pd.read_pickle(f)

    os.remove(f"./data/{name}.pkl")
    final_df = ori_df.append(data_df, ignore_index=True)
    final_df.drop_duplicates(
        inplace=True,
        subset=["id", "date", "time", "username", "name"],
        ignore_index=True,
    )
    final_df.to_pickle(f"./data/{name}.pkl")
    return final_df


def show_prev_tweets(name):
    if os.path.exists(f"./data/processed_{name}.pkl"):
        with open(f"./data/processed_{name}.pkl", "rb") as f:
            return pd.read_pickle(f)

    all_info = dict()
    all_info["name"] = name[1:]
    with open(f"./data/{name}.pkl", "rb") as f:
        data_df = pd.read_pickle(f)
    process_data(data_df, all_info)
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

def create_regex():
    with open("cfps.txt", "r") as f:
        possible_calls = f.readlines()

    for a in range(len(possible_calls)):
        if a!=len(possible_calls)-1:
            possible_calls[a] = possible_calls[a][:-1]
        possible_calls[a] = possible_calls[a] + "s?"
        possible_calls[a] = "[" + possible_calls[a][0] + possible_calls[a][0].lower()+"]" + possible_calls[a][1:]

    final = "[cC]all for (" + "|".join(possible_calls) + ")"
    return final

# ^https?://(www\.)*?aclweb\.org/anthology/(.*?)/?(\.pdf)?$|^https?://(www\.)*?arxiv\.org/abs/(.*)*?$