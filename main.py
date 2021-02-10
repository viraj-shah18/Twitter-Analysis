import urllib
import os
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import plotly.express as px
from utils import show_prev_tweets, add_comas

external_stylesheets = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    dbc.themes.BOOTSTRAP,
]

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    title="Twitter-Analysis",
    update_title="Changing conference...",
)
server = app.server

conf_options = ["EMNLP 2020", "COLING 2020", "EACL 2021", "ACL 2020"]

app.layout = html.Div(
    children=[
        dcc.Location(
            id="home-page",
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.H2(
                        "Select Conference to view Twitter Discussion",
                        style={
                            "textAlign": "right",
                            "margin-top": "10px",
                            "fontSize": "20px",
                        },
                    ),
                    width={"size": 6, "offset": 0},
                ),
                dbc.Col(
                    dbc.DropdownMenu(
                        [
                            dbc.DropdownMenuItem(
                                i,
                                href=f"/{i.replace(' ', '')}",
                                style={"fontSize": "10px"},
                            )
                            for i in conf_options
                        ],
                        label="Select One Conference",
                        style={
                            "textAlign": "left",
                            "z-index": 999,
                            "margin-top": "8px",
                            "fontSize": "18px",
                        },
                    ),
                    width={"size": 2, "offset": 0},
                ),
                dbc.Col(
                    dbc.Button(
                        "Home (NLProc)",
                        color="primary",
                        className="mr-1",
                        href="/",
                        style={
                            "textAlign": "left",
                            "margin-top": "10px",
                            "fontSize": "16px",
                        },
                    ),
                    width={"size": 2, "offset": 0},
                ),
            ],
        ),
        html.Hr(),
        dcc.Loading(
            children=[html.Div(id="page-content")], type="default", id="loading"
        ),
        html.Div(
            style={"textAlign": "center"},
            children=[
                html.Div(
                    children=[
                        html.H1("Most Popular Tweets"),
                        dbc.Button(
                            n_clicks=0,
                            id="recent-button",
                        )                
                    ]
                )
            ],
        ),
        html.Div(children=[html.Div(id="tweet-content")]),
    ],
)


def show_out(all_info):
    return html.Div(
        children=[
            html.H1(
                children=f"Twitter Coverage of {all_info['name']}",
                style={"textAlign": "center"},
            ),
            html.Div(
                children=[
                    html.H3(children="Twitter Activity"),
                    html.H3(children="Likes Counter"),
                    html.H3(children="Retweets Counter"),
                    html.H3(children="Unique Mentions"),
                    html.H3(children="Unique Paper Mentions"),
                ],
                style={"columnCount": 5, "textAlign": "center"},
            ),
            html.Div(
                children=[
                    html.H4(children=add_comas(all_info["Twitter Activity"])),
                    html.H4(children=add_comas(all_info["Likes Counter"])),
                    html.H4(children=add_comas(all_info["Retweets Counter"])),
                    html.H4(children=add_comas(all_info["unique mentions"])),
                    html.H5(children=add_comas(all_info["total_paper_mentions"])),
                ],
                style={"columnCount": 5, "textAlign": "center"},
            ),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(html.H3(children="Top 10 Hashtags"), width={"size": 2}),
                    dbc.Col(html.H3(children="Top 10 mentions"), width={"size": 2}),
                    dbc.Col(html.H3(children="Top 10 URLs"), width={"size": 3}),
                    dbc.Col(
                        html.H3(children="Few Most discussed papers"), width={"size": 5}
                    ),
                ],
                style={"textAlign": "center", "margin-top": "10px"},
            ),
            html.Div(
                children=[
                    dbc.Row(
                        [
                            dbc.Col(
                                html.A(
                                    f"#{all_info['top 10 hashtags'][i][0]}"
                                    if int(all_info["top 10 hashtags"][i][1]) > 0
                                    else "",
                                    href=f"https://twitter.com/hashtag/{all_info['top 10 hashtags'][i][0]}?src=hashtag_click",
                                ),
                                width={"size": 2},
                            ),
                            dbc.Col(
                                html.A(
                                    f"@{all_info['top 10 mentions'][i][0]}"
                                    if int(all_info["top 10 mentions"][i][1]) > 0
                                    else "",
                                    href=f"https://twitter.com/{all_info['top 10 mentions'][i][0]}",
                                ),
                                width={"size": 2},
                            ),
                            dbc.Col(
                                html.A(
                                    f"{all_info['top 10 urls'][i][0]}"
                                    if int(all_info["top 10 urls"][i][1]) > 0
                                    else "",
                                    href=f"{all_info['top 10 urls'][i][0]}",
                                ),
                                width={"size": 3},
                            ),
                            dbc.Col(
                                html.A(
                                    f"{all_info['top_paper_names'][i]}",
                                    href=f"https://www.aclweb.org/anthology/{all_info['top_papers'][i]}.pdf",
                                ),
                                width={"size": 5},
                            ),
                        ],
                        style={"textAlign": "center", "fontSize": "18px"},
                    )
                    for i in range(10)
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Graph(id="graph", figure=all_info["month_plot"]),
                    ),
                    dbc.Col(
                        dcc.Graph(id="graph2", figure=all_info["day_plot"]),
                    ),
                ],
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="graph3", figure=all_info["lang_pie"])),
                    dbc.Col(dcc.Graph(id="graph4", figure=all_info["count_users"])),
                ]
            ),
        ]
    )


