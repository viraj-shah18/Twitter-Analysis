import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import plotly.express as px
import datetime


def create_divs(deadline, tweet, side):
    # deadline = row["duedate"]
    # tweet = row["tweet"]
    deadline_str = deadline.strftime("%d %B, %Y") 
    content = html.Div(
        className=f"container {side}",
        children=[
            html.Div(
                className="content",
                children=[
                    html.Center(
                        children=[html.H2(deadline_str)]
                    ),
                    html.P(tweet)
                ]
            )
        ]
    )
    return content
    
    
    
    # html.Div(
    #     className="twitter-tweet twitter-tweet-rendered",
    #     children=[
    #         html.Iframe(
    #             style={
    #                 "position": "static",
    #                 "visibility": "visible",
    #                 "display": "block",
    #                 "flex-grow": 1,
    #                 "scrolling": "no",
    #                 "border": 0,
    #                 "frame": "false",
    #                 "margin-left": "15px",
    #             },
    #             src=f"https://platform.twitter.com/embed/index.html?dnt=false&embedId=twitter-widget-0&frame=false&hideCard=false&hideThread=false&id={id_cfps[i]}&theme=light",
    #             lang="en",
    #             width="550px",
    #             height="550px",
    #         )
    #         for i in range(start, min(end, len(id_cfps)))
    #     ],
    #     style={
    #         "display": "flex",
    #         "max-width": "550px",
    #         "width": "100%",
    #         "margin-top": "10px",
    #         "margin-bottom": "10px",
    #     },
    # )


def cfp_page():
    with open("./data/curate_cfps.pkl", "rb") as f:
        cfps = pd.read_pickle(f)
    with_date = cfps[cfps["duedate"]!=0]
    with_date.sort_values(by=["duedate"], ascending=False)
    due_dates = with_date["duedate"].to_list()
    tweets_date = with_date["tweet"].to_list()

    without_date = cfps[cfps["duedate"]==0]
    child = []
    len1 = len(with_date.index)
    len2 = len(without_date.index)

    for tweet_no in range(len1):
        if tweet_no%2==0:
            child.append(create_divs(due_dates[tweet_no], tweets_date[tweet_no], "left"))
        else:
            child.append(create_divs(due_dates[tweet_no], tweets_date[tweet_no], "right"))
        
    return html.Div(children=child,className="timeline")
