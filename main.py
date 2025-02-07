import json
import math
import time
import typing
from src.prompts import Prompt
from src.agent import Agent
from src.llm.gpt import GptLlmApi
import matplotlib.pyplot as plt
import networkx as nx
from agents.democracy.voter import voter_fn
from agents.democracy.candidate import candidate_fn
from agents.democracy.election import election_fn
import graphviz

G = graphviz.Digraph()

candidate_0 = candidate_fn('candidate_0', G)
candidate_1 = candidate_fn('candidate_1', G)
# candidate_2 = candidate_fn('candidate_2', G)

voter_0 = voter_fn('voter_0', G)
voter_1 = voter_fn('voter_1', G)
voter_2 = voter_fn('voter_2', G)

election = election_fn('election', G)


# graph

candidate_0.connect_node(voter_0)
candidate_1.connect_node(voter_0)

candidate_0.connect_node(voter_1)
candidate_1.connect_node(voter_1)

candidate_0.connect_node(voter_2)
candidate_1.connect_node(voter_2)

voter_0.connect_node(election)
voter_1.connect_node(election)
voter_2.connect_node(election)

# election.connect_node(    candidate_0)
# election.connect_node(candidate_1)

G.graph_attr['size'] = '100,100'
G.render('graph', view=True, format='png')
raise SystemExit()
# plt.figure(figsize=(10, 7))
# g_pos = nx.circular_layout(G)
# color_map = ['tomato' if node == 'shark_input_loop' else 'lightblue' for node in G]
# nx.draw_networkx(
#     G=G, pos=g_pos, with_labels=True,
#     arrows=True, arrowsize=30,
#     node_size=3000, font_size=10, 
#     node_color=color_map,# labels=labels,
#     connectionstyle='arc3,rad=0.2',
# )
# plt.show()


candidate_0.run(input=Prompt(contents=[{"winner": "-"}], role='user'))
candidate_1.run(input=Prompt(contents=[{"winner": "-"}], role='user'))
# candidate_2.run(input=Prompt(contents=[{"winner": "-"}], role='user'))