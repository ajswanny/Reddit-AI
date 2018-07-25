"""
Created by Alexander Swanson on 6/25/18.
Copyright (c) 2018, Alexander Joseph Swanson Villares
alexjosephswanson@gmail.com
"""


from Experiment3.src.python.DialogFlowAgent import DialogFlowAgent


def main(submission_id):

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
            submission=submission_id,
    )


    # Start the Agent's main function.
    dialog_flow_agent.run_main_process(
            engage=True,
            time_limiter=7200
    )


# Run 'main'.
if __name__ == '__main__': main("8gm3un")