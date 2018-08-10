"""
Created by Alexander Swanson on 6/25/18.
Copyright (c) 2018, Alexander Joseph Swanson Villares
alexjosephswanson@gmail.com

The script for the Reddit AI agent that implements DialogFlow.
"""

# This imported in order to authenticate GCP functionality.
# from Experiment3.src.auth.__j_g_c__ import gcp_authentication

from google.api_core.exceptions import InvalidArgument
from praw.exceptions import APIException
import dialogflow
import praw
import time
import google


class DialogFlowAgent:

    ## Constructor.
    def __init__(
            self,
            reddit_parameters: tuple,
            submission_id: str,
            gcp_project_id: str,
            gcp_session_id: str = "dialogflow_reddit_moderation_agent",
            gcp_language_code: str = "en",
    ):
        """

        :param reddit_parameters:
        :param submission_id:
        :param gcp_project_id: Must be static! The Project ID, respective to the project on the GCP.
        :param gcp_session_id: Can be modified. This field provides a description for the current session.
        :param gcp_language_code:
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

        # Session ID.
        self.gcp_session_id = gcp_session_id

        # Language code.
        self.gcp_language_code = gcp_language_code

        # Session client.
        self.gcp_session_client = dialogflow.SessionsClient()

        # GCP Session.
        self.gcp_session = self.gcp_session_client.session_path(self.gcp_project_id, self.gcp_session_id)


    def define_gcp_parameters(self):
        """
        Redefines the GCP parameters (necessary due to an error caused by the GCP remote).

        :return:
        """

        # # Define Google Cloud Platform (GCP) Parameters.
        # self.gcp_project_id = self.gcp_project_id
        #
        # # Session ID.
        # self.gcp_session_id = self.gcp_session_id
        #
        # # Language code.
        # self.gcp_language_code = self.gcp_language_code


        # Session client.
        self.gcp_session_client = dialogflow.SessionsClient()

        # GCP Session.
        self.gcp_session = self.gcp_session_client.session_path(self.gcp_project_id, self.gcp_session_id)


    def print_subm_comments(self):
        """

        :return:
        """

        # Define list of all Comment objects from the specified Submission.
        self.submission.comments.replace_more(limit=0)
        submission_comments = self.submission.comments.list()

        # Output every comment to console.
        for comment in submission_comments:

            print(comment.body, "\n", '=' * 30, "\n")

        return self


    def run(self, process_time_limit: int = 0, verbose: bool = False, engage=False):
        """

        :param process_time_limit: The limit time for the mainloop (in seconds).
        :param verbose:
        :param engage:
        :return:
        """

        # Define list of all Comments that have been engaged-on.
        engaged_comments = []

        # Define list of all responses generated for Comments.
        comment_responses = []

        # Define the process time limit.
        time_limit = time.time() + process_time_limit

        # Define counter for mainloop iterations.
        mainloop_iterations = 0

        # Run the process until 'process_time_limit' is exceeded.
        while True:

            # Process a short sleep to avoid CPU hog.
            time.sleep(1)

            # Define list of all Comment objects of the specified Submission.
            self.submission.comments.replace_more(limit=0)
            submission_comments = self.submission.comments.list()

            # Consider every Comment for a response.
            for comment in submission_comments:

                # Define container for the Comment context (body).
                comment_body = comment.body


                try:

                    # Ignore Comment is the context length is less than 3 (three words).
                    if len(comment_body.split()) < 5:

                        print(
                            "Encountered Comment of insufficient context length.",
                            "Adding Comment to 'engaged_comments' and continuing process.",
                            "\n", "-" * 20, "\n\n"
                        )

                        # Archive Comment object to 'engaged_comments'.
                        engaged_comments.append(comment)

                        continue

                    # Ignore Comment if it has already been processed.
                    elif comment in engaged_comments:

                        print(
                            "Encountered Comment which has already been processed.",
                            "Continuing process.",
                            "\n", "-" * 20, "\n\n"
                        )

                        continue

                    # Generate a response to the comment with the DialogFlow API.
                    else:

                        # Output status.
                        if verbose: print(comment_body)

                        # Generate response to the comment.
                        comment_response = self.generate_dialogflow_response(comment_body)

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
                                "Created response to Comment: \n",
                                "\t\t",
                                comment_body,
                                "\n\n",
                                "Beginning process stall for 5 minutes.",
                                "\n",
                                "-" * 20,
                                "\n\n"
                            )
                            time.sleep(600)

                            # Redefine the GCP parameters.
                            self.define_gcp_parameters()

                        # Currently ignoring COMMENT if a RESPONSE is received that has already been used. #
                        else:

                            # Output status: account for prevention of repeated response.
                            print(
                                "Received repeated Comment response. Continuing without action. \n",
                                "Beginning process stall for 5 minutes.", "\n", "-" * 20, "\n\n"
                            )

                            # Archive comment to 'engaged_comments'.
                            engaged_comments.append(comment)

                            # Stall process.
                            time.sleep(600)

                            # Redefine the GCP parameters.
                            self.define_gcp_parameters()

                # Catch exception for invalid input to the GCP API.
                except google.api_core.exceptions.InvalidArgument:

                    # Output status.
                    print(
                        "Encountered invalid GCP API argument.",
                        "Comment context length is likely too large.",
                        "Adding Comment to 'engaged_comments' and continuing process.",
                        "\n",
                        "-" * 20,
                        "\n\n"
                    )

                    # Archive Comment object to 'engaged_comments'.
                    engaged_comments.append(comment)

                    # Redefine the GCP parameters.
                    self.define_gcp_parameters()

                    continue

                # Catch Reddit API server-side error.
                except praw.exceptions.APIException:

                    # Output status.
                    print(
                        "Encountered Reddit Comment creation limit.",
                        "Adding Comment to 'engaged_comments' and continuing process.",
                        "\n",
                        "-" * 20,
                        "\n\n"
                    )

                    # Archive Comment object to 'engaged_comments'.
                    engaged_comments.append(comment)

                    # Redefine the GCP parameters.
                    self.define_gcp_parameters()

                    continue

                # Catch a KeyboardInterrupt; this is likely to be the most common way to end the process.
                except KeyboardInterrupt:

                    # Output status.
                    print("Finished loop: ", mainloop_iterations)
                    print("Encountered keyboard interrupt; terminating process.")

                    # End process.
                    return self

                finally:

                    # Redefine the GCP parameters.
                    self.define_gcp_parameters()

            # After end of loop, check if the time since the beginning of the process surpasses the given limit.
            if time.time() > time_limit:

                # Output status.
                print("\n", "Reached time-limit; completed process.")

                # End the process.
                break

            # Continue the process; stall for 5 minutes then fetch for new comments.
            else:

                # Output status.
                print(
                    "Finished loop: ",
                    mainloop_iterations,
                    "\n",
                    "Beginning process stall for 5 minutes.",
                    "\n",
                    "=" * 30,
                    "\n\n"
                )

                # Increment mainloop iterations record.
                mainloop_iterations += 1

                # Redefine the GCP parameters.
                self.define_gcp_parameters()

                # Stall process.
                time.sleep(600)


        return self


    def generate_dialogflow_response(self, text_body):
        """

        :return:
        """

        # Define the text input container for DialogFlow.
        text_input = dialogflow.types.TextInput(
            text=text_body,
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
