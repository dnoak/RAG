import json
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


# graph #
loop.connect_node(classifier)

classifier.connect_node(specialist)
classifier.connect_node(query_formatter)
classifier.connect_node(wiki)

query_formatter.connect_node(query_responder)
query_responder.connect_node(emojifier)

specialist.connect_node(emojifier)

emojifier.connect_node(loop)

wiki.connect_node(loop)


def io_formatter(output_schema):
    type_hints = typing.get_type_hints(output_schema)
    output_dict = {}
    for type_key, type_value in type_hints.items():
        if isinstance(type_value, type):
            type_value = type_value.__name__
        else:
            type_value = str(type_value).replace('typing.', '')
        output_dict[type_key] = f"{type_value}"
    return json.dumps(output_dict, indent=4, ensure_ascii=False)


# plt.figure(figsize=(10, 7))
# g_pos = nx.spring_layout(G)
# color_map = ['tomato' if node == 'shark_input_loop' else 'lightblue' for node in G]
# # labels = {
# #     node: f'{node}\ninput:\n{io_formatter(data["input"])}\noutput:\n{io_formatter(data["output"])}'
# #     for node, data in G.nodes(data=True)
# # }
# nx.draw_networkx(
#     G=G, pos=g_pos, with_labels=True,
#     node_size=6000, font_size=10, 
#     node_color=color_map,# labels=labels,
# )
plt.show()


print(loop.run(
    input=Prompt(
        content={'loop_output': 'Fale o nome do autor que descobriu o Squatina aculeata'},
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
