import json
import math
import time
import typing
from src.prompts import Prompt
from agent import Agent
from src.llm.gpt import GptLlmApi
import matplotlib.pyplot as plt
import networkx as nx
from agents.democracy.voter import voter_fn
from agents.democracy.candidate import candidate_fn
from agents.democracy.election import election_fn

G = nx.DiGraph()

candidate_0 = candidate_fn(name='candidate_0', n_inputs=1, graph=G)
candidate_1 = candidate_fn(name='candidate_1', n_inputs=1, graph=G)

voter_0 = voter_fn(name='voter_0', n_inputs=2, graph=G)
voter_1 = voter_fn(name='voter_1', n_inputs=2, graph=G)
voter_2 = voter_fn(name='voter_2', n_inputs=2, graph=G)

election = election_fn(name='election', n_inputs=3, graph=G)


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

# election.connect_node(candidate_0)
# election.connect_node(candidate_1)


# compile
candidate_0.compile(closed_loop=False)
candidate_1.compile(closed_loop=False)
voter_0.compile()
voter_1.compile()
voter_2.compile()
election.compile()


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



candidate_0.run(input=Prompt(contents=[{"winner": "-"}], role='user'))
candidate_1.run(input=Prompt(contents=[{"winner": "-"}], role='user'))