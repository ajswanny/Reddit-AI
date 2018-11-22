"""
Created by Alexander Swanson on 6/25/18.
Copyright (c) 2018, Alexander Joseph Swanson Villares
alexjosephswanson@gmail.com

The script for initialization and operation of a Reddit AI agent.
"""


# Imports
import csv

from .reddit_operation_handler import RedditOperationHandler

import indicoio
import json
import pandas
import praw
import praw.exceptions as praw_exceptions
import praw.models as reddit
import random
import time
from datetime import datetime
from indicoio.utils.errors import IndicoError
from nltk.corpus import stopwords as nltk_stopwords


class RedditAgent:
    """
    The Reddit Agent for spreading awareness throughout Reddit comment sections about a given problem topic.
    """

    """ Class Fields """
    # Indicates if the Agent is to comment within Submission comment sections or not.
    engage = False

    # Indicates whether the algorithm should consider a Submission's Linked Article for keyword analysis.
    do_analyze_subm_articles = False

    # Indicates if the algorithm is to consider a Submission's Title for keyword analysis.
    do_analyze_subm_titles = False

    # The boolean controller for analysis of Submission relevance.
    do_analyze_relevance = False

    # The boolean controller indicating if the program is to record the main DataFrame after process completion.
    record_data = False

    # The title of the problem-topic.
    problem_topic_title = str()

    # TODO: Complete compilation of ptopic keywords.
    # The file-path of the collection of keywords of the Problem-Topic.
    ptopic_keywords_fp = str()

    # The collection of ptopic keywords.
    ptopic_keywords = tuple()

    # The collection of ptopic keywords and their measured relevance level.
    ptopic_kwds_and_relevance = pandas.Series()

    # The tuple containing English stop words.
    eng_stop_words = tuple(nltk_stopwords.words("english"))

    # The main collection of Reddit Submissions.
    default_reddit_submissions = list()

    # The collection of completed keyword analyses for Reddit Submissions.
    data = pandas.DataFrame()

    # The Submission collection limit.
    subm_fetch_limit = int()

    # The Relevance threshold for a Submission's Title and Linked Article.
    relevance_threshold = float()

    # The average size of Submission Titles for the current working Submission collection.
    avg_subm_title_size = 0

    # The minimum keyword intersection magnitude for two collections of keywords.
    keyword_intersection_min = 0

    # The divider for determination of minimum keyword intersection magnitude.
    intersection_min_divider = 0

    # The API key for authentication of the Indico Natural Language Processing API.
    indicoio.config.api_key = '43c624474f147b8b777a144807e7ca95'

    # The main Subreddit for Agent processes.
    work_subreddit = str()

    # The datetime stamp for main operations this Agent performs.
    op_datetime_stamp = str()

    # The handler for Reddit-related operations.
    reddit_op_handler = RedditOperationHandler


    """ Constructor """
    def __init__(
            self,
            reddit_params: tuple,
            problem_topic_id: str,
            problem_topic_title: str,
            data_fp=None,
    ):
        """
        Initializes a RedditAgent for a specified problem-topic.

            :param reddit_params: The values necessary to create access to the Reddit API and Reddit data. The 5-tuple
            structure must always be provided in the order:
                1. client_id
                2. client_secret
                3. user_agent
                4. username
                5. password
        :param problem_topic_id: The short ID of the problem-topic.
        :param problem_topic_title: The Title of the problem-topic.
        :param data_fp: The file-path for the main DataFrame.
        """

        # The PRAW Reddit object.
        self.reddit_instance = praw.Reddit(
            client_id=reddit_params[0],
            client_secret=reddit_params[1],
            user_agent=reddit_params[2],
            username=reddit_params[3],
            password=reddit_params[4]
        )

        # Define the problem-topic's title.
        self.problem_topic_title = problem_topic_title

        # Define the problem topic ID.
        self.problem_topic_id = problem_topic_id

        # The tuple of sentences to be used for expression utterance.
        utterance_sentences_fp = \
            "../resources/problem_topics/" + self.problem_topic_id + "/utterances/utterance_sentences.txt"
        self.utterance_sentences = tuple(open(utterance_sentences_fp).read().splitlines())

        # Define location of the JSON file to archive 'data'.
        if data_fp is None:

            self.data_archive_fp = str
        else:

            self.data_archive_fp = data_fp

        # Initialize the list of already-engaged Submissions.
        try:

            with open("../resources/reddit/engaged_subm_ids.csv") as file:

                # Define the file iterator.
                reader = csv.reader(file)

                # Obtain the list of IDs of Submissions that have been engaged in the past.
                self.engaged_subm_ids = [element for element in list(reader)[0] if element is not '']

        except FileNotFoundError:

            print("File 'engaged_subm_ids.csv' not found.")

        # Initialize dependencies for keyword analysis.
        self.init_kwd_metadata()


    """ Methods """
    def init_kwd_metadata(self):
        """
        Initializes all necessary keyword-relative data fields.
        """

        # Define the FP for the problem topic keywords.
        ptopic_keywords_fp = \
            "../resources/problem_topics/" + self.problem_topic_id + "/problem_topic_kwds/problem_topic_kwds.json"

        # Load the keywords for the problem topic.
        with open(ptopic_keywords_fp, 'r') as file:

            self.ptopic_kwds_and_relevance = pandas.Series(json.load(file))


        # Define the bag of keywords for the problem topic.
        self.ptopic_keywords = tuple(self.ptopic_kwds_and_relevance.index.values)

        # Normalize, converting all keywords to lowercase strings.
        self.ptopic_keywords = list(map(lambda x: x.lower(), self.ptopic_keywords))
        # Remove stop words.
        self.ptopic_keywords = self.remove_stopwords(self.ptopic_keywords)


        # Define the main operation DataFrame.
        self.data = pandas.DataFrame(
            columns=[
                'subm_object',
                'subm_id',
                'comment_count',
                'title',
                'title_kwd_intxn',
                'title_kwd_intxn_size',
                'title_kwds',
                'title_relevance_score',
                'subma_relevance_score',
                'subma_kwd_intxn',
                'subma_kwd_intxn_size',
                'subma_kwds',
                'subma_url',
                'utterance_content'
            ]
        )


    def start(
            self,
            work_subreddit: str,
            engage: bool,
            process_method: str,
            subm_fetch_limit: (int, None),
            analyze_subm_articles: bool,
            relevance_threshold: float,
            record_data: bool = True,
            analyze_subm_titles: bool= True,
            analyze_subm_relevance: bool = False
    ):
        """
        Starts the experimental process.

        :param relevance_threshold: The threshold for the magnitude of relevance between a Submission and the problem-
            topic. This value is used to determine if Submissions should be commented on.
        :param record_data: The boolean indicating if the data generated by the analysis is to be recorded.
        :param analyze_subm_relevance: The boolean indicating if the program is to analyze Submission Relevance.
        :param analyze_subm_titles: The boolean indicating if the program is to analyze a Submission titles.
        :param analyze_subm_articles: The boolean indicating if the program is to analyze Submission Linked Articles.
        :param engage: The boolean indicating if the program is to create comments for Submissions.
        :param process_method: The algorithm to be used:
            - Batch: collect and analyze "Hot" Submissions.
            - Stream: continuously collect Submissions that are newly created.
        :param subm_fetch_limit: The amount of Submissions to fetch from the work Subreddit.
        :param work_subreddit: The Subreddit from which to fetch Submissions.
        """

        # Define global variables.
        self.work_subreddit = work_subreddit
        self.engage = engage
        self.subm_fetch_limit = subm_fetch_limit
        self.do_analyze_subm_articles = analyze_subm_articles
        self.relevance_threshold = relevance_threshold
        self.record_data = record_data
        self.do_analyze_subm_titles = analyze_subm_titles
        self.do_analyze_relevance = analyze_subm_relevance

        # Initialize the Reddit operations handler.
        self.reddit_op_handler = RedditOperationHandler(
            reddit_instance=self.reddit_instance,
            subreddit=self.work_subreddit
        )

        # Initialize the Agent work process.
        if process_method == "batch":

            # Define the date-time stamp for the operation.
            self.op_datetime_stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            # Begin the batch process.
            self.run_batch_process()

        elif process_method == "stream":

            # Unimplemented.
            pass


    def run_batch_process(self):
        """
        Performs Reddit Submission analysis using a batch method of Submission collection. The Submissions that are
        collected, by default, fall under the "Hot" category (see PRAW documentation).

        """

        # Get a batch of Reddit Submissions within the "Hot" category.
        self.default_reddit_submissions = self.reddit_op_handler.get_hot_submissions(fetch_limit=self.subm_fetch_limit)

        # Calculate average length of Submission title length.
        self.avg_subm_title_size = self.calc_avg_subm_title_size(collection=self.default_reddit_submissions)

        # Analyze the Reddit Submissions.
        self.analyze_submissions()

        if self.engage:

            try:

                # Perform engagement for the Submissions if appropriate.
                self.process_subm_engages()

                # Redefine the 'engage' boolean controller.
                self.engage = False

            except praw.exceptions.APIException as e:
                print("Encountered: ", e.message)
                raise e


        # Archive 'data'.
        if self.record_data:

            # Remove elements from 'data' that cannot be serialized.
            t: pandas.DataFrame = self.data.drop("subm_object", 1)

            # Generate the archive FP.
            self.data_archive_fp = \
                "../resources/dataframes/" + self.problem_topic_id + "/data/" + self.op_datetime_stamp + ".json"

            t.to_json(path_or_buf=self.data_archive_fp)


    def analyze_submissions(self):
        """
        Analyzes Reddit Submissions. Analysis is performed on the Titles and Linked Articles of the default collection
        of Reddit Submissions.

        """

        # Create temporary container for keywords analyses.
        keyword_analyses = []

        # Analyze the Reddit Submissions in the default collection, appending each analysis to 'data'.
        for submission in self.default_reddit_submissions:

            # Define container for Submission Title and LinkedArticle analyses.
            analysis = {}

            try:

                # Resolve instances of MoreComments within the Submission's comment forest. That is, expand the forest.
                submission.comments.replace_more(limit=0)

                # Record the Submission ID.
                analysis["subm_id"] = submission.id

                # Record the amount of comments the Submission has.
                analysis["comment_count"] = len(submission.comments.list())

                if self.do_analyze_subm_titles:

                    # Perform keyword analysis of the Submission's Title.
                    analysis.update(self.analyze_subm_title_kwds(submission))

                if self.do_analyze_subm_articles:

                    # Perform keyword analysis of the Submission's Linked Article.
                    analysis.update(self.analyze_subm_artc_kwds(submission))

                if self.do_analyze_relevance:

                    # Perform relevance measurement.
                    analysis.update(self.analyze_relevance(submission))

            except IndicoError:

                # Output status.
                print("Dismissed Submission ", submission.id,
                      " in 'analyze_submissions' due to an Indico IO value error.")
                continue

            # Append the analysis to the collection for merging with 'data'.
            keyword_analyses.append(analysis)


        # Convert 'keyword_analyses' to DataFrame for concatenation with 'data'.
        keyword_analyses = pandas.DataFrame(keyword_analyses)

        # Update 'data'.
        self.data = pandas.concat([self.data, keyword_analyses])


    def analyze_relevance(self, submission: reddit.Submission):
        """
        Generates a definition of relevance to the problem-topic for a given Submission's Title and Linked Article using
        the IndicoIO API's 'relevance' function. The relevance measure is generated by comparing the problem-topic Title
        with a Submission's Title and Linked Article.

        :return: The completed relevance analysis.
        """

        # Define a reference to linked URL of the provided Submission.
        subm_url = submission.url

        # Generate a relevance measure.
        relevance_analyses = indicoio.relevance(
            [submission.title, subm_url],
            [self.problem_topic_title]
        )

        return {"title_relevance_score": relevance_analyses[0][0], "subma_relevance_score": relevance_analyses[1][0]}


    def analyze_subm_artc_kwds(self, submission: reddit.Submission):
        """
        Performs keyword intersection analysis for the ptopic-keywords and a Submission's Linked Article.

        :return: The completed analysis.
        """

        # Define a reference to linked URL of the provided Submission.
        subm_url = submission.url

        # Generate keyword analysis for the Linked Article.
        subm_artc_kwd_analysis = indicoio.keywords(subm_url)

        # Retrieve the keywords identified for the Linked Article.
        subm_artc_kwds = tuple(subm_artc_kwd_analysis.keys())

        # Make all keywords lowercase.
        subm_artc_kwds = tuple(map(lambda x: x.lower(), subm_artc_kwds))

        # Define the intersection of the problem-topic keywords and the Linked Article's keywords.
        subm_artc_kwd_intxn = self.intersect(self.ptopic_keywords, subm_artc_kwds)

        # Define a structure to contain all measures relevant to analysis.
        analysis = {
            "subma_kwd_intxn": subm_artc_kwd_intxn,
            "subma_kwd_intxn_size": float(len(subm_artc_kwd_intxn)),
            "subma_kwds": subm_artc_kwds,
            "subma_url": subm_url
        }


        return analysis


    # noinspection PyDictCreation
    def analyze_subm_title_kwds(self, submission: reddit.Submission, track_subm_obj: bool = True):
        """
        Performs keyword intersection analysis for the problem-topic keyword collection and a given Submission's title.

        In this method, we perform the keywords analysis for the Submission's title and the problem topic keywords.
        For the title, we perform an intersection of its entire word-set, stripped of English stopwords, and
        the problem topic-keywords. We use a Submission's title's entire token set because this is analogous to
        manual evaluation of relevancy. The Submission's title's keywords are archived for possible necessity.

        :return: The completed analysis.
        """


        # Define the collection of the words for the given Submission's Title.
        subm_title_words = tuple(map(lambda x: x.lower(), submission.title.split()))

        # Remove English stopwords from the Submission title token set.
        subm_title_words = self.remove_stopwords(corpus=subm_title_words)

        # Define the intersection of the problem-topic keywords and the Submission's title's content.
        subm_title_intxn = self.intersect(self.ptopic_keywords, subm_title_words)

        # Define the PtopicKeyword-SubmissionTitle intersection magnitude.
        keywords_intersections_count = len(subm_title_intxn)

        # Define the collection of the keywords for the given Submission's Title.
        subm_title_kwds = tuple(indicoio.keywords(submission.title).keys())
        subm_title_kwds = tuple(map(lambda x: x.lower(), subm_title_kwds))
        subm_title_kwds = self.remove_stopwords(subm_title_kwds)

        # Define a structure to contain all measures relevant to analysis.
        analysis = {
            "title": submission.title,
            "title_kwd_intxn": subm_title_intxn,
            "title_kwd_intxn_size": float(keywords_intersections_count),
            "title_kwds": subm_title_kwds
        }

        if track_subm_obj:

            # Append Submission object to the analysis.
            # NOTE: Attempting to serialize the main DataFrame with this field as a member will cause an
            # overflow error.
            analysis["subm_object"] = submission


        return analysis


    def process_subm_engages(self):
        """
        Conducts the engagement actions of the agent.
        """

        # Note: "row" necessary; causes error if exempted.
        for index, row in self.data.iterrows():

            if self.engagement_clearance(self.data.loc[index]):

                # Generate the utterance message.
                utterance_message = self.generate_utterance(submission_data=self.data.loc[index])

                # Save the utterance message content.
                self.data.at[index, "utterance_content"] = utterance_message

                try:

                    print("Delaying process for 10 minutes to avoid 'excessive posting' error. Waiting...")
                    # Delay process to avoid encountering an "excessive posting" error from the Reddit API.
                    time.sleep(600)
                    print("...Done")

                    # Create and deliver a message for the respective Submission providing the Submission object as the
                    # actionable Submission and the utterance to be used.
                    self.reddit_op_handler.create_comment(
                        submission=self.data.subm_object[index],
                        comment_content=utterance_message
                    )

                    # Record the engagement time.
                    self.data.at[index, "engagement_time"] = str(datetime.now())

                    # Record the engaged Submission's ID.
                    with open("../resources/reddit/engaged_subm_ids.csv", "a") as file:

                        # Perform output.
                        file.write(self.data.at[index, "subm_id"] + ",")


                except praw.exceptions.APIException as e:

                    # Output error details and delay operation.
                    print("Caught error: ", e.message, "...Dismissing Submission: ", self.data.at[index, "subm_id"])

            else:

                # Save the utterance message content.
                self.data.at[index, "utterance_content"] = "UNDEFINED"


    def calc_avg_subm_title_size(self, collection: (list, tuple)):
        """
        Calculates the average word count of the title for each Submission in a given collection.

        :return: The value of the average magnitude of Submission Title lengths.
        """

        # Extract the title size for each Submission in 'submission_objects'.
        x = 0
        for submission in collection:
            tokens = submission.title.split()
            num_tokens = len(tokens)
            x += num_tokens

        # Return the average Submission Title size.
        return int(x / len(self.default_reddit_submissions))


    def generate_utterance(self, submission_data: pandas.Series):
        """
        Generates a message to be submitted to a Reddit Submission.

        Currently selecting a random choice, further versions will implement more intelligent utterance generation.

        :return: A random selection from the collection of utterances.
        """

        # TODO:
        #   - Define utterance choice to be generated by considering which of the sample sentences are most similar to
        #     a respective Submission title.


        return random.choice(self.utterance_sentences)


    def get_reddit_submission(self, submission_id: str):
        """
        Returns a Reddit Submission object using a Submission unique ID.

        :param submission_id: The ID of the desired Submission.
        :return: The desired Submission.
        """

        return self.reddit_instance.submission(id=submission_id)


    def remove_stopwords(self, corpus: (list, tuple)):
        """
        Returns the given corpus stripped of English stopwords.

        :param corpus: The corpus to strip of stopwords.
        :return: The normalized corpus.
        """

        return [word for word in corpus if word not in self.eng_stop_words]


    def engagement_clearance(self, submission_data: pandas.Series):
        """
        Determines if the Agent is to engage in a Submission, observing the Submission metadata.

        :return: The boolean indicating whether or not the agent is to comment on a Submission.
        """

        # Determine if the sum of the relevance scores of the Submission title and linked article are above a desired
        # threshold.
        if (submission_data.title_relevance_score + submission_data.subma_relevance_score) > self.relevance_threshold \
                and (submission_data.subm_id not in self.engaged_subm_ids):

            return True

        else:

            # Output status.
            print("Submission " + submission_data.subm_id +
                  " not granted engagement_clearance. It has already been engaged.")

        return False


    @staticmethod
    def intersect(list_x: (list, tuple), list_y: (list, tuple)):
        """
        Performs an intersection of two collections.

        :param list_x: The first collection.
        :param list_y: The second collection.
        :return: The completed intersection.
        """

        return list(set(list_x) & set(list_y))
