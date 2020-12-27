"""
Usage:
python main.py <HASHTAG>

This command scrapes the all tweets pertaining to that hashtag from 1st Jan till the date
"""
import urllib

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import plotly.express as px
from utils import run_all, add_comas
import logging as log

log.basicConfig(filename="log.txt", filemode="a", level=log.INFO)

external_stylesheets = [
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    dbc.themes.BOOTSTRAP,
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

conf_options = ["ACL 2020", "EMNLP 2020", "COLING 2020", "EACL 2021"]

app.layout = html.Div(
    children=[
        dcc.Location(
            id="home-page",
        ),
        html.H2("Select Conference to view Twitter Discussion",style={"textAlign": "center", "margin-top": "10px"}),
        html.Div(
            [
                dbc.DropdownMenu(
                    [
                        dbc.DropdownMenuItem(i, href=f"/{i.replace(' ', '')}")
                        for i in conf_options
                    ],
                    label="Select One Conference",
                ),
            ],
            style= {"textAlign": "center", "fontSize": "20px"}
        ),
        html.Hr(),
        html.Div(id="page-content"),
    ],
)


def show_out(all_info):
    log.info(f"currently executing {all_info['name']}")
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
                ],
                style={"columnCount": 4, "textAlign": "center"},
            ),
            html.Div(
                children=[
                    html.H4(children=add_comas(all_info["Twitter Activity"])),
                    html.H4(children=add_comas(all_info["Likes Counter"])),
                    html.H4(children=add_comas(all_info["Retweets Counter"])),
                    html.H4(children=add_comas(all_info["unique mentions"])),
                ],
                style={"columnCount": 4, "textAlign": "center"},
            ),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(html.H3(children="Top 10 Hashtags"), width={"size": 3}),
                    dbc.Col(html.H3(children="Top 10 mentions"), width={"size": 3}),
                    dbc.Col(html.H3(children="Top 10 URLs"), width={"size": 6}),
                ],
                style={"textAlign": "center", "margin-top": "10px"},
            ),
            html.Div(
                children = [
                    dbc.Row([
                        dbc.Col(html.A(
                                f"#{all_info['top 10 hashtags'][i][0]}" if int(all_info['top 10 hashtags'][i][1])>0 else "",
                                href=f"https://twitter.com/hashtag/{all_info['top 10 hashtags'][i][0]}?src=hashtag_click",
                            ),width={"size": 3}),
                        dbc.Col(html.A(
                            f"@{all_info['top 10 mentions'][i][0]}" if int(all_info['top 10 mentions'][i][1])>0 else "", 
                            href=f"https://twitter.com/{all_info['top 10 mentions'][i][0]}"
                            ),width={"size": 3}),
                        dbc.Col(html.A(f"{all_info['top 10 urls'][i][0]}" if int(all_info['top 10 urls'][i][1])>0 else "",
                        href=f"{all_info['top 10 urls'][i][0]}"),width={"size": 6})
                ],
                style={"textAlign": "center", "fontSize":"18px"},
                ) 
                for i in range(10)]
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
                style={"textAlign": "center"}, children=[html.H4("Most Popular Tweets")]
            ),
            html.Div(
                style={"rowCount": 2},
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
                                src=f"https://platform.twitter.com/embed/index.html?dnt=false&embedId=twitter-widget-0&frame=false&hideCard=false&hideThread=false&id={all_info['tweet_ids'][i]}&theme=light",
                                lang="en",
                                width="550px",
                                height="550px",
                            )
                            for i in range(min(4, len(all_info["tweet_ids"])))
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
                                src=f"https://platform.twitter.com/embed/index.html?dnt=false&embedId=twitter-widget-0&frame=false&hideCard=false&hideThread=false&id={all_info['tweet_ids'][i]}&theme=light",
                                lang="en",
                                width="550px",
                                height="550px",
                            )
                            for i in range(
                                min(4, len(all_info["tweet_ids"])),
                                min(8, len(all_info["tweet_ids"])),
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
        ]
    )


@app.callback(Output("page-content", "children"), [Input("home-page", "pathname")])
def display_page(pathname):
    all_info = dict()
    if pathname == "/":
        log.info(f"time -> {pathname} - #NLProc")
        all_info["name"] = "NLProc"
        all_info = run_all("#NLProc", all_info)
        return show_out(all_info)
    else:
        log.info(f"time -> {pathname} - #{pathname[1:]}")
        all_info["name"] = pathname[1:]
        all_info = run_all(f"#{pathname[1:]}", all_info)
        return show_out(all_info)


if __name__ == "__main__":
    # FOR LOCAL MACHINE RUNNING Uncomment the line below
    # run_type = "LOCAL"
    run_type = "PROD"

    if run_type == "LOCAL":
        app.run_server(debug=True)
    else:
        app.run_server(host="0.0.0.0", debug=True)
