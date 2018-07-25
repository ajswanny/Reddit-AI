"""
Created by Alexander Swanson on 6/25/18.
Copyright (c) 2018, Alexander Joseph Swanson Villares
alexjosephswanson@gmail.com
"""

from Experiment3.src.auth import GCPAuthentication
from google.api_core.exceptions import InvalidArgument
from praw.exceptions import APIException
import dialogflow
import praw
import time
import google


class DialogFlowAgent:


    def __init__(
            self,
            reddit_parameters: tuple,
            submission: str,
            gcp_project_id: str = "cs-196",
            gcp_session_id: str = "dialogflow_reddit_moderation_agent",
            gcp_language_code: str = "en",
    ):
        """

        :param reddit_parameters:
        :param submission:
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
        self.submission = self.reddit_instance.submission(id= submission)


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


    def run_main_process(
            self,
            time_limiter: int = 0,
            verbose: bool = False,
            engage=False
    ):
        """

        :param time_limiter: The limit time for the mainloop (in seconds).
        :param verbose:
        :param engage:
        :return:
        """

        # Define list of all Comments that have been engaged-on.
        engaged_comments = []

        # Define list of all responses generated for Comments.
        comment_responses = []


        # Define time limit.
        timeout = time.time() + time_limiter


        # Define counter for mainloop iterations.
        mainloop_iterations = 0

        while True:

            # Define list of all Comment objects from the specified Submission.
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
                            "\n"
                        )

                        # Archive Comment object to 'engaged_comments'.
                        engaged_comments.append(comment)


                        continue

                    # Ignore Comment if it has already been processed.
                    elif comment in engaged_comments:

                        print(
                            "Encountered Comment which has already been processed.",
                            "Continuing process.",
                            "\n"
                        )


                        continue

                    else:

                        # Output status.
                        if verbose: print(comment_body)


                        # Generate response to the comment.
                        comment_response = self.generate_dialogflow_response(comment_body)

                        # Ensure that no duplicate responses are generated.
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

                            time.sleep(300)

                            # Redefine the GCP parameters.
                            self.define_gcp_parameters()

                        # Currently ignoring COMMENT if a RESPONSE is received that has already been used. #
                        else:

                            # Account for prevention of repeated response.
                            print(
                                "Received repeated Comment response. Continuing without action. \n",
                                "Beginning process stall for 5 minutes."
                            )

                            # Archive comment to 'engaged_comments'.
                            engaged_comments.append(comment)

                            # Stall process.
                            time.sleep(300)

                            # Redefine the GCP parameters.
                            self.define_gcp_parameters()

                # Catch exception for invalid input to the GCP API.
                except google.api_core.exceptions.InvalidArgument:

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

                    print(
                        "Encountered Reddit Comment creation limit.",
                        "Adding Comment to 'engaged_comments' and continuing process.",
                        "\n",
                        "-" * 30,
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


            # After end of loop, check if the time since the beginning of the process surpasses the given limit.
            if time.time() > timeout:

                # Output status.
                print("\n", "Reached time-limit; completed process.", "\n")

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
                time.sleep(300)


        return self


    def generate_dialogflow_response(self, text_body):
        """

        :return:
        """

        # Define the text input container for DialogFlow.
        text_input = dialogflow.types.TextInput(
            text= text_body,
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
