#### A description of each of the elements within a Reddit AI Agent's main DataFrame

- utterance_content: The text submitted as a comment to a Submission by
the Reddit AI Agent.
    - Possible values:
        - NaN: the process was not commanded to engage in Submissions.
        - UNDEFINED: the process was commanded to engage in Submissions
        but the particular Submission did not gain engagement_clearance for
        engagement (meaning it was deemed not relevant enough to the
        problem topic).
        - \<utterance>: any possible utterance relative to the problem
        topic.