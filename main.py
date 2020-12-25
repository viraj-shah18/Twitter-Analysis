import os
import pickle
import sys
from collections import Counter, OrderedDict
import urllib

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px

try:
    import twint
except ModuleNotFoundError:
    os.system(
        "pip3 install --upgrade git+https://github.com/twintproject/twint.git@origin/master#egg=twint"
    )
    import twint


def scrape(to_search=""):
    tweets_objects = []
    c = twint.Config(
        Since="2020-01-01",
        Hide_output=True,
        Search=to_search,
        Store_object=True,
        Store_object_tweets_list=tweets_objects,
    )

    twint.run.Search(c)
    with open(f"./data/{to_search}.pkl", "wb") as out_file:
        df = twint.storage.panda.Tweets_df
        pickle.dump(df, out_file, pickle.HIGHEST_PROTOCOL)
    return tweets_objects


def top_tweets(df):
    df2 = df.nlargest(8, ["likes_count"])
    arr = df2["id"].to_list()
    all_info["tweet_ids"] = arr


def print_top(data_df, col_name):
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


def print_stats(df):
    all_info["Twitter Activity"] = len(df.likes_count)
    all_info["Likes Counter"] = df.likes_count.sum()
    all_info["Retweets Counter"] = df.retweets_count.sum()


def encoder(url):
    url = url.replace("'/g", "%27").replace('"/g', "%22")
    return urllib.parse.quote(url.encode("utf-8"))


def show_out(all_info):
    app.layout = html.Div(
        children=[
            html.H1(
                children="Twitter Coverage of EMNLP 2020", style={"textAlign": "center"}
            ),
            html.Div(
                children=[
                    html.H5(children="Twitter Activity"),
                    html.H5(children="Likes Counter"),
                    html.H5(children="Retweets Counter"),
                    html.H5(children="Unique Mentions"),
                ],
                style={"columnCount": 4, "textAlign": "center"},
            ),
            html.Div(
                children=[
                    html.H6(children=f"{all_info['Twitter Activity']}"),
                    html.H6(children=f"{all_info['Likes Counter']}"),
                    html.H6(children=f"{all_info['Retweets Counter']}"),
                    html.H6(children=f"{all_info['unique mentions']}"),
                ],
                style={"columnCount": 4, "textAlign": "center"},
            ),
            html.Div(
                className="row",
                children=[
                    html.H5(children="Top 10 Hashtags"),
                    html.H5(children="Top 10 mentions"),
                    html.H5(children="Top 10 URLs"),
                ],
                style={"columnCount": 3, "textAlign": "center", "margin-top": "50px"},
            ),
            html.Div(
                className="row",
                children=[
                    html.P(
                        className="top10",
                        children=[
                            html.P(
                                html.A(
                                    f"#{i[0]}",
                                    href=f"https://twitter.com/hashtag/{i[0]}?src=hashtag_click",
                                )
                            )
                            for i in all_info["top 10 hashtags"]
                        ],
                    ),
                    html.P(
                        className="top10",
                        children=[
                            html.P(
                                html.A(f"@{i[0]}", href=f"https://twitter.com/{i[0]}")
                            )
                            for i in all_info["top 10 mentions"]
                        ],
                    ),
                    html.Div(
                        className="top10",
                        children=[
                            html.P(html.A(f"{i[0]}", href=f"{i[0]}"))
                            for i in all_info["top 10 urls"]
                        ],
                    ),
                ],
                style={"columnCount": 3, "textAlign": "center", "rowCount": 10},
            ),
            html.Div(
                [
                    html.Div(
                        dcc.Graph(id="graph", figure=all_info["month_plot"]),
                    ),
                    html.Div(
                        dcc.Graph(id="graph2", figure=all_info["day_plot"]),
                    ),
                ],
                style={"columnCount": 2, "margin-top": "30px"},
            ),
            html.Div(
                style={"rowCount":2},
                children = [html.Div(
                    className="twitter-tweet twitter-tweet-rendered",
                    children=[
                        # html.Iframe(src = f"{encoder('https://twitter.com/anyuser/status/')}{all_info['tweet_ids'][i]}", height = "400px") for i in range(8)
                        html.Iframe(
                            style={
                                "position": "static",
                                "visibility": "visible",
                                "display": "block",
                                "flex-grow": 1,
                                "scrolling": "no",
                                "border": 0,
                                "frame": "false",
                                "hideCard":False,
                                "margin-left":"15px",
                            },
                            src = f"https://platform.twitter.com/embed/index.html?dnt=false&embedId=twitter-widget-0&frame=false&hideCard=false&hideThread=false&id={all_info['tweet_ids'][i]}&theme=light",
                            lang="en",
                            width="550px",
                            height="550px",
                        )
                        for i in range(4)
                    ],
                    style={
                        "display": "flex",
                        "max-width": "550px",
                        "width": "100%",
                        "margin-top": "10px",
                        "margin-bottom": "10px",
                    },
                ),
                    html.Div(
                        className="twitter-tweet twitter-tweet-rendered",
                        children=[
                            html.Iframe(
                                style={
                                    "position": "static",
                                    "visibility": "visible",
                                    "display": "block",
                                    "flex-grow": 1,
                                    "scrolling": "no",
                                    "border": 0,
                                    "frame": False,
                                    "width": "100%",
                                    "margin-left":"15px",
                                },
                                src = f"https://platform.twitter.com/embed/index.html?dnt=false&embedId=twitter-widget-0&frame=false&hideCard=false&hideThread=false&id={all_info['tweet_ids'][i]}&theme=light",
                                lang="en",
                                width="550px",
                                height="550px",
                            )
                            for i in range(4,8)
                        ],
                        style={
                            "display": "flex",
                            "max-width": "550px",
                            "max-height": "750px",
                            "margin-top": "10px",
                            "margin-bottom": "10px",
                        },
                    ),
                ],
            ),
        ]
    )


def plot_daily(df):
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
        title="Twitter Activity in the month of conference",
    )
    li_ = list(day_data.keys())
    all_info["day_highest"] = li_[1] if li_[0] == -1 else li_[0]
    all_info["day_plot"] = fig


def plot_monthly(df):
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
        title="Twitter Activity in this year",
    )
    all_info["month_highest"] = names.index(list(month_data.keys())[0]) + 1
    all_info["month_plot"] = fig


def process_data(df):
    print_stats(df)
    print_top(df, "mentions")
    print_top(df, "hashtags")
    print_top(df, "urls")
    plot_monthly(df)
    plot_daily(df)
    top_tweets(df)


def clean_data(name, tweet_list=None):
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
    process_data(data_df)
    with open(f"./data/clean_{name}.pkl", "wb") as f:
        pickle.dump(data_df, f)


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

if __name__ == "__main__":
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
    if not os.path.exists("./data"):
        os.system("mkdir data")
    args = sys.argv
    if len(args) == 1:
        args.append("#EMNLP2020")
    if not os.path.exists(f"./data/clean_{args[1]}.pkl"):
        all_tweets = scrape(to_search=args[1])
        clean_data(args[1], all_tweets)
    else:
        df = pd.read_pickle(f"./data/clean_{args[1]}.pkl")
        process_data(df)
    show_out(all_info)
    app.run_server(host="0.0.0.0")
