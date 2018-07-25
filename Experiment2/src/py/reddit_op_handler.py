"""
Created by Alexander Swanson on 6/25/18.
Copyright (c) 2018, Alexander Joseph Swanson Villares
alexjosephswanson@gmail.com

A script that allows for the collection of Reddit Submissions within a default Subreddit's (if one is not specified)
"Hot" Submissions.
"""

import praw
import praw.models as reddit
from pprint import pprint


# TODO: Implement data input.

class RedditOpHandler:
    """
    The Input Lobe, derivative of the Cerebrum.

    """

    # The UTC time of retrieval of the Submission objects.
    submissions_retrieval_time = int()

    def __init__(self, reddit_instance: praw.Reddit, **kwargs):
        """

        :param reddit_instance:
        :param kwargs:
        """

        # Define the Reddit instance.
        self.reddit_instance = reddit_instance

        # Define default working Subreddit if provided in object instantiation.
        if "subreddit" in kwargs:

            self.default_subreddit = self.reddit_instance.subreddit(display_name=kwargs["subreddit"])

        else:

            self.default_subreddit = self.reddit_instance.subreddit("news")

    def __test_functionality__(self):

        # print(self.reddit_instance.auth)
        #
        # submission = self.reddit_instance.submission(id="7v6jp6")
        #
        # print(submission.title)
        #
        # # for submission in self.reddit_instance.subreddit('news').hot(limit=10):
        # #
        # #     print(submission.id)
        #
        # for submission in self.default_subreddit.hot():
        #     print(submission.title)

        x = self.__collect_submissions__(listing_type="hot")

        return 0

    def __collect_submissions__(self, listing_type: str = None, fetch_limit=None, return_objects=True):

        submissions = []
        counter = 0

        print("\n", "-" * 50, '\n')
        print("\tCollecting Submission Objects...")

        for submission in self.default_subreddit.hot(limit=fetch_limit):
            # # Increment 'counter'.
            # counter += 1

            # Store Submission in 'submissions'.
            submissions.append(submission)

        print("\tTask completed.")
        print("\n", "-" * 50, '\n')

        if return_objects:

            return submissions

        else:

            return 0


    def submit_submission_expression(self, actionable_submission: reddit.Submission, utterance_content: str):
        """
        A high-level management function to oversee expression utterance for Reddit Submissions.

        :param actionable_submission:
        :param utterance_content:
        :return:
        """

        # Perform expression utterance to the given Reddit Submission.
        actionable_submission.reply(

            body=utterance_content

        )

        return self
