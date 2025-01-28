from src.prompts import Prompt
from src.agent import Agent
from agents.emoji_shark import SHARK_SYS_PROMPT, SHARK_EMOJI
from src.llm.gpt import GptLlmApi
import matplotlib.pyplot as plt
import networkx as nx
from agents.shark.classifier import shark_classifier
from agents.shark.specialist import shark_specialist_unformatted
from agents.shark.emojifier import shark_emojifier
from agents.shark.db_formatter import shark_db_formatter
from agents.shark.input_loop import shark_input_loop

G = nx.DiGraph()

loop = shark_input_loop(G)
classifier = shark_classifier(G)
specialist = shark_specialist_unformatted(G)
emojifier = shark_emojifier(G)
db_formatter = shark_db_formatter(G)


# graph #

loop.connect_node(classifier)

classifier.connect_node(specialist)
classifier.connect_node(db_formatter)

db_formatter.connect_node(specialist)

specialist.connect_node(emojifier)

emojifier.connect_node(loop)


# plt.figure(figsize=(10, 7))
# nx.draw(G, with_labels=True, node_color="lightblue")
# plt.show()


loop.run(
    input=Prompt(
        content={'formatted_output': 'Fale o nome do autor que descobriu o Squatina aculeata'},
        role='user'
    ), 
    debug=True
)








# from agents.shark_2 import (
#     SHARK_CHOICE as choice, 
#     SHARK as shark, 
#     SHARK_EMOJIFIER as emoji, 
#     SHARK_QUERY as query,
#     GLOBAL_GRAPH as graph
# )

# choice.connect_node(shark)
# choice.connect_node(query)

# shark.connect_node(emoji)
# emoji.connect_node(choice)

# query.connect_node(shark)


# plt.figure(figsize=(10, 7))
# nx.draw(graph, with_labels=True, node_color="lightblue")
# plt.show()


# r = choice.run(
#     input=Prompt(
#         # content={'input': 'Fale o nome do autor que descobriu o Squatina aculeata'},
#         content={},
#         role='user'
#     ), 
#     debug=True
# )
