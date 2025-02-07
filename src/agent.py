from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
import functools
import threading
import time
from typing import Any, Literal, Optional, Type
from termcolor import colored
from src.prompts import SystemPrompt, Prompt
from models.ml import LlmModel
from models.agents import AgentSchema, AgentProcessor, Classifier, Replier, Replicator
import random
import json
import graphviz

@dataclass(kw_only=True)
class Agent:
    name: str
    llm_model: Optional[LlmModel]
    system_prompt: Optional[SystemPrompt]
    role: Literal['user', 'assistant', 'user:connection']
    output_schema: type[AgentSchema]
    processor: Optional[AgentProcessor] = None
    graph: Optional[graphviz.Digraph] = None # type: ignore
    metadata: list[Any] = field(default_factory=list)
    debug: dict[Literal['output', 'llm'], bool] = field(
        default_factory=lambda: {'output': False, 'llm': False}
    )

    def __post_init__(self):
        self.running = False
        self.locker = threading.Lock()
        self.input_nodes: list[Agent] = []
        self.output_nodes: list[Agent | None] = [None]
        self.inputs_args_queue: list[dict] = []
        if self.graph is not None:
            self.graph.node(self.name, label=self.name)

    def _full_input_args_queue(self):
        if len(self.inputs_args_queue) == 0:
            'No input was provided'
            return False
        if len(self.input_nodes) == 0:
            'In case of starting nodes where there is no input'
            return True
        return len(self.inputs_args_queue) == len(self.input_nodes)

    def _wait_for_inputs(self) -> tuple[Prompt, list[Prompt]]:
        while not self._full_input_args_queue():
            time.sleep(0.1)

        contents = sum([i['input'].contents for i in self.inputs_args_queue], [])
        roles = [i['input'].role for i in self.inputs_args_queue]
        histories = [i['history'] for i in self.inputs_args_queue]
        assert all(role == roles[0] for role in roles)
        assert all(history == histories[0] for history in histories)
        return Prompt(contents=contents, role=roles[0]), histories[0]
    
    def _node_choice(self, result: Prompt, history: list[Prompt]):
        if self.output_nodes[0] is None:
            assert len(self.output_nodes) == 1
            return result
        
        if self.output_schema.connection_type() == Replier.connection_type():
            assert len(self.output_nodes) == 1
            return self.output_nodes[0].run(input=result, history=history)
        
        elif self.output_schema.connection_type() == Classifier.connection_type():
            selected_node = result.contents[0][self.output_schema.connection_type()]
            for output_node in self.output_nodes:
                assert output_node is not None
                if output_node.name == selected_node:
                    return output_node.run(input=result, history=history)
            raise Exception(colored(
                f'\nNo connection node found in classifier output for agent {self.name}',
                color='yellow', attrs=['bold']
            ))
        
        elif self.output_schema.connection_type() == Replicator.connection_type():
            for output_node in self.output_nodes:
                assert output_node is not None
                output_node.run(input=result, history=history)

    def _start_loop(self):
        while True:
            self.start()
            with self.locker:
                self.inputs_args_queue.clear()
    
    def llm_response(
            self, input: Prompt, history: list[Prompt], debug: bool
        ) -> dict:
        if self.llm_model is None:
            return {}
        response = self.llm_model.generate(
            system_prompt=self.system_prompt,
            input=input,
            history=history,
            debug=debug
        )
        self.metadata.append(response)
        return json.loads(response.output_text)

    def start(self):
        input, history = self._wait_for_inputs()
        output = None
        if self.llm_model:
            assert self.system_prompt is not None
            output = self.llm_response(
                input=input,
                history=history,
                debug=True#self.debug['llm']
            )
            assert self.system_prompt.output_schema(**output)
        if self.processor:
            args = asdict(self) | {
                'input': input, 
                'history': history, 
            }
            output = self.processor.process(**args | {'llm_output': output})
        
        if output is None:
            raise Exception(colored(
                f'\nAgent {self.name} must have at least a `llm_model` or a `processor` defined',
                color='red', attrs=['bold'])
            )
        assert self.output_schema(**output)

        result = Prompt(
            contents=[output],
            role=self.role
        )
        
        if self.debug['output']:
            debug_colors = {
                "system": "yellow",
                "assistant": "green",
                "user": "blue",
                "user:connection": "grey",
            }
            # if result.role != 'user':
            #     return
            print(f"\n\n{colored(f'[CHAT] - {self.name}', color='red', attrs=['bold'])}")
            print(f"{colored(f'[{result.role}]:', color=debug_colors[result.role], attrs=['bold'])}") # type: ignore
            print(f"{colored(result.content_format(show_connection_type=True), debug_colors[result.role])}") # type: ignore

        return result if not self.output_nodes else self._node_choice(result, history)

    def connect_node(self, agent: 'Agent'):
        self.output_nodes = list(filter(lambda x: x is not None, self.output_nodes))
        self.output_nodes.append(agent)
        agent.input_nodes.append(self)
        
        if self.graph is not None:
            colors = [
                'lime', 'tomato', 'lightblue', 'lightcoral', 'lightsalmon', 'palegreen',
                'darkgreen', 'darkviolet', 'darkmagenta', 'orangered', 'gold',
                'deepskyblue', 'crimson', 'mediumvioletred', 'chocolate', 'royalblue'
            ]
            choice = random.choice(colors)
            self.graph.edge(
                tail_name=self.name, 
                head_name=agent.name, 
                label='\n'.join(self.output_schema.annotations().keys()),
                _attributes={'color': choice, 'fontcolor': choice}
            ) 
    
    def run(self, input: Prompt, history: list[Prompt] = []):
        with self.locker:
            if not self.running:
                threading.Thread(target=self._start_loop).start()
                self.running = True
            self.inputs_args_queue.append(
                {'input': input, 'history': history}
            )

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import random

    G = nx.DiGraph()

    class Processor(Replier):
        def process(self, *args, **kwargs) -> dict:
            return kwargs['input'].contents[0]
    
    class A_input(Replier):
        abc_input: str
    class A_output(Replier):
        a_output: str
    class A_prompt(SystemPrompt):
        background: str = 'você escolhe aleatoriamente um dos resultados e responde em JSON'
        steps: list[str] = []
        output_schema: Type[A_output]
    a = Agent(
        name='a', llm_model=None, system_prompt=None, 
        role='user', output_schema=A_output, graph=G,
    )

    class B_input(Replier):
        abc_input: str
    class B_output(Replier):
        b_output: str
    b = Agent(
        name='b', llm_model=None, system_prompt=None, 
        role='user', output_schema=B_output, graph=G
    )

    class C_input(Replier):
        abc_input: str
    class C_output(Replier):
        c_output: str
    c = Agent(
        name='c', llm_model=None, system_prompt=None, 
        role='user', output_schema=C_output, graph=G
    )

    class D_output(Replier):
        abc_input: str
    d = Agent(
        name='d', llm_model=None, system_prompt=None,
        role='user', output_schema=D_output, graph=G, debug={'output': True}
    )


    a.connect_node(d)
    b.connect_node(d)
    c.connect_node(d)

    d.connect_node(a)
    d.connect_node(b)
    d.connect_node(c)


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


    choice = random.choice([
        {'a_output': 'resposta a'},
        {'b_output': 'resposta b'},
        {'c_output': 'resposta c'},
    ])
    print(choice)
    a.run(
        input=Prompt(contents=[choice], role='user'),
    )
    b.run(
        input=Prompt(contents=[choice], role='user'),
    )
    c.run(
        input=Prompt(contents=[choice], role='user'),
    )