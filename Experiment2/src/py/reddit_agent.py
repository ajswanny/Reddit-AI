"""
Agent: Cerebrum::MachineLobe
Copyright (c) 2018, Alexander Joseph Swanson Villares
"""


from Cerebrum.input_lobe.input_lobe_h import InputLobe
from Cerebrum.output_lobe.output_lobe_h import OutputLobe

import _pickle as pickle
import indicoio
import json
import pandas
from pprint import pprint
import praw
import praw.exceptions
import praw.models as reddit
import random
import time
import os
from datetime import datetime
from indicoio.utils import errors as indicoio_errors
from nltk.corpus import stopwords as nltk_stopwords



class MachineLobe:
    """
    The Machine Lobe, derivative of the Cerebrum.
    """

    # TODO: Declare all Class fields here.

    # Declare global boolean operation controllers.
    engage = False                          # Indicates if the Agent is to engage in utterance with Submissions.
    start_menu_run = False                  # Indicates if the start menu is running.
    analyze_subm_articles = False           # Indicates whether the algorithm should consider a Submission's linked
                                            #   article for keyword analysis.
    analyze_subm_titles = False             # Indicates if the algorithm is to consider a Submission's title for keyword
                                            #   analysis.
    analyze_subm_relevance = False          # The boolean controller for analysis of Submission relevance.


    # TODO: Complete compilation of ptopic keywords.
    # The location of the collection of topic keywords relative to Puerto Rico and the humanitarian crisis.
    topic_keywords_bag_path = str()

    # The collection of ptopic keywords and their measured relevance to the document.
    _placer_ptopic_kwds_rated = pandas.Series()

    # The collection of ptopic keywords.
    ptopic_kwds_bag = tuple()

    # The tuple containing English stop words.
    stop_words = tuple(nltk_stopwords.words("english"))


    # The collection of completed keyword analysis for Reddit Submissions.
    _main_kwd_df = pandas.DataFrame()


    # The Submission collection limit.
    subm_fetch_limit = 0

    # The average Submission title size for the current working Submission collection: 'submission_objects'.
    avg_subm_title_size = 0

    # The minimum keyword intersection magnitude.
    kwd_intxn_min = 0

    # The divider for determination of minimum keyword intersection magnitude.
    intersection_min_divider = 0


    # The tuple of sentences to be used for expression utterance.
    utterance_sentences = tuple(open("Resources/Utterances/utterance_sentences_(manual).txt").read().splitlines())


    # The authentication for the Indico NLP API.
    indicoio.config.api_key = '43c624474f147b8b777a144807e7ca95'


    def __init__(self, platform: str, reddit_params: tuple, main_df_archive_filepath: str, analyize_subm_links: bool,
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


        # The current platform (i.e., Reddit, Facebook, etc.).
        self.working_platform = platform


        # The PRAW Reddit object.
        self.reddit_instance = praw.Reddit(
            client_id= reddit_params[0],
            client_secret= reddit_params[1],
            user_agent= reddit_params[2],
            username= reddit_params[3],
            password= reddit_params[4]
        )


        # Define location of the JSON file to archive '_main_kwd_df'.
        self.FILEPATH_main_kwd_df = main_df_archive_filepath


        # Initialize dependencies for keyword analysis.
        self.__init_kwd_process_metadata__()



    #-}



    def __init_operation_lobes__(self, work_subreddit: str):

        self._input_lobe = self.__new_InputLobe__(
            reddit_instance= self.reddit_instance,
            subreddit= work_subreddit
        )

        self._output_lobe = self.__new_OutputLobe__(
            reddit_instance= self.reddit_instance,
            subreddit= work_subreddit
        )



    def __init_kwd_process_metadata__(self):
        """
        Init method to initialize all necessary keyword-relative data fields.
        :return:
        """

        # TODO: Define the keywords collection.
        # A temporary definition of the collection of the topic keywords.
        # NOTE: CURRENTLY USING ONLY THE FIRST COLLECTION OF PROBLEM TOPIC KEYWORDS; STILL COMPILING FULL COLLECTION.
        with open("Resources/ProblemTopicKeywords/v1/topic_keywords.json", 'r') as fp:

            self._placer_ptopic_kwds_rated = pandas.Series(json.load(fp))


        # Define the bag of words for the problem topic keyword data.
        self.ptopic_kwds_bag = tuple(self._placer_ptopic_kwds_rated.index.values)

        # Normalize 'ptopic_kwds_bag', converting all keywords to lowercase strings.
        self.ptopic_kwds_bag = list(map(lambda x: x.lower(), self.ptopic_kwds_bag))

        # Remove stop words.
        self.ptopic_kwds_bag = self.remove_stopwords(self.ptopic_kwds_bag)


        # TODO: Define metadata.
        # TODO: Implement inclusion of AURL KWD analysis within the 'success_probability' measure.
        # Declare the main operation DataFrame.
        self._main_kwd_df = pandas.DataFrame(
            columns= [
                'subm_title_keywords', 'intersection_size', 'keywords_intersection',
                'aurl_kwd_intxn', 'aurl_kwd_intxn_size', 'subm_aurl_kwds',
                'submission_id', 'submission_object', 'submission_title',
                'success_probability', 'utterance_content', 'engagement_time',
                "comment_count", "subm_relevance_score"
            ]
        )


        return self


    def remove_stopwords(self, corpus: (list, tuple)):
        """
        Returns the given corpus restricted of English stopwords.

        :param corpus:
        :return:
        """

        return [word for word in corpus if word not in self.stop_words]



    # noinspection PyCompatibility
    def archive_main_dataframe(self):
        """
        Currently archives field: '_main_kwd_df'. Future development will see this method allow for the archival of
        any specified Class data field.

        # TODO: Update to allow for archival of any specified DataFrame.

        :return:
        """

        # Archive '_main_kwd_df'.
        x: pandas.DataFrame = self._main_kwd_df.drop("submission_object", 1)

        x.to_json(path_or_buf = self.FILEPATH_main_kwd_df)


        return 0



    @staticmethod
    def __new_InputLobe__(reddit_instance: praw.Reddit, subreddit: str):
        """
        A method allowing for customizable creation of InputLobe objects.

        :param reddit_instance:
        :param subreddit:
        :return:
        """

        return InputLobe(reddit_instance= reddit_instance, subreddit= subreddit)



    @staticmethod
    def __new_OutputLobe__(reddit_instance: praw.Reddit, subreddit: str):
        """
        A method allowing for customizable creation of OutputLobe objects.

        :param reddit_instance:
        :param subreddit:
        :return:
        """

        return OutputLobe(reddit_instance= reddit_instance, subreddit= subreddit)



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



    def __test_functionality__(self):
        """

        :return:
        """

        print(type(self._main_kwd_df))

        return 0



    # noinspection PyAttributeOutsideInit
    def start(self, work_subreddit: str, engage: bool, intersection_min_divider: int,
              subm_fetch_limit: (int, None), analyze_subm_articles: bool, override: bool= False,
              analyze_subm_titles: bool= True, analyze_subm_relevance: bool = False):
        """
        Begins the process of Work.

        Workflow for KeywordWork algorithm:
            1.  __init_keyword_workflow__
            2.  __setup_process__
                3.  __standard_process__
                    4.  __process_subm_analysis__

                3.  __stream_process__
                    ...


        :return:
        """

        # Define all necessary fields.
        self.set__start__values(engage, intersection_min_divider, subm_fetch_limit, analyze_subm_articles,
                                analyze_subm_titles, analyze_subm_relevance)


        # Quick formal process override.
        if override:

            self.__init_keyword_workflow__(work_subreddit= work_subreddit)

            return self


        # Output status.
        print("\n", "-" * 100, '\n',
              "The Machine Lobe has been instantiated and initialized.", '\n\n',
              "\t[1] Begin KeywordWork process. \t\t [2] Exit.", '\n',
              )


        while self.start_menu_run:

            # Prompt for desired operation.
            action_choice = input("Option: ")

            if action_choice is 1:

                # Initialize keyword analysis workflow.
                self.__init_keyword_workflow__(work_subreddit= work_subreddit)

                break

            if action_choice is 2:

                # Future implementation.
                pass

            else:

                # Exit program.
                self.start_menu_run = False
                break


        return 0



    def set__start__values(self, engage: bool, intersection_min_divider: int,
                           subm_fetch_limit: (int, None), analyze_subm_articles: bool,
                           analyze_subm_titles: bool, analyze_subm_relevance: bool):
        """
        Trivially defines the values for the '__start__' method.

        :return:
        """

        # Define True condition for 'engage' if desired.
        if engage:
            self.engage = True


        # Define True condition for start menu run-state.
        self.start_menu_run = True


        # Define specified intersection minimum determination divider.
        self.intersection_min_divider = intersection_min_divider


        # Define the Submission collection limit.
        self.subm_fetch_limit = subm_fetch_limit


        # Define the boolean controller for analysis of Submission titles.
        self.analyze_subm_titles = analyze_subm_titles


        # Define the boolean controller for analysis of Submission article links.
        self.analyze_subm_articles = analyze_subm_articles


        # Define the boolean controller for analysis of Submission relevance.
        self.analyze_subm_relevance = analyze_subm_relevance


        return 0



    def __init_keyword_workflow__(self, work_subreddit: str):
        """

        :return:
        """

        self.start_menu_run = False
        self.__setup_process__(method="standard", work_subreddit= work_subreddit)


        return 0



    def __setup_process__(self, method: str, work_subreddit: str):
        """
        Standard: collect 'hot' Submissions.

        Stream: continuously collect Submissions, perform analysis, and conduct utterance.

        :param method:
        :return:
        """

        if method == "standard":

            self.__standard_process__(work_subreddit= work_subreddit)

        elif method == "stream":

            # Unimplemented.
            pass


        return 0



    def __standard_process__(self, work_subreddit: str):
        """
        Begin work using a standard Submission object retrieval using the "hot" listing type.

        :return:
        """

        # Create InputLobe object to produce Submission metadata for the "news" Subreddit.
        # Create OutputLobe object to handle expression utterance.
        self.__init_operation_lobes__(work_subreddit= work_subreddit)


        # Command collection of Submission objects. Note: the '__collect_submissions__' method operates on the default
        # Subreddit for the InputLobe instance, which is defined by the 'work_subreddit' parameter for the call to
        # '__init_operation_lobes__' method.
        self.submission_objects = self._input_lobe.__collect_submissions__(
            return_objects= True,
            fetch_limit= self.subm_fetch_limit
        )


        # Calculate average length of Submission title length.
        self.avg_subm_title_size = self.__calc_avg_subm_title_size__(collection= self.submission_objects)


        # Perform keyword-based success probability analysis, yielding a DataFrame with metadata respective analyses.
        self.__process_subm_analysis__()


        try:

            if self.engage:

                # Perform engagement, determining for every Submission if it should be engaged and following through if so.
                self.__process_submission_engages__()


                # Redefine 'engage' boolean controller.
                self.engage = False

        except praw.exceptions.APIException as E:

            print("Encountered: ", E.message)

        finally:

            # Archive '_main_kwd_df'.
            self.archive_main_dataframe()


        return 0



    def __process_submission_engages__(self):
        """
        Conducts the engagement actions of the Agent.

        :return:
        """

        # Define the minimum intersection size.
        # self.intersection_min = int(self.avg_subm_title_size / self.intersection_min_divider)
        self.kwd_intxn_min = 3


        def out(x: tuple):
            """
            Implementer of expression utterance operation.

            :param x:
            :return:
            """

            self._output_lobe.submit_submission_expression(actionable_submission= x[0], utterance_content= x[1])


        for index, row in self._main_kwd_df.iterrows():

            if self.__clearance__(self._main_kwd_df.loc[index]):

                # Generate the utterance message.
                utterance_message = self.__generate_utterance__(submission_data= self._main_kwd_df.loc[index])


                # Define container of data for operation of Submission engage.
                operation_fields = (self._main_kwd_df.submission_object[index], utterance_message)


                # Archive the utterance message content.
                self._main_kwd_df.at[index, "utterance_content"] = utterance_message


                try:

                    # Create and deliver a message for the respective Submission.
                    # We provide the Submission object as the actionable Submission and the Submission metadata.
                    out(operation_fields)

                except praw.exceptions.APIException as E:

                    # Output error details and delay operation.
                    print("Caught error: ", E.message, "\nWaiting...")
                    time.sleep(600)

                finally:

                    out(operation_fields)


                # Record the engagement time.
                self._main_kwd_df.at[index, "engagement_time"] = str(datetime.now())


                break


        return 0



    def __clearance__(self, submission_data: pandas.Series):
        """
        Determines if the Agent is to engage in a Submission, observing the Submission metadata.

        # TODO: Substantial optimization.

        :return:
        """

        # Initialize a clearance determination.
        clearance = False


        # Determine clearance status. Clearance evaluates as true if the magnitude of the intersection is greater than
        # or equal to 'intersection_min'.
        if (submission_data.intersection_size or submission_data.aurl_kwd_intxn_size) >= self.kwd_intxn_min:

            clearance = True

        elif sum(submission_data.subm_relevance_score) > 5:

            clearance = True


        return clearance



    def __calc_avg_subm_title_size__(self, collection: (list, tuple)):
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
        return int(x / len(self.submission_objects))



    def __generate_utterance__(self, submission_data: pandas.Series):
        """
        Generates a message to be submitted to a Reddit Submission.

        Currently selecting a random choice, further versions will implement more intelligent utterance generation.

        # TODO: Substantial optimization.

        :return:
        """

        # Option:
        #   - Define utterance choice to be generated by considering which of the sample sentences are most similar to
        #     a respective Submission title.


        return random.choice(self.utterance_sentences)



    def __process_subm_analysis__(self):
        """
        A mid-level management method for measurement of Submission engagement success probability.
        The purpose of this method is to allow for the monitoring of the keyword-based
        analysis loop and provide accessibility to intervention for optimization or
        modification.

        :return:
        """


        # Create temporary container for keyword analyses.
        keyword_analyses = []


        indico_scraping_error = indicoio_errors.IndicoError


        # Analyze every Submission collected, appending each analysis to '_main_kwd_df'.
        for submission in self.submission_objects:

            # Define container for Submission title and AURL analyses.
            analysis = {}

            # Update 'analysis' with Submission metadata.
            submission.comments.replace_more(limit= 0)
            comment_count = len(submission.comments.list())

            analysis["comment_count"] = comment_count


            if self.analyze_subm_titles:

                # Perform Submission title keyword analysis.
                analysis.update(self.__analyze_subm_title_kwds__(submission))

            if self.analyze_subm_articles:

                try:

                    # Perform Submission AURL keyword analysis.
                    analysis.update(self.__analyze_subm_aurl_kwds__(submission))

                except indico_scraping_error:

                    continue

            if self.analyze_subm_relevance:

                try:

                    # Perform relevance measurement.
                    analysis["subm_relevance_score"] = self.__analyze_subm_relevance__(submission)

                except indico_scraping_error:

                    continue


            # Append the analysis to the collection for merging with '_main_kwd_df'.
            keyword_analyses.append(analysis)


        # Convert 'keyword_analyses' to DataFrame for concatenation with '_main_kwd_df'.
        keyword_analyses = pandas.DataFrame(keyword_analyses)


        # Update '_main_kwd_df'.
        self._main_kwd_df = pandas.concat([self._main_kwd_df, keyword_analyses])


        return 0



    def __analyze_subm_relevance__(self, submission: reddit.Submission):
        """
        Generates a definition of relevance to the ptopic for a given Submission.

        :return:
        """

        # Define alias to linked URL of the provided Submission.
        subm_url = submission.url


        # Generate a relevance measure.
        relevance_analyses = indicoio.relevance(
            [submission.title, subm_url],
            [
                "Puerto Rico Humanitarian Crisis",
                # "Humanitarian Crisis",
                # "Empathy",
                # "Anger"
            ]
        )


        # Convert "Anger" measures to negative values.
        # relevance_analyses[0][3] = -abs(relevance_analyses[0][3])
        # relevance_analyses[1][3] = -abs(relevance_analyses[1][3])


        return relevance_analyses




    def __analyze_subm_aurl_kwds__(self, submission: reddit.Submission):
        """
        Performs keyword intersection analysis on the ptopic keywords and a Submission's linked article accessed by an
        attached URL.

        This attached article for a Submission is referenced as "AURL".

        :return:
        """

        # Define alias to linked URL of the provided Submission.
        subm_url = submission.url


        # Generate keyword analysis for the AURL.
        subm_aurl_kwd_analysis = indicoio.keywords(subm_url)

        # Retrieve the exclusively the keywords identified for the AURL.
        subm_aurl_kwds = tuple(subm_aurl_kwd_analysis.keys())


        # Normalize all keywords to be lowercase.
        subm_aurl_kwds = tuple(map(lambda x: x.lower(), subm_aurl_kwds))


        # Define the intersection of the ptopic keywords and the AURL.
        subm_aurl_intxn = self.intersect(self.ptopic_kwds_bag, subm_aurl_kwds)


        # Initialize the keyword intersection count.
        subm_aurl_intxn_count = len(subm_aurl_intxn)


        # Define a structure to contain all measures relevant to analysis.
        analysis = {
            "aurl_kwd_intxn": subm_aurl_intxn,
            "aurl_kwd_intxn_size": float(subm_aurl_intxn_count),
            "subm_aurl_kwds": subm_aurl_kwds,
            "sub_aurl_url": subm_url
        }


        return analysis



    # noinspection PyDictCreation
    def __analyze_subm_title_kwds__(self, submission: reddit.Submission, return_subm_obj: bool = True):
        """
        'Analyze Submission Keywords'

        Performs keyword intersection analysis for the topic keyword collection and a given Submission's title.

        :return:
        """


        # Define the keywords for the given Submission title.
        # NOTE: CURRENTLY USING JUST THE KEYWORDS GIVEN; NOT INCLUDING THEIR LIKELY RELEVANCE.
        # TODO: Officially determine if we are to use a Submission's title's keywords, or the entire content of a
        # TODO  Submission title.
        #
        # subm_title_keyword_analysis = indicoio.keywords(submission.title)
        # subm_title_keywords = tuple(subm_title_keyword_analysis.keys())
        """ PLACER """
        subm_title_keywords = 0


        # Define a collection of the words in a Submission title.
        subm_title_tokens = tuple(map(lambda x: x.lower(), submission.title.split()))

        # Remove English stopwords from the Submission title word content set.
        subm_title_tokens = self.remove_stopwords(corpus= subm_title_tokens)

        # Define the intersection of the topic keywords bag and the Submission's title content.
        # FIXME Currently using the entire set of words from Submission titles -- this is naturally what we as people do
        # FIXME when reading documents to identify relevance to a certain topic.
        title_intxn = self.intersect(self.ptopic_kwds_bag, subm_title_tokens)


        # Initialize the keyword intersection count.
        keywords_intersections_count = len(title_intxn)


        # Define a structure to contain all measures relevant to analysis.
        analysis = {
            "submission_id": submission.id,
            "submission_title": submission.title,
            "title_intxn": title_intxn,
            "title_intxn_size": float(keywords_intersections_count),
            "title_kwds": subm_title_keywords
        }


        # Define a probability measure of success and append this to the 'analysis' dictionary.
        # This figure is used to determine whether or not the Agent will submit a textual expression
        # to a Reddit Submission.
        # TODO: This measure is to be optimized in the future.
        analysis["success_probability"] = self.probability(method= "keyword", values= tuple(analysis.values()))



        if return_subm_obj:

            # Append Submission object to the analysis.
            # NOTE: Attempting to serialize the main DataFrame with this field as a member will cause an
            # overflow error.
            analysis["submission_object"] = submission


        return analysis



    def __get_reddit_submission__(self, submission_id: str):
        """
        Returns a Reddit Submisssion object using a Submission unique ID.

        :param submission_id:
        :return:
        """

        return self.reddit_instance.submission(id= submission_id)



    def probability(self, method: str, values: tuple, normalize: bool= True):
        """
        Calculates the probability of success, judging this measure with respect to the intersection
        of keywords of the base keyword set and a given Submission title's keywords.

        At the moment, this measure is obtained simply and naively from the length of the intersection
        of the base keyword set and a given Submission title's keyword set.

        # TODO: Substantial optimization.

        :return:
        """

        if method == "keyword":

            # Initialize a probability measure; this tuple index refers to the sum of the amount of values
            # in the intersection list. That is, the amount of keywords that intersected.
            success_probability = values[3]


            if normalize:

                # Return a probability measure normalized to a range of [0, 1].
                # The determined max value is obtained from the amount of ptopic keywords.
                return self.normalize(success_probability, minimum= 0, maximum= 79)

            else:

                return success_probability


