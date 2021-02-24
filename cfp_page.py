import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import plotly.express as px
import datetime
import re


def get_confname(tweet):
    with open("./conferences.txt", "r") as f:
        all_conf = f.readlines()
    pattern = "("
    for conf in all_conf:
        conf = conf.rstrip()
        pattern += conf
        pattern += "|"
    pattern = pattern[:-1]
    pattern += ")"
    # print(pattern)
    pattern_ = re.compile(pattern)
    match = re.findall(pattern_, tweet)
    if match:
        # print(match)
        return match[0]
    else:
        return ""


def check_workshop(tweet):
    pattern = re.compile(r"workshop", re.IGNORECASE)
    match = re.findall(pattern, tweet)
    if len(match) == 0:
        return 0
    return 1


def create_divs(row, side):
    deadline = row.duedate
    workshop = row.workshop
    tweet = row.tweet
    urls = row.urls
    if len(urls)==0:
        disabled = 1
    else:
        disabled = 0
        url = urls[0]
    conf_name = get_confname(row.tweet)
    deadline_str = deadline.strftime("%d %B, %Y")
    if row.workshop == 1:
        string = "W"
    else:
        string = ""
    content = html.Div(
        className=f"container {side}",
        children=[
            html.Div(
                className="content",
                children=[
                    dbc.Row(
                        children=[
                            html.H2(
                                children=[deadline_str], style={"margin-right": "25px"}
                            ),
                            html.H2(children=[conf_name], style={"align": "right"}),
                            html.Abbr(
                                string,
                                title="Workshop",
                                style={"margin-left": "auto", "font-size": "16px"},
                            ),
                        ]
                    ),
                    html.P(tweet),
                    dbc.Row(
                        children=[
                            html.H4("Useful Links", style={"margin-top":"7px"}),
                            dbc.Button(
                                "Website",
                                color="secondary",
                                style={"margin-left": "10px", "margin-right": "10px", "font-size":"14px"},
                                href = url
                            ),
                            dbc.Button(
                                "Tweet",
                                color="secondary",
                                style={"font-size":"14px"},
                                href=f"https://twitter.com/user/status/{row.id}",
                            ),
                        ]
                    ),
                ],
            )
        ],
    )
    return content


def create_divs_without_date(tweet_ids, start, end):
    return html.Div(
        children=[
            html.Iframe(
                style={
                    "position": "static",
                    "visibility": "visible",
                    "display": "block",
                    "flex-grow": 1,
                    "scrolling": "no",
                    "border": 0,
                    "frame": "false",
                    "margin-left": "15px",
                },
                src=f"https://platform.twitter.com/embed/index.html?dnt=false&embedId=twitter-widget-0&frame=false&hideCard=false&hideThread=false&id={tweet_ids[i]}&theme=light",
                lang="en",
                height="550px",
            )
            for i in range(start, min(end, len(tweet_ids)))
        ],
        style={
            "display": "flex",
            "width": "100%",
            "margin-top": "10px",
            "margin-bottom": "10px",
            "margin-left": "25px",
        },
    )


def cfp_page():
    with open("./data/curate_cfps.pkl", "rb") as f:
        cfps = pd.read_pickle(f)
    with_date = cfps[cfps["duedate"] != 0]
    with_date["workshop"] = with_date["tweet"].apply(check_workshop)
    with_date = with_date.sort_values(by=["duedate"], ascending=True)
    upcoming_dates = with_date[
        with_date["duedate"] > datetime.datetime.now() + datetime.timedelta(days=10)
    ]
    # due_dates = with_date["duedate"].to_list()
    # tweets_date = with_date["tweet"].to_list()

    without_date = cfps[cfps["duedate"] == 0]
    tweet_ids = without_date["id"].to_list()
    child = []
    # len1 = len(with_date.index)
    # len2 = len(without_date.index)

    tweet_no = 0
    for row in upcoming_dates.itertuples():
        if tweet_no % 2 == 0:
            child.append(create_divs(row, "left"))
        else:
            child.append(create_divs(row, "right"))
        tweet_no += 1

    child2 = []
    for start in range(0, len(tweet_ids), 4):
        child2.append(create_divs_without_date(tweet_ids, start, start + 4))

    return html.Div(
        children=[
            html.Div(
                children=child,
                className="timeline",
            ),
            html.H2(
                children=["Conferences without date mentions"],
                style={
                    "margin-top": "35px",
                    "font-size": "28px",
                    "margin-left": "auto",
                    "text-align": "center",
                },
            ),
            html.Div(children=child2),
        ],
        # className="timeline",
    )
