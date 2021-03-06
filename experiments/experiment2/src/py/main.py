"""
Created by Alexander Swanson on 6/25/18.
Copyright (c) 2018, Alexander Joseph Swanson Villares
alexjosephswanson@gmail.com
"""


from .reddit_agent import RedditAgent

from pprint import pprint
import pandas
import json
import indicoio


def process():

    # Define the credentials for the Reddit object.
    reddit_parameters = (
        "zO1z52xZNtdxrA",
         "VbAzyOfUcj-94a71j8V_6lUTyAM",
         "An observer of Subreddit Streams",
         "ssa1G",
         "subreddit.stream.agent.1.password"
    )

    # Define the MachineLobe with the desired Reddit credentials.
    machine = RedditAgent(
        reddit_params=reddit_parameters,
        problem_topic_id="__pr_h_c__",
        utterance_sentences_fp="../resources/utterances/__pr_h_c__/utterance_sentences.txt"
    )

    # Initialize the process.
    machine.start(
        work_subreddit='politics',
        engage=True,
        subm_fetch_limit=5,
        analyze_subm_articles=True,
        analyze_subm_relevance=True,
        intxn_min_divider=3,
        process_method="batch",
        record_data=True
    )


def get_datetime():
    from datetime import datetime

    x = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    print(x)


def main():

    # process()

    x: pandas.DataFrame = pandas.read_json(
        path_or_buf="../resources/dataframes/__pr_h_c__/data/2018-07-26_21-57-59.json")
    print(x.to_string())


process()
