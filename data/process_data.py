#!/usr/bin/env python3

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import re
from nltk.corpus import stopwords
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image


def loadDataset(messages_path="messages.csv",
                categories_path="categories.csv"):
                """
                Load dataset stored as csv files.
                Args:
                    messages_path (str): path to message file.
                    categories_path (str) : path to categories file.
                Returns:
                    A Pandas dataframe.
                """
                messages = pd.read_csv(messages_path)
                categories = pd.read_csv(categories_path)
                df = pd.merge(messages, categories, how="inner", on="id")
                return df


def cleanDatasets(df):
    """
    Clean dataset.
    Args:
        df (dataframe): a Pandas dataframe to be cleaned.
    Returns:
        A cleaned Pandas dataframe.
    """
    categories = df["categories"].str.split(pat=";", expand=True)
    # Select the first row of the categories dataframe
    row = categories.iloc[0, :]
    category_colnames = [
        i[:i.find("-")].title().replace("_", " ")
        for i in list(row)]
    # Rename the columns of `categories`
    categories.columns = category_colnames
    for column in categories:
        # Set each value to be the last character of the string
        categories[column] = categories[column].str[-1]
        # Convert each column from string to integer
        categories[column] = pd.to_numeric(
            categories[column],
            downcast="integer")
    # Link each ID to its categories
    categories = pd.concat([df["id"], categories], axis=1)
    # Drop rows where Related equals 2
    categories = categories[categories["Related"] != 2]
    # Drop column ("Child Alone")
    categories.drop("Child Alone", axis=1, inplace=True)
    # Drop the original categories column from `df`
    df.drop("categories", axis=1, inplace=True)
    # Rename columns
    df.rename(columns={
        "id": "ID",
        "message": "Message",
        "original": "Original",
        "genre": "Genre"},
        inplace=True)
    # Merge the original dataframe with the new `categories` dataframe
    df = df.merge(categories, how="inner", left_on="ID", right_on="id")
    df.drop("id", axis=1, inplace=True)
    # Drop duplicates
    df.drop_duplicates(inplace=True)
    return df


def save2DB(df):
    """
    Save to cleaned dataframe to sqlite database.
    Args:
        df (dataframe): the cleaned Pandas dataframe.
    Returns:
        Not applicable.
    """
    engine = create_engine("sqlite:///messages.db")
    df.to_sql("messages", engine, index=False, if_exists="replace")


def generateWordCloud(df):
    """
    Generate a word cloud image of a given training set.
    Args:
        df (dataframe): the cleaned Pandas dataframe.
    Returns>
        Not applicable.
    """
    words = " ".join(message for message in df.Message)
    words = re.sub(r"[^a-zA-Z]", " ", words)
    words = words.split()
    words = [word for word in words if word not in stopwords.words("english")]
    stopwords_set = set(STOPWORDS)
    words = [word for word in words if word not in stopwords_set]
    words = " ".join(words)
    wordcloud = WordCloud(
        stopwords=stopwords_set,
        background_color="white").generate(words)
    wordcloud.to_file("wordcloud.png")

if __name__ == "__main__":
    df = loadDataset()
    df = cleanDatasets(df)
    save2DB(df)
    generateWordCloud(df)
