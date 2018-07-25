from dialogflow_agent import DF_Agent



# Define Reddit account parameters.
reddit_parameters = (
        "zO1z52xZNtdxrA",
        "VbAzyOfUcj-94a71j8V_6lUTyAM",
        "An observer of Subreddit Streams",
        "ssa1G",
        "subreddit.stream.agent.1.password"
)


DialogFlow_Agent = DF_Agent(
        reddit_parameters=reddit_parameters,
        submission="8gm3un",
)


DialogFlow_Agent.run_main_process(
        engage= True,
        time_limiter= 7200
)

# DialogFlow_Agent.print_subm_comments()
