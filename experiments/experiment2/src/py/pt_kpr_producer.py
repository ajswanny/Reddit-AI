"""
Created by Alexander Swanson on 8/1/18.
Copyright (c) 2018, Alexander Joseph Swanson Villares
alexjosephswanson@gmail.com
"""

import indicoio
import json
import pandas
from itertools import chain
from pprint import pprint

indicoio.config.api_key = '43c624474f147b8b777a144807e7ca95'


def generate_kprs(
        article_link: str,
        save_data: bool = False,
        normalize_data: bool = False,
        save_fp: str = None,
):
    """
    Generates the key-phrases for an article using the Indico IO API.

    :param normalize_data:
    :param save_data:
    :param save_fp:
    :param article_link:
    :return:
    """

    # Define the key-phrases for the provided article.
    key_phrases = indicoio.keywords(article_link)

    # Save the key-phrases if desired.
    if save_data:

        if normalize_data:
            key_phrases = {lower(key): key_phrases[key] for key in key_phrases}

        with open(save_fp, 'w') as fp:
            json.dump(key_phrases, fp, indent=2)


def read_kprs_as_series(path):
    """
    Reads key-phrase stored in a JSON and returns it as a Pandas Series.

    :param path:
    :return:
    """

    # Load the data.
    with open(path, 'r') as fp:
        data = json.load(fp)

    # Define a Pandas Series from the loaded JSON.
    series = pandas.Series(data)

    # Return the Series.
    return series


def read_write(path, link):
    generate_kprs(path, link)

    read_kprs_as_series(path)


def lower(x: str):
    return x.lower()


def main():

    # a = read_kprs_as_series("ptopic_keywords.json").to_dict()
    #
    # normalized = {lower(key): a[key] for key in a}
    #
    # with open("ptopic_keywords.json", 'w') as fp:
    #     json.dump(normalized, fp, indent=2)

    print("Starting Main")

    generate_kprs(
        article_link="https://edition.cnn.com/2018/07/20/entertainment/james-gunn-exits-guardians-of-the-galaxy-3"
                     "/index.html",
        save_data=True,
        normalize_data=True,
        save_fp="/Users/admin/Documents/Python Personal Workspace/RedditAI/Experiment-2/src/resources/problem_topics/__j_g_c__/problem_topic_kprs/collections/1/topic_key_phrases.json"
    )


main()
