from flask import Flask, render_template, url_for, request
from sqlalchemy import create_engine
import pandas as pd
import plotly.graph_objs as go
import plotly.plotly as py
import plotly
import json
import numpy as np
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
import pickle

# Load data
engine = create_engine("sqlite:///../data/messages.db")
df = pd.read_sql("select * from messages", con=engine)
df.rename(columns={"Search And Rescue": "Search and Rescue"}, inplace=True)
categories = df.iloc[:, 4:]

plots = []

# First plot
Categories = df.iloc[:, 4:].sum().sort_values()
firstData = [
    go.Bar(
        x=Categories.values,
        y=list(Categories.index),
        orientation="h"
    )
]
firstLayout = go.Layout(
    yaxis=go.layout.YAxis(
        automargin=True
    ),
    xaxis=go.layout.XAxis(
        title="Number of Occurrences",
        automargin=True
    )
)
firstPlot = go.Figure(data=firstData, layout=firstLayout)
plots.append(firstPlot)

# Second plot
genres = df.Genre.str.title().value_counts().sort_values()
labels = list(genres.index)
values = list(genres.values)
colors = ["#FEBFB3", "#E1396C", "#96D38C"]
secondData = [
    go.Pie(
        labels=labels,
        values=values,
        hoverinfo="label+percent",
        textinfo="value",
        marker=dict(
            colors=colors,
            line=dict(color="#000000", width=2)))
]
secondPlot = go.Figure(data=secondData)
plots.append(secondPlot)

# Third plot
img_width = 368
img_height = 450
scale_factor = 1

thirdLayout = go.Layout(
    xaxis=go.layout.XAxis(
        visible=False,
        range=[0, img_width*scale_factor]),
    yaxis=go.layout.YAxis(
        visible=False,
        range=[0, img_height*scale_factor],
        scaleanchor="x"),
    width=img_width*scale_factor,
    height=img_height*scale_factor,
    margin={'l': 0, 'r': 0, 't': 100, 'b': 0},
    images=[go.layout.Image(
        x=0,
        sizex=img_width*scale_factor,
        y=img_height*scale_factor,
        sizey=img_height*scale_factor,
        xref="x",
        yref="y",
        opacity=1.0,
        sizing="stretch",
        source="https://c2.staticflickr.com/8/7897/"
        "46234968524_77f342bec8_o.png")]
)
thirdPlot = go.Figure(data=[{
    "x": [0, img_width * scale_factor],
    "y": [0, img_height * scale_factor],
    "mode": "markers",
    "marker": {"opacity": 0}}], layout=thirdLayout)
plots.append(thirdPlot)

# Generate an ID for each plot
ids = ["plot{}".format(i) for i, _ in enumerate(plots)]

# Convert the Plotly plots to JSON
plotsJSON = json.dumps(plots, cls=plotly.utils.PlotlyJSONEncoder)


# Load pre-trained model
def tokenize(text):
    text = re.sub(r"[^a-zA-Z0-9]", " ", text.lower())
    tokens = word_tokenize(text)
    tokens = [
        WordNetLemmatizer().lemmatize(token)
        for token in tokens
        if token not in stopwords.words("english")]
    return tokens

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Display the UI of the web application.
    Args:
        Not applicable.
    Returns:
        Renders a template with plots and an input field.
    """
    if request.method == "POST":
        try:
            message = "Message: " + request.form["message"]
            # Run prediction here
            prediction = pipeline.predict(np.array([request.form["message"]]))
            prediction = json.dumps(prediction[0].tolist())
        except:
            print("Unable to get the message.")
    else:
        message = "No message has been received yet."
        prediction = json.dumps(np.zeros(35).tolist())
    return render_template(
        "index.html",
        dataset=categories,
        ids=ids,
        plotsJSON=plotsJSON,
        message=message,
        prediction=prediction
        )

if __name__ == "__main__":
    pipeline = pickle.load(
        open("../models/LinearSVCClassifierChain.pkl", "rb"))
    app.run(host="0.0.0.0", port=8000)
