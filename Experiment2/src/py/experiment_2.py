"""
Created by Alexander Swanson on 7/31/18.
Copyright (c) 2018, Alexander Joseph Swanson Villares
alexjosephswanson@gmail.com
"""


import pandas
from Experiment2.src.py.reddit_agent import RedditAgent


def process__pr_h_c__():

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
        engage=False,
        subm_fetch_limit=5,
        analyze_subm_articles=True,
        analyze_subm_relevance=True,
        process_method="batch",
        relevance_threshold=0.65,
        archive_data=True
    )


def process__j_g_c__():

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
        problem_topic_id="__j_g_c__",
        utterance_sentences_fp="../resources/utterances/__j_g_c__/utterance_sentences.txt"
    )

    # Initialize the process.
    machine.start(
        work_subreddit='politics',
        engage=False,
        subm_fetch_limit=5,
        analyze_subm_articles=True,
        analyze_subm_relevance=True,
        process_method="batch",
        relevance_threshold=0.65,
        archive_data=False
    )


def main():

    # process__pr_h_c__()
    process__j_g_c__()

    x: pandas.DataFrame = pandas.read_json(
        path_or_buf="../resources/dataframes/__pr_h_c__/data/2018-07-31_22-58-43.json")
    print(x.to_string())


main()
