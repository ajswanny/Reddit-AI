"""
Created by Alexander Swanson on 6/25/18.
Copyright (c) 2018, Alexander Joseph Swanson Villares
alexjosephswanson@gmail.com

The script for the Reddit Agent that implements DialogFlow.
"""


""" Imports """
from google.api_core.exceptions import InvalidArgument
from praw.exceptions import APIException
import dialogflow
import praw
import time
import google


class DialogFlowAgent:
    """
    An Agent for the use of DialogFlow to create conversations on Reddit comment sections about a given problem-topic.
    """

    """ Constructor """
    def __init__(
            self,
            reddit_parameters: tuple,
            submission_id: str,
            gcp_project_id: str,
            gcp_session_id: str = "dialogflow_reddit_moderation_agent",
            gcp_language_code: str = "en",
    ):
        """
        Initializes a new DialogFlowAgent to conduct operations on the provided Submission.

        :param reddit_parameters: The values necessary to create access to the Reddit API and Reddit data. The 5-tuple
        structure must always be provided in the order:
            1. client_id
            2. client_secret
            3. user_agent
            4. username
            5. password
        :param submission_id: The ID of the Submission for which to conduct operations.
        :param gcp_project_id: The Project ID, respective to the project on the Google Cloud Platform.
        :param gcp_session_id: Provides a description for the current session.
        :param gcp_language_code: The code indicating which language the DialogFlow agent is expected to interpret.
        """

        # Define the Reddit instance with the specified parameters.
        self.reddit_instance = praw.Reddit(
            client_id=reddit_parameters[0],
            client_secret=reddit_parameters[1],
            user_agent=reddit_parameters[2],
            username=reddit_parameters[3],
            password=reddit_parameters[4]
        )

        # Define the Subreddit for work.
        self.submission = self.reddit_instance.submission(id=submission_id)

        # Define Google Cloud Platform (GCP) Parameters.
        self.gcp_project_id = gcp_project_id
        self.gcp_session_id = gcp_session_id
        self.gcp_language_code = gcp_language_code
        self.gcp_session_client = dialogflow.SessionsClient()
        self.gcp_session = self.gcp_session_client.session_path(self.gcp_project_id, self.gcp_session_id)


    """ Methods """
    def define_gcp_parameters(self):
        """
        Redefines the GCP parameters (necessary due to an error caused by the GCP remote).
        """

        # # Define Google Cloud Platform (GCP) Parameters.
        # self.gcp_project_id = self.gcp_project_id
        #
        # # Session ID.
        # self.gcp_session_id = self.gcp_session_id
        #
        # # Language code.
        # self.gcp_language_code = self.gcp_language_code


        # Define the Sessions Client.
        self.gcp_session_client = dialogflow.SessionsClient()

        # Define the GCP Session.
        self.gcp_session = self.gcp_session_client.session_path(self.gcp_project_id, self.gcp_session_id)


    def print_subm_comments(self):
        """
        Prints the content of the Comments of the working Submission.
        """

        # Define list of all Comment objects from the specified Submission.
        self.submission.comments.replace_more(limit=0)
        submission_comments = self.submission.comments.list()

        # Output every comment to console.
        for comment in submission_comments:

            print(comment.body, "\n", '=' * 30, "\n")


    def run(self, process_time_limit: int = 0, engage=False):
        """
        The main process. The program monitors the working Submission, first generating a response (Comment) to any of
        the existing Submission's Comments that merit a response.

        :param process_time_limit: The limit time for the mainloop (in seconds).
        :param engage: Boolean controller for whether or not to submit generated replies to Comments.
        :return: 0 indicating a process exit.
        """

        # Define the list of all Comments that have been engaged.
        engaged_comments = []

        # Define the list of the responses that have been generated.
        comment_responses = []

        # Define the process time limit.
        time_limit = time.time() + process_time_limit

        # Define counter for mainloop iterations.
        mainloop_iterations = 0

        # Run the process until 'process_time_limit' is exceeded.
        while time.time() <= time_limit:

            # Process a short sleep to avoid CPU hog.
            time.sleep(1)

            # Define list of all Comment objects of the specified Submission.
            self.submission.comments.replace_more(limit=0)
            submission_comments = self.submission.comments.list()

            # Consider every Comment for a response.
            for comment in submission_comments:

                # Define reference to the Comment context (body).
                comment_content = comment.body

                try:

                    # TODO: Determine an appropriate value.
                    # Ignore Comment is the context length is less than 5 (three words).
                    if len(comment_content.split()) < 5:

                        print(
                            "Encountered Comment of insufficient context length. Adding Comment to 'engaged_comments' "
                            "and continuing process.\n", "-" * 20
                        )

                        # Add Comment object to 'engaged_comments'.
                        engaged_comments.append(comment)
                        continue

                    # Ignore Comment if it has already been processed.
                    elif comment in engaged_comments:

                        print("Encountered Comment which has already been processed. Continuing process.\n", "-" * 20)
                        continue

                    # Generate a response to the comment with the DialogFlow API.
                    else:

                        # Respond to the Comment.
                        self.respond(comment, comment_content, comment_responses, engage, engaged_comments)

                        # Stall process.
                        time.sleep(600)

                # Catch exception for invalid input to the GCP API.
                except google.api_core.exceptions.InvalidArgument:

                    # Output status.
                    print(
                        "Encountered invalid GCP API argument. Comment context length is likely too large.",
                        "Adding Comment to 'engaged_comments' and continuing process.\n", "-" * 20
                    )

                    # Archive Comment object to 'engaged_comments'.
                    engaged_comments.append(comment)

                    continue

                # Catch Reddit API server-side error.
                except praw.exceptions.APIException:

                    # Output status.
                    print(
                        "Encountered Reddit Comment creation limit. Adding Comment to 'engaged_comments' and "
                        "continuing process.\n", "-" * 20
                    )

                    # Archive Comment object to 'engaged_comments'.
                    engaged_comments.append(comment)

                    continue

                # Catch a KeyboardInterrupt; this is likely to be the most common way to end the process.
                except KeyboardInterrupt:

                    # Output status.
                    print("Finished loop: ", mainloop_iterations)
                    print("Encountered keyboard interrupt; terminating process.")

                    # End process.
                    return 0

                finally:

                    # Redefine the GCP parameters.
                    self.define_gcp_parameters()

            # Output status.
            print(
                "Finished loop: ", mainloop_iterations, "\nBeginning process stall for 5 minutes.\n", "=" * 20, "\n\n"
            )

            # Increment mainloop iterations record.
            mainloop_iterations += 1

            # Stall process.
            time.sleep(600)

        # Output status.
        print("\n", "Reached time-limit; completed process.")


    def respond(
            self, comment, comment_content: str, comment_responses: list, engage: bool, engaged_comments: list
    ):
        """
        Generates a response to a Comment if the generated response has not already been used and submits it to Reddit
        if desired.

        :param comment: The working Submission's Comment.
        :param comment_content: The body of the Comment.
        :param comment_responses: The collection of responses that have previously been used.
        :param engage: The boolean indicating whether or not to submit the generated response.
        :param engaged_comments: The collection of Comments of the working Submission that have previously been engaged.
        """

        # Generate response to the comment.
        comment_response = self.generate_dialogflow_response(comment_content)

        # Create a response for the comment if the generated response has not already been used.
        if comment_response not in comment_responses:

            # Create a response to the Comment with a body generated by the DialogFlow API.
            if engage:
                comment.reply(comment_response)

            # Archive comment to 'engaged_comments'.
            engaged_comments.append(comment)

            # Archive generated response to 'comment_responses'.
            comment_responses.append(comment_response)

            # Stall process continuation in order to account for Reddit Comment creation rules and to
            # ensure desirable perception of the Agent on Reddit.
            print(
                "Responded to Comment: \n",
                comment_content, "\n",
                "With: \n",
                comment_response, "\n"
                "\n",
                "Beginning process stall for 5 minutes.",
                "\n",
                "-" * 20,
            )

        # Currently ignoring COMMENT if a RESPONSE is received that has already been used.
        else:

            # Output status: account for prevention of repeated response.
            print(
                "Received repeated Comment response. Continuing without action. \n",
                "Beginning process stall for 5 minutes.", "\n", "-" * 20
            )

            # Archive comment to 'engaged_comments'.
            engaged_comments.append(comment)


    def generate_dialogflow_response(self, text):
        """
        Generates an appropriate response to a provided body of text using DialogFlow.

        :return: The generated response.
        """

        # Define the text input container for DialogFlow.
        text_input = dialogflow.types.TextInput(
            text=text,
            language_code=self.gcp_language_code
        )

        # Define the DialogFlow text input query.
        query_input = dialogflow.types.QueryInput(text=text_input)

        # Define a reference to the DialogFlow-generated response.
        response = self.gcp_session_client.detect_intent(
            session=self.gcp_session,
            query_input=query_input
        )

        # Return the response.
        return response.query_result.fulfillment_text
