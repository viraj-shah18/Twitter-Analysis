import os
import pickle
import sys
from collections import Counter, OrderedDict

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import twint


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
    )

    twint.run.Search(c)
    with open(f"./data/{to_search}.pkl", "wb") as out_file:
        df = twint.storage.panda.Tweets_df
        pickle.dump(df, out_file, pickle.HIGHEST_PROTOCOL)
    return tweets_objects


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
                # to_add = to_add.strip().replace("'", "")
            # elif col_name=="hashtags" or col_name=="urls":
            # to_add = elem.strip().replace("'", "")

            cnt[to_add] += 1
    all_info[f"unique {col_name}"] = len(cnt)
    all_info[f"top 10 {col_name}"] = cnt.most_common(10)
    # print(len(cnt))
    # print(cnt.most_common(10))


def print_stats(df):
    all_info["Twitter Activity"] = len(df.likes_count)
    all_info["Likes Counter"] = df.likes_count.sum()
    all_info["Retweets Counter"] = df.retweets_count.sum()
    # print(f"Likes Counter\t\t = {df.likes_count.sum()}")
    # print(f"Retweets Counter\t = {df.retweets_count.sum()}")


def show_out(all_info):
    app.layout = html.Div(
        children=[
            html.H1(
                children="Twitter Coverage of EMNLP 2020", style={"textAlign": "center"}
            ),
            html.Div(
                children=[
                    html.H5(
                        children = "Twitter Activity"
                    ),
                    html.H5(
                        children = "Likes Counter"
                    ),
                    html.H5(
                        children = "Retweets Counter"
                    ),
                    html.H5(
                        children = "Unique Mentions"
                    ),

                ],
                style={"columnCount": 4, "textAlign": "center"},
            ),
            html.Div(
                children=[
                    html.H6(
                        children = f"{all_info['Twitter Activity']}"
                    ),
                    html.H6(
                        children = f"{all_info['Likes Counter']}"
                    ),
                    html.H6(
                        children = f"{all_info['Retweets Counter']}"
                    ),
                    html.H6(
                        children = f"{all_info['unique mentions']}"
                    ),

                ],
                style={"columnCount": 4,"textAlign": "center"},
            ),
            html.Div(
                className = "row",
                children=[
                    html.H5(
                        children = "Top 10 Hashtags"
                    ),
                    html.H5(
                        children = "Top 10 mentions"
                    ),
                    html.H5(
                        children = "Top 10 URLs"
                    ),

                ],
                style={"columnCount": 3,"textAlign": "center", "margin-top":"50px"},
            ),
            html.Div(
                className = "row",
                children=[
                    html.P(
                        className = "top10",
                        children = [html.P(html.A(f"#{i[0]}", href = f"https://twitter.com/hashtag/{i[0]}?src=hashtag_click" )) for i in all_info['top 10 hashtags']],
                        ),
                    html.P(
                        className = "top10",
                        children  = [html.P(html.A(f"@{i[0]}", href = f"https://twitter.com/{i[0]}")) for i in all_info['top 10 mentions']]
                    ),
                    html.Div(
                        className = "top10",
                        children = [html.P(html.A(f"{i[0]}", href = f"{i[0]}")) for i in all_info['top 10 urls']]
                        )
                ],
                style={"columnCount": 3,"textAlign": "center", "rowCount": 10},
            ),
            html.Div([
                html.Div(
                    dcc.Graph(id="example-graph", figure=all_info["month_plot"]),
                ),
                html.Div(
                    dcc.Graph(id="example-graph2", figure=all_info["month_plot"]),
                )
            ],
            style={"columnCount": 2, "margin-top":"30px"},
            )

        ]
    )


def plot_monthly(df):
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
    )
    all_info["month_plot"] = fig
    # fig.show()


def process_data(df):
    print_stats(df)
    print_top(df, "mentions")
    print_top(df, "hashtags")
    print_top(df, "urls")
    plot_monthly(df)


def clean_data(tweet_list=None):
    if tweet_list is None:
        data_df = pd.read_csv("data/tweets.csv", header=0)
        data_df = data_df.drop(columns=["created_at"])
    else:
        # data_df = pd.DataFrame.from_records([to_dict(s) for s in tweet_list])
        data_df = pd.DataFrame([t.__dict__ for t in tweet_list])
        data_df = data_df.drop(columns=["datetime", "user_id_str", "id_str"])
        data_df = data_df.rename(
            columns={"datestamp": "date", "timestamp": "time"}, errors="raise"
        )

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
    # print(data_df.head(2))
    process_data(data_df)
    # data_df.to_csv("./data/clean_data.csv")
    with open("./data/clean.pkl", "wb") as f:
        pickle.dump(data_df, f)


all_info = dict()
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


if __name__ == "__main__":
    # os.system("rm -rf data")
    if not os.path.exists("./data"):
        os.system("mkdir data")
    # args = sys.argv
    # all_tweets = scrape(to_search=args[1])
    # clean_data(all_tweets)
    # print(all_info)
    df = pd.read_pickle("./data/clean.pkl")
    process_data(df)
    show_out(all_info)
    app.run_server(debug=True, host="0.0.0.0")
