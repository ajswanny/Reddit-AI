"""
Created by Alexander Swanson on 8/3/18.
Copyright (c) 2018, Alexander Joseph Swanson Villares
alexjosephswanson@gmail.com
"""


# Import 'gcp_authentication' -- necessary for use of the GCP API.
from auth import gcp_authentication

from .dialog_flow_agent import DialogFlowAgent


def process__j_g_c__(submission_id: str):

    # Define a tuple of Reddit account parameters.
    reddit_parameters_1 = (
        "zO1z52xZNtdxrA",
        "VbAzyOfUcj-94a71j8V_6lUTyAM",
        "An observer of Subreddit Streams",
        "ssa1G",
        "subreddit.stream.agent.1.password"
    )

    # Define a DialogFlow agent for the provided Submission.
    dialog_flow_agent = DialogFlowAgent(
        reddit_parameters=reddit_parameters_1,
        submission_id=submission_id,
        gcp_project_id="reddit-ai-212207"
    )

    # Start the Agent's main function.
    dialog_flow_agent.run(
        engage=False,
        process_time_limit=7200
    )


# Run 'main'.
if __name__ == "__main__":
    process__j_g_c__(submission_id="8gm3un")
