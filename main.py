from src.prompts import Prompt
from src.agent import Agent
from src.llm.gpt import GptLlmApi
import matplotlib.pyplot as plt
import networkx as nx
from agents.shark.input_loop import shark_input_loop
from agents.shark.classifier import shark_classifier
from agents.shark.specialist import shark_specialist_unformatted
from agents.shark.emojifier import shark_emojifier
from agents.shark.query_response import shark_query_responder
from agents.shark.query_formatter import shark_query_formatter

G = nx.DiGraph()

loop = shark_input_loop(G) 
classifier = shark_classifier(G)
specialist = shark_specialist_unformatted(G)
query_formatter = shark_query_formatter(G)
query_responder = shark_query_responder(G)
emojifier = shark_emojifier(G)


# graph #
loop.connect_node(classifier)

classifier.connect_node(specialist)
classifier.connect_node(query_formatter)

query_formatter.connect_node(query_responder)
query_responder.connect_node(emojifier)

specialist.connect_node(emojifier)

emojifier.connect_node(loop)


# plt.figure(figsize=(10, 7))
# g_pos = nx.spring_layout(G)
# color_map = ['tomato' if node == 'shark_input_loop' else 'lightblue' for node in G]
# nx.draw_networkx(
#     G=G, pos=g_pos, with_labels=True,
#     node_size=6000, font_size=10, 
#     node_color=color_map
# )
# plt.show()


print(loop.run(
    input=Prompt(
        content={'formatted_output': 'Fale o nome do autor que descobriu o Squatina aculeata'},
        role='user'
    ), 
    debug=True
))








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
