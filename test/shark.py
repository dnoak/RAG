import json
import math
import typing
from src.prompts import Prompt
from src.agent import Agent
from src.llm.gpt import GptLlmApi
import matplotlib.pyplot as plt
import networkx as nx
from agents.shark.input_loop import shark_input_loop
from agents.shark.classifier import shark_classifier
from agents.shark.query_formatter import shark_query_formatter
from agents.shark.specialist import shark_specialist
from agents.shark.wiki import shark_wikipedia
from agents.shark.emojifier import shark_emojifier
from agents.shark.query_responder import shark_query_responder

G = nx.DiGraph()

loop = shark_input_loop(G)
classifier = shark_classifier(G)
specialist = shark_specialist(G)
query_formatter = shark_query_formatter(G)
wiki = shark_wikipedia(G)
query_responder = shark_query_responder(G)
emojifier = shark_emojifier(G)




loop.connect_node(classifier)

classifier.connect_node(specialist)
classifier.connect_node(query_formatter)
classifier.connect_node(wiki)

query_formatter.connect_node(query_responder)
query_responder.connect_node(emojifier)
wiki.connect_node(emojifier)

specialist.connect_node(emojifier)

emojifier.connect_node(loop)


plt.figure(figsize=(10, 7))
g_pos = nx.circular_layout(G)
color_map = ['tomato' if node == 'shark_input_loop' else 'lightblue' for node in G]
nx.draw_networkx(
    G=G, pos=g_pos, with_labels=True,
    arrows=True, arrowsize=30,
    node_size=3000, font_size=10, 
    node_color=color_map,# labels=labels,
    connectionstyle='arc3,rad=0.2',

)
plt.show()

loop.compile()
classifier.compile()
specialist.compile()
query_formatter.compile()
wiki.compile()
query_responder.compile()
emojifier.compile()





print(loop.run(
    input=Prompt(
        contents=[{'loop_output': 'Fale o nome do autor que descobriu o Squatina aculeata'}],
        role='user'
    ), 
))

