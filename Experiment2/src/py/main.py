"""
Created by Alexander Swanson on 6/25/18.
Copyright (c) 2018, Alexander Joseph Swanson Villares
alexjosephswanson@gmail.com
"""


from Experiment2.src.py.reddit_agent import RedditAgent

from pprint import pprint
import pandas
import json
import indicoio


def process():

    # Define the credentials for the Reddit object.
    reddit_parameters = ("YKsn6_Q_yaP46A",
                         "eygwAD8rMNEhFet0vLQmBqVPxbE",
                         "default_for_research",
                         "agent000001",
                         "S0awesome")

    # Define the MachineLobe with the desired Reddit credentials.
    machine = RedditAgent(
        reddit_params=reddit_parameters,
        analyize_subm_links=False,
        main_df_archive_filepath="Resources/data/_r-politics_/Title_Kwd_Anlysis/2018-02-21_10-09/v2/data.json"
    )

    # Initialize the process.
    machine.start(
        work_subreddit= 'politics',
        engage= False,
        subm_fetch_limit= 1,
        analyze_subm_articles= True,
        intxn_min_divider= 3,
        analyze_subm_relevance= False,
        process_method="batch"
    )


def get_datetime():
    from datetime import datetime

    x = str(datetime.now())

    print(x)


def main():
    # with open("Resources/data/_r-worldnews_/2018-02-18_00-40/data.json", "r") as fp:
    #
    #     x = json.load(fp)

    # r news 1:
    #   Resources/data/_r-news_/2018-02-17_20-54/data.json

    # r worldnews 1:
    #   Resources/data/_r-worldnews_/2018-02-18_00-40/data.json

    x: pandas.DataFrame = pandas.read_json(
        path_or_buf="Resources/data/_r-politics_/Title_Kwd_Anlysis/2018-02-21_10-09/v2/data.json")

    y = x.iloc[0]

    print(y.subm_relevance_score)

    # print((x.loc[x.intersection_size > 1]).to_string())

    # print((x.loc[x.aurl_kwd_intxn_size > 1]).to_string())

    print(x.head().to_string())


def f(x):

    if x == 1:
        process()

    elif x == 2:
        main()

    elif x == 3:
        get_datetime()


f(1)