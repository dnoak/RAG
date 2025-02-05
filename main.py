import json
import math
import typing
from src.prompts import Prompt
from src.agent import Agent
from src.llm.gpt import GptLlmApi
import matplotlib.pyplot as plt
import networkx as nx
from agents.democracy import (
    voter,
    
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
