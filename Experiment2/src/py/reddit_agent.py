"""
Created by Alexander Swanson on 6/25/18.
Copyright (c) 2018, Alexander Joseph Swanson Villares
alexjosephswanson@gmail.com

The script for initialization and operation of a Reddit AI agent.
"""


# Import custom modules.
from .reddit_op_handler import RedditOpHandler

# Import third-party modules.
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


    # Declare global boolean operation controllers.
    engage = False                          # Indicates if the Agent is to engage in utterance with Submissions.
    analyze_subm_articles = False           # Indicates whether the algorithm should consider a Submission's linked
                                            # article for keyword analysis.
    analyze_subm_titles = False             # Indicates if the algorithm is to consider a Submission's title for keyword
                                            #   analysis.
    analyze_relevance = False               # The boolean controller for analysis of Submission relevance.


    # TODO: Complete compilation of ptopic keywords.
    # The location of the collection of topic keywords relative to Puerto Rico and the humanitarian crisis.
    topic_keywords_bag_path = str()

    # The collection of ptopic keywords and their measured relevance to the document.
    ptopic_key_phrases = pandas.Series()

    # The collection of ptopic keywords.
    ptopic_kpr_bag = tuple()

    # The tuple containing English stop words.
    stop_words = tuple(nltk_stopwords.words("english"))

    # The collection of completed keyword analysis for Reddit Submissions.
    data = pandas.DataFrame()

    # The Submission collection limit.
    subm_fetch_limit = 0

    # The average Submission title size for the current working Submission collection: 'submission_objects'.
    avg_subm_title_size = 0

    # The minimum keyword intersection magnitude.
    kpr_intxn_min = 0

    # The divider for determination of minimum keyword intersection magnitude.
    intersection_min_divider = 0

    # The tuple of sentences to be used for expression utterance.
    utterance_sentences = tuple(open("../resources/utterances/utterance_sentences_one.txt").read().splitlines())

    # The authentication for the Indico NLP API.
    indicoio.config.api_key = '43c624474f147b8b777a144807e7ca95'


    def __init__(self, reddit_params: tuple, problem_topic_id: str, data_archive_fp = None,
                 task: str = "Keyword Analysis and Expression"):
        """

        :param reddit_params:
            The 5-tuple structure must always be provided in the order:
                client_id
                client_secret
                user_agent
                username
                password
        """

        # Define the Agent's purpose.
        self.purpose = task

        # The PRAW Reddit object.
        self.reddit_instance = praw.Reddit(
            client_id=reddit_params[0],
            client_secret=reddit_params[1],
            user_agent=reddit_params[2],
            username=reddit_params[3],
            password=reddit_params[4]
        )

        # Define the problem topic ID.
        self.problem_topic_id = problem_topic_id

        # Define location of the JSON file to archive 'data'.
        if data_archive_fp is None:

            self.data_archive_fp = str

        else:

            self.data_archive_fp = data_archive_fp

        # Initialize dependencies for keyword analysis.
        self.init_kpr_metadata()



    def init_kpr_metadata(self):
        """
        Initializes all necessary keyword-relative data fields.
        :return:
        """

        # Define the collection of key-phrases and their salience.
        # TODO: CURRENTLY USING ONLY THE FIRST COLLECTION OF PROBLEM TOPIC KEYWORDS; STILL COMPILING FULL COLLECTION.
        # TODO: REMOVE ABSOLUTE PATHING.
        with open("../resources/problem_topics/__pr_h_c__/problem_topic_kwds/problem_topic_kwds.json", 'r') as fp:

            self.ptopic_key_phrases = pandas.Series(json.load(fp))


        # Define the bag of key-phrases for the problem topic.
        self.ptopic_kpr_bag = tuple(self.ptopic_key_phrases.index.values)

        # Normalize 'ptopic_kpr_bag', converting all key-phrases to lowercase strings.
        self.ptopic_kpr_bag = list(map(lambda x: x.lower(), self.ptopic_kpr_bag))

        # Remove stop words.
        self.ptopic_kpr_bag = self.remove_stopwords(self.ptopic_kpr_bag)


        # Declare the main operation DataFrame.
        self.data = pandas.DataFrame(
            columns=[
                'subm_object',
                'subm_id',
                'comment_count',
                'title',
                'title_kpr_intxn',
                'title_kpr_intxn_size',
                'title_kprs',
                'title_relevance_score',
                'subma_relevance_score',
                'subma_kpr_intxn',
                'subma_kpr_intxn_size',
                'subma_kprs',
                'subma_url',
                'utterance_content'
            ]
        )


        return self


    # noinspection PyAttributeOutsideInit
    def start(self, work_subreddit: str, engage: bool, intxn_min_divider: int, process_method: str,
              subm_fetch_limit: (int, None), analyze_subm_articles: bool, archive_data: bool = True,
              analyze_subm_titles: bool= True, analyze_subm_relevance: bool = False):
        """

        :param archive_data:
        :param analyze_subm_relevance:
        :param analyze_subm_titles:
        :param analyze_subm_articles:
        :param engage:
        :param intxn_min_divider:
        :param process_method:
        :param subm_fetch_limit: The amount of Submissions to fetch from the work Subreddit.
        :param work_subreddit:
        :return:
        """

        # Define True condition for 'engage' if desired.
        if engage:
            self.engage = True


        # Define divider for specified key-phrase-intersection minimum.
        self.intersection_min_divider = intxn_min_divider

        # Define the Submission collection limit.
        self.subm_fetch_limit = subm_fetch_limit

        # Define the boolean controller for analysis of Submission titles.
        self.analyze_subm_titles = analyze_subm_titles

        # Define the boolean controller for analysis of Submission articles.
        self.analyze_subm_articles = analyze_subm_articles

        # Define the boolean controller for analysis of Submission relevance.
        self.analyze_relevance = analyze_subm_relevance

        # Define the boolean controller for the archival of 'data'.
        self.archive_data = archive_data

        # Initialize the Subreddit to be used for work.
        self.work_subreddit = work_subreddit


        # Initialize the Agent work process.
        self.init_workflow(method=process_method)


        return self


    def init_workflow(self, method: str):
        """

        Batch: collect 'hot' Submissions.

        Stream: continuously collect Submissions, perform analysis, and conduct utterance.

        :return:
        """

        # Initialize the Reddit operations handler.
        self.reddit_op_handler = RedditOpHandler(reddit_instance=self.reddit_instance, subreddit=self.work_subreddit)

        if method == "batch":

            # Define the date-time stamp for the operation.
            self.op_datetime_stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

            # Begin the batch process.
            self.run_batch_process()

        elif method == "stream":

            # Unimplemented.
            pass


        return 0


    def run_batch_process(self):
        """
        Begin work using a standard Submission object retrieval using the "hot" listing type.

        :return:
        """

        # Command collection of Submission objects. Note: the '__collect_submissions__' method operates on the default
        # Subreddit for the InputLobe instance, which is defined by the 'work_subreddit' parameter for the call to
        # '__init_operation_lobes__' method.
        self.r_submissions = self.reddit_op_handler.__collect_submissions__(
            fetch_limit=self.subm_fetch_limit
        )


        # Calculate average length of Submission title length.
        self.avg_subm_title_size = self.calc_avg_subm_title_size(collection=self.r_submissions)


        # Perform key-phrase-based success response probability analysis, yielding a DataFrame with metadata of
        # respective analyses.
        self.analyze_submissions()


        try:

            if self.engage:

                # Perform engagement, determining for every Submission if it should be engaged and following through
                # if so.
                self.process_subm_engages()


                # Redefine 'engage' boolean controller.
                self.engage = False

        except praw.exceptions.APIException as e:

            print("Encountered: ", e.message)

        finally:

            # Archive 'data'.
            if self.archive_data:
                self.archive_data()


        return 0


    def analyze_submissions(self):
        """
        A mid-level management method for measurement of Submission engagement success probability.
        The purpose of this method is to allow for the monitoring of the key-phrase-based
        analysis loop and provide accessibility to intervention for optimization or
        modification.

        :return:
        """

        # Create temporary container for key-phrase analyses.
        kpr_analyses = []


        # Analyze every Submission collected, appending each analysis to 'data'.
        for submission in self.r_submissions:

            # Define container for Submission title and SUBMA analyses.
            analysis = {}

            # Update 'analysis' with Submission metadata.
            submission.comments.replace_more(limit=0)

            # Record the amount of comments the Submission has.
            comment_count = len(submission.comments.list())
            analysis["comment_count"] = comment_count


            try:

                if self.analyze_subm_titles:

                    # Perform Submission title key-phrase analysis.
                    analysis.update(self.analyze_subm_title_kprs(submission))

                if self.analyze_subm_articles:

                    # Perform Submission Article key-phrase analysis.
                    analysis.update(self.analyze_subma_kprs(submission))

                if self.analyze_relevance:

                    # Perform relevance measurement.
                    analysis.update(self.__analyze_relevance__(submission))

            except IndicoError:

                # Output status.
                print("Dismissed Submission ", submission.id,
                      " in 'analyze_submissions' due to an Indico IO value error.")

                continue


            # Append the analysis to the collection for merging with 'data'.
            kpr_analyses.append(analysis)


        # Convert 'keyword_analyses' to DataFrame for concatenation with 'data'.
        kpr_analyses = pandas.DataFrame(kpr_analyses)

        # Update 'data'.
        self.data = pandas.concat([self.data, kpr_analyses])


        return self


    # noinspection PyMethodMayBeStatic
    def __analyze_relevance__(self, submission: reddit.Submission):
        """
        Generates a definition of relevance to the ptopic for a given Submission.

        :return:
        :exception Cannot be static: must access current Indico IO authentication.
        """

        # Define alias to linked URL of the provided Submission.
        subm_url = submission.url


        # TODO: Optimize.
        # Generate a relevance measure.
        relevance_analyses = indicoio.relevance(
            [submission.title, subm_url],
            ["Puerto Rico Humanitarian Crisis"]
        )


        return {
            "title_relevance_score": relevance_analyses[0][0],
            "subma_relevance_score": relevance_analyses[1][0]
        }


    def analyze_subma_kprs(self, submission: reddit.Submission):
        """
        Performs key-phrase intersection analysis on the ptopic key-phrases and a Submission's linked article.

        :return:
        """

        # Define alias to linked URL of the provided Submission.
        subm_url = submission.url


        # Generate keyword analysis for the SUBMA.
        subma_kpr_analysis = indicoio.keywords(subm_url)

        # Retrieve key-phrases identified for the SUBMA.
        subma_kprs = tuple(subma_kpr_analysis.keys())

        # Normalize all keywords to be lowercase.
        subma_kprs = tuple(map(lambda x: x.lower(), subma_kprs))


        # Define the intersection of the problem topic key-phrases and the SUBMA.
        subma_intxn = self.intersect(self.ptopic_kpr_bag, subma_kprs)


        # Initialize the keyword intersection count.
        subma_intxn_count = len(subma_intxn)


        # Define a structure to contain all measures relevant to analysis.
        analysis = {
            "subma_kpr_intxn": subma_intxn,
            "subma_kpr_intxn_size": float(subma_intxn_count),
            "subma_kprs": subma_kprs,
            "subma_url": subm_url
        }


        return analysis


    # noinspection PyDictCreation
    def analyze_subm_title_kprs(self, submission: reddit.Submission, track_subm_obj: bool = True):
        """
        Performs keyword intersection analysis for the topic keyword collection and a given Submission's title.

        In this method, we perform the key-phrase analysis for the Submission's title and the problem topic key-phrases.
        For the title, we perform an intersection of its entire token (word) set, stripped of English stopwords, and
        the problem topic key-phrase bag. We use a Submission's title's entire token set because this is analogous to
        manual evaluation of relevancy. The Submission's title's key-phrases are archived for possible necessity.

        :return:
        """


        # Define the keywords for the given Submission title.
        subm_title_kprs = tuple(indicoio.keywords(submission.title).keys())
        subm_title_kprs = tuple(map(lambda x: x.lower(), subm_title_kprs))
        subm_title_kprs = self.remove_stopwords(subm_title_kprs)


        # Define a collection of the words in the Submission title.
        subm_title_tokens = tuple(map(lambda x: x.lower(), submission.title.split()))

        # Remove English stopwords from the Submission title token set.
        subm_title_tokens = self.remove_stopwords(corpus=subm_title_tokens)

        # Define the intersection of the topic key-phrases bag and the Submission's title's content.
        title_intxn = self.intersect(self.ptopic_kpr_bag, subm_title_tokens)


        # Initialize the keyword intersection count.
        keywords_intersections_count = len(title_intxn)


        # Define a structure to contain all measures relevant to analysis.
        analysis = {
            "subm_id": submission.id,
            "title": submission.title,
            "title_kpr_intxn": title_intxn,
            "title_kpr_intxn_size": float(keywords_intersections_count),
            "title_kprs": subm_title_kprs
        }


        if track_subm_obj:

            # Append Submission object to the analysis.
            # NOTE: Attempting to serialize the main DataFrame with this field as a member will cause an
            # overflow error.
            analysis["subm_object"] = submission


        return analysis


    def process_subm_engages(self):
        """
        Conducts the engagement actions of the Agent.

        :return:
        """

        # TODO: DEFINE THE OFFICIAL METRIC FOR THIS FIELD.
        # Define the minimum intersection size.
        # self.intersection_min = int(self.avg_subm_title_size / self.intersection_min_divider)
        # $DEVELOPMENT
        self.kpr_intxn_min = 3


        # TODO: DETERMINE IF "row" IS NECESSARY.
        for index, row in self.data.iterrows():

            if self.clearance(self.data.loc[index]):

                # Generate the utterance message.
                utterance_message = self.generate_utterance(submission_data=self.data.loc[index])


                # Define container of data for operation of Submission engage.
                operation_fields = (self.data.submission_object[index], utterance_message)


                # Archive the utterance message content.
                self.data.at[index, "utterance_content"] = utterance_message


                try:

                    print("Delaying process for 10 minutes to avoid 'excessive posting' error. Waiting...")
                    # Delay process to avoid encountering an "excessive posting" error from the Reddit API.
                    time.sleep(600)
                    print("...Done")

                    # Create and deliver a message for the respective Submission providing the Submission object as the
                    # actionable Submission and the utterance to be used.
                    self.reddit_op_handler.__create_comment__(
                        actionable_submission=operation_fields[0],
                        utterance_content=operation_fields[1]
                    )

                    # Record the engagement time.
                    self.data.at[index, "engagement_time"] = str(datetime.now())

                except praw.exceptions.APIException as e:

                    # Output error details and delay operation.
                    print("Caught error: ", e.message, "...Dismissing Submission: ", self.data.at[index, "subm_id"])

            else:

                # Archive the utterance message content.
                self.data.at[index, "utterance_content"] = "UNDEFINED"


        return 0


    def clearance(self, submission_data: pandas.Series):
        """
        Determines if the Agent is to engage in a Submission, observing the Submission metadata.

        :return:
        """

        # TODO: DETERMINE OFFICIAL MEASUREMENT.
        # Determine clearance status. Clearance evaluates as true if the magnitude of one of the intersections is
        # greater than or equal to 'intersection_min' or if the calculated Submission Article relevance score.
        if (submission_data.title_kpr_intxn_size or submission_data.subma_kpr_intxn_size) >= self.kpr_intxn_min:

            return True

        # TODO: DETERMINE OFFICIAL MEASUREMENT.
        elif (submission_data.title_relevance_score or submission_data.subma_relevance_score) > 0.65:

            return True


        return False


    def calc_avg_subm_title_size(self, collection: (list, tuple)):
        """
        Calculates the average word count of the title for each Submission in 'submission_objects'.

        :return:
        """

        # Define a sum for Submission title sizes.
        x = 0


        # Extract the title size for each Submission in 'submission_objects'.
        for submission in collection:

            tokens = submission.title.split()

            num_tokens = len(tokens)

            x += num_tokens


        # Define the average Submission title size.
        return int(x / len(self.r_submissions))



    def generate_utterance(self, submission_data: pandas.Series):
        """
        Generates a message to be submitted to a Reddit Submission.

        Currently selecting a random choice, further versions will implement more intelligent utterance generation.

        :return:
        """

        # TODO:
        #   - Define utterance choice to be generated by considering which of the sample sentences are most similar to
        #     a respective Submission title.


        return random.choice(self.utterance_sentences)


    def get_reddit_submission(self, submission_id: str):
        """
        Returns a Reddit Submission object using a Submission unique ID.

        :param submission_id:
        :return:
        """

        return self.reddit_instance.submission(id=submission_id)


    @DeprecationWarning
    def calc_response_probability(self, method: str, values: tuple, normalize: bool= True):
        """
        Calculates the calc_response_probability of success, judging this measure with respect to the intersection
        of keywords of the base keyword set and a given Submission title's keywords.

        At the moment, this measure is obtained simply and naively from the length of the intersection
        of the base keyword set and a given Submission title's keyword set.

        # TODO: Substantial optimization.

        :return:
        """

        if method == "keyword":

            # Initialize a calc_response_probability measure; this tuple index refers to the sum of the amount of
            #  values in the intersection list. That is, the amount of keywords that intersected.
            success_probability = values[3]


            if normalize:

                # Return a calc_response_probability measure normalized to a range of [0, 1].
                # The determined max value is obtained from the amount of ptopic keywords.
                return self.normalize(success_probability, minimum=0, maximum=79)

            else:

                return success_probability


    # noinspection PyCompatibility
    def archive_data(self):
        """
        Currently archives field: 'data'.

        :return:
        """

        # Remove elements from 'data' that cannot be serialized.
        t: pandas.DataFrame = self.data.drop("subm_object", 1)

        # Generate the archive FP.
        self.data_archive_fp = \
            "../resources/dataframes/" + str(self.problem_topic_id) + "/data/" + self.op_datetime_stamp + ".json"

        t.to_json(path_or_buf=self.data_archive_fp)

        return 0


    def remove_stopwords(self, corpus: (list, tuple)):
        """
        Returns the given corpus stripped of English stopwords.

        :param corpus:
        :return:
        """

        return [word for word in corpus if word not in self.stop_words]


    @staticmethod
    def intersect(list_x: (list, tuple), list_y: (list, tuple)):
        """

        :param list_x:
        :param list_y:
        :return:
        """

        return list(set(list_x) & set(list_y))


    @staticmethod
    def normalize(value, minimum, maximum):
        """

        :param value:
        :param minimum:
        :param maximum:
        :return:
        """

        numerator = value - minimum
        denominator = maximum - minimum

        return numerator / denominator