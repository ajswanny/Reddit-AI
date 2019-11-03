# Reddit AI
The source code for the research project in which a collection of Python programs were used to identify levels of awareness about the hurrican disaster in Puerto Rico – which occurred in September 2017 – and attempt to increase them via a conversational agent (a Reddit bot).

#### Project Abstract
*On September 20, 2017 hurricane “Maria” made landfall in the U.S. territory of Puerto Rico. The hurricane’s devastation maintained its impact for several months after September 20 and still does. The lack of adequate assistance given to the government of Puerto Rico for hurricane relief became concerning; efforts to denounce these realities or contribute to benefaction did not appear sufficient during the months immediately after the storm. This project aimed at raising the awareness of this situation in Puerto Rico by using a weak-AI agent charged with the task of spreading details about the situation. The task was carried out through three different experimental approaches for creating contents about the humanitarian crisis in the form of Reddit submissions and comments. These approaches showed good potential but stopped short of showing the expected results as desired, thus suggesting migration to other online social media platforms such as Facebook and Twitter.*

#### Repo Content
This repository contains the source code for two of the last experiments in the project. The first experiment is not included in the source code separately, as it used the same classes that were implemented in the other experiments. This first experiment consisted of scanning Reddit randomly for posts, and submitting comments. The later experiments apply the bot to specific *subreddits* (a subreddit is a forum of the website within which posts focus on a specific topic, such as 'news' or 'politics').

##### Experiment 2
In this experiment, subreddit posts were scanned by our programs and post titles were matched for semantic similarity for the name of the problem topic –– the humanitarian crisis in Puerto Rico. This measure of semantic similarity was used to determine if a conversational agent would engage with comment-creators of a subreddit post. If so, the agent would submit a comment to the post in the hopes that human users would see it and continue a conversation.

##### Experiment 3
Taking things a step forward, a more powerful conversational agent was created using Google's [DialogFlow](https://dialogflow.com). In an attempt to reach out to individual commentors (instead of simply hoping that Reddit users would respond to the comments created in each post by the programs of *Experiment 2*), the agent would scan Subreddit posts and their comments, responding to individual comments that it determined had potential of conversation.

For more information, see the project [paper](paper.pdf).
