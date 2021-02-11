import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import plotly.express as px


def create_divs(id_cfps, start, end):
    return html.Div(
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
                src=f"https://platform.twitter.com/embed/index.html?dnt=false&embedId=twitter-widget-0&frame=false&hideCard=false&hideThread=false&id={id_cfps[i]}&theme=light",
                lang="en",
                width="550px",
                height="550px",
            )
            for i in range(start, min(end, len(id_cfps)))
        ],
        style={
            "display": "flex",
            "max-width": "550px",
            "width": "100%",
            "margin-top": "10px",
            "margin-bottom": "10px",
        },
    )

def cfp_page():
    with open("./data/curate_cfps.pkl", "rb") as f:
        cfps = pd.read_pickle(f)
    # print(cfps.head(5))
    print(f"idx {len(cfps.index)}")
    id_cfps = cfps["id"].to_list()
    print(f"len - {len(id_cfps)}")
    child = []
    for start in range(0, len(id_cfps), 4):
        print(f"start - {start}")
        child.append(create_divs(id_cfps, start, start+4))
    print(len(child))
    return html.Div(children=child)
