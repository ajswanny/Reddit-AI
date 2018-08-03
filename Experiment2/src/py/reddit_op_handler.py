"""
Created by Alexander Swanson on 6/25/18.
Copyright (c) 2018, Alexander Joseph Swanson Villares
alexjosephswanson@gmail.com

A script that allows for the collection of Reddit Submissions within a default Subreddit's (if one is not specified)
"Hot" Submissions and the creation of comments within Submission comment sections.
"""

import praw
import praw.models as reddit


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


    def collect_submissions(self, listing_type: str = None, fetch_limit=None):
        """

        :param listing_type:
            - "hot"
            - "new"
            - "controversial"
            - "rising"
        :param fetch_limit:
        :return:
        """

        # Define the container for Reddit Submissions.
        submissions = []

        # Output status.
        print("Collecting Submission Objects...")

        # Fetch the Reddit Submissions.
        for submission in self.default_subreddit.hot(limit=fetch_limit):

            # Store Submission in 'submissions'.
            submissions.append(submission)

        # Output status.
        print("...Done")


        # Return the Submissions.
        return submissions


    def create_comment(self, actionable_submission: reddit.Submission, utterance_content: str):
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