def all_time_page(all_info, cat):
    if cat=="all_time":
        tweet_list = all_info["tweet_ids"]
        retweet_list = all_info["retweet_ids"]
    else:
        tweet_list = all_info["recent_tweet_ids"]
        retweet_list = all_info["recent_retweet_ids"]
    return html.Div(
        children=[
            html.Div(
            children=[
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
                                "frame": "false",
                                "margin-left": "15px",
                            },
                            src=f"https://platform.twitter.com/embed/index.html?dnt=false&embedId=twitter-widget-0&frame=false&hideCard=false&hideThread=false&id={tweet_list[i]}&theme=light",
                            lang="en",
                            width="550px",
                            height="550px",
                        )
                        for i in range(min(4, len(tweet_list)))
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
                                "margin-left": "15px",
                            },
                            src=f"https://platform.twitter.com/embed/index.html?dnt=false&embedId=twitter-widget-0&frame=false&hideCard=false&hideThread=false&id={tweet_list[i]}&theme=light",
                            lang="en",
                            width="550px",
                            height="550px",
                        )
                        for i in range(
                            min(4, len(tweet_list)),
                            min(8, len(tweet_list)),
                        )
                    ],
                    style={
                        "display": "flex",
                        "max-width": "550px",
                        "margin-top": "10px",
                        "margin-bottom": "10px",
                    },
                ),
            ],
        ),
        html.Div(
            style={"textAlign": "center"},
            children=[html.H1("Most Retweeted Tweets")],
        ),
        html.Div(
            children=[
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
                                "frame": "false",
                                "margin-left": "5px",
                            },
                            src=f"https://platform.twitter.com/embed/index.html?dnt=false&embedId=twitter-widget-0&frame=false&hideCard=false&hideThread=false&id={retweet_list[i]}&theme=light",
                            lang="en",
                            width="550px",
                            height="550px",
                        )
                        for i in range(min(4, len(retweet_list)))
                    ],
                    style={
                        "display": "flex",
                        "max-width": "550px",
                        "width": "100%",
                        "margin-top": "20px",
                        "margin-bottom": "20px",
                    },
                ),
            ],
        ),
        ]
    )

@app.callback(
    Output("tweet-content", "children"),
    [Input("recent-button", "n_clicks"), Input("home-page", "pathname")],
)
def display_tweets(n_clicks, pathname):
    if pathname == "/":
        name = "NLProc"
    else:
        name = pathname[1:]
    if os.path.exists(f"./data/processed_{name}.pkl"):
        with open(f"./data/processed_{name}.pkl", "rb") as f:
            all_info = pd.read_pickle(f)
    if n_clicks % 2 == 0:
        return all_time_page(all_info, "all_time")
    else:
        return all_time_page(all_info, "recent")


@app.callback(
    Output("recent-button", "children"),
    [Input("recent-button", "n_clicks")]
)
def display_name(n_clicks):
    if n_clicks%2==0:
        return "Recent"
    else:
        return "All-Time"

@app.callback(
    Output("recent-button", "color"),
    [Input("recent-button", "n_clicks")],
)
def display_outline(n_clicks):
    if n_clicks%2==0:
        return "primary"
    else:
        return "secondary"



@app.callback(Output("page-content", "children"), [Input("home-page", "pathname")])
def display_page(pathname):
    known = {
        "/EMNLP2020",
        "/COLING2020",
        "/EACL2021",
        "/ACL2020",
    }

    if pathname == "/":
        all_info = show_prev_tweets("NLProc")
        return show_out(all_info)
    elif pathname in known:
        all_info = show_prev_tweets(f"{pathname[1:]}")
        return show_out(all_info)
    else:
        return html.Div(html.H1("Please select one from the above given conferences"))


if __name__ == "__main__":
    # FOR LOCAL MACHINE RUNNING Uncomment the line below
    run_type = "LOCAL"
    # run_type = "PROD"

    if run_type == "LOCAL":
        app.run_server(debug=True)
    else:
        app.run_server(host="0.0.0.0")
