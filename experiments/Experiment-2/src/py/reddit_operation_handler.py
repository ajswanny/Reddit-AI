"""
Created by Alexander Swanson on 6/25/18.
Copyright (c) 2018, Alexander Joseph Swanson Villares
alexjosephswanson@gmail.com

A script that allows for the collection of Reddit Submissions within a default Subreddit's (if one is not specified)
"Hot" Submissions and the creation of comments within Submission comment sections.
"""

import praw
import praw.models as reddit


class RedditOperationHandler:
    """
    A handler for Reddit operations with the Python Reddit API Wrapper (PRAW).
    """

    """ Class Fields """
    # The UTC time of retrieval of the Submission objects.
    submissions_retrieval_time = int()


    """ Constructor """
    def __init__(self, reddit_instance: praw.Reddit, **kwargs):
        """
        Creates a RedditOperationHandler with the given Reddit instance.

        :param reddit_instance: The Reddit object that allows for access to Reddit data.
        :param kwargs:
            - subreddit: The working Subreddit for this handler.
        """

        # Define the Reddit instance.
        self.reddit_instance = reddit_instance

        # Define working Subreddit if provided in object instantiation.
        if "subreddit" in kwargs:

            self.working_subreddit = self.reddit_instance.subreddit(display_name=kwargs["subreddit"])
        else:

            self.working_subreddit = self.reddit_instance.subreddit("news")


    """ Methods """
    def get_hot_submissions(self, fetch_limit: int = None, verbose: bool = False):
        """
        Returns a collection of Submissions from the working Subreddit within the "Hot" category.

        :param fetch_limit: The amount of Submissions to collect.
        :param verbose: Whether or not to output process-status updates.
        :return: The list of Submission objects.
        """

        # Define the container for Reddit Submissions.
        submissions = []

        # Output status.
        if verbose: print("Collecting Submission Objects...")


        # Fetch the Reddit Submissions.
        for submission in self.working_subreddit.hot(limit=fetch_limit):
            submissions.append(submission)

        # Output status.
        if verbose: print("...Done")


        # Return the Submissions.
        return submissions


    @staticmethod
    def create_comment(submission: reddit.Submission, comment_content: str):
        """
        Allows for the creation of a comment within the comment section of a Reddit Submission.

        :param submission: The Submission for which to add the desired text as a comment.
        :param comment_content: The content of the comment.
        """

        # Create the comment for the Submission.
        submission.reply(body=comment_content)
