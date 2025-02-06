from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
import functools
import threading
import time
from typing import Any, Callable, Literal, Optional, Type
from termcolor import colored
from src.prompts import SystemPrompt, Prompt
from models.ml import LlmModel
from models.llm import ResultsMetadata
from models.agents import AgentSchema, Classifier, Replier, Replicator
import networkx as nx
import json

@dataclass(kw_only=True)
class AgentValidationErrors:
    @staticmethod
    def nodes_io_mismatch(_self: 'Agent', agent: 'Agent'):
        exception = colored(
            f"\n{'❌ '*24}\n{agent.name} INPUTs schemas must have the {_self.name} OUTPUT schema",
            color='yellow', attrs=['bold']
        )
        exception += colored(f"\n[Output]: Agent {_self.name}", color='red', attrs=['bold'])
        dumped = json.dumps(_self.output_schema.annotations(), indent=4, ensure_ascii=False)
        exception += colored(f"\n{dumped}", color='red')
        exception += colored(f"\n[Inputs]: Agent {agent.name}", color='green', attrs=['bold'])
        dumped = json.dumps(
            [i.annotations() for i in agent.connections_input_schema_queue], 
            indent=4, ensure_ascii=False)
        exception += colored(f"\n{dumped}", color='green')
        raise Exception(exception)
    
    @staticmethod
    def pending_connections(_self: 'Agent'):
        exception = colored(
            f"\n{'❌ '*12}\nConnections not completed in agent {_self.name}",
            color='yellow', attrs=['bold']
        )
        exception += colored(f"\n[Pending connections]: agent {_self.name}", color='red', attrs=['bold'])
        dumped = json.dumps(
            [i.annotations() for i in _self.connections_input_schema_queue], 
            indent=4, ensure_ascii=False)
        exception += colored(f"\n{dumped}", color='red')
        raise Exception(exception)
    
    @staticmethod
    def no_schema_found(_self: 'Agent', input: Prompt):
        exception = colored(f'\nNo input schema found for agent {_self.name}', color='yellow', attrs=['bold'])
        dumped = json.dumps(input.contents, indent=4, ensure_ascii=False)
        exception += colored(f"\n[Received Input]:", color='red', attrs=['bold'])
        exception += colored(f"\n{dumped}", color='red')
        dumped = json.dumps(
            [i.annotations() for i in _self.input_schema_queue], 
            indent=4, ensure_ascii=False)
        exception += colored(f"\n[Input Schemas]:", color='green', attrs=['bold'])
        exception += colored(f"\n{dumped}", color='green')
        raise Exception(exception)

    
@dataclass(kw_only=True)
class AgentProcessor(ABC):
    metadata: list[Any] = field(default_factory=list)

    @abstractmethod
    def process(self, *args, **kwargs) -> dict:
        ...

@dataclass(kw_only=True)
class Agent:
    name: str
    llm_model: Optional[LlmModel]
    system_prompt: Optional[SystemPrompt]
    role: Literal['user', 'assistant', 'user:connection']
    input_schemas: list[type[AgentSchema]]
    output_schema: type[AgentSchema]
    processor: Optional[AgentProcessor] = None
    graph: Optional[nx.DiGraph] = None
    metadata: list[Any] = field(default_factory=list)
    debug: dict[Literal['output', 'llm'], bool] = field(
        default_factory=lambda: {'output': False, 'llm': False}
    )

    def __post_init__(self):
        self.locker = threading.Lock()
        self.output_nodes: list[Agent] = []
        self._set_queues()
        if self.graph is not None:
            self.graph.add_node(self.name)
        threading.Thread(target=self._start_loop).start()

    def _set_queues(self):
        self.connections_input_schema_queue: list[type[AgentSchema]] = [
            i for i in self.input_schemas
        ]
        self.input_schema_queue: list[type[AgentSchema]] = [
            i for i in self.input_schemas
        ]
        self.inputs_args_queue: list[dict] = []

    def _nodes_io(self, agent: 'Agent'):
        for index, input_schema in enumerate(agent.input_schemas): 
            if input_schema.annotations() == self.output_schema.annotations():
                if agent.connections_input_schema_queue:
                    return agent.connections_input_schema_queue.pop(index)
                return []
        AgentValidationErrors.nodes_io_mismatch(_self=self, agent=agent)

    def _wait_for_inputs(self) -> tuple[Prompt, list[Prompt]]:
        while len(self.inputs_args_queue) < len(self.input_schemas):
            time.sleep(0.1)
        args = sorted(self.inputs_args_queue, key=lambda x: x['index'])
        contents = sum([i['input'].contents for i in args], [])
        roles = [i['input'].role for i in args]
        histories = [i['history'] for i in args]
        assert all(role == roles[0] for role in roles)
        assert all(history == histories[0] for history in histories)
        return Prompt(contents=contents, role=roles[0]), histories[0]
    
    def _node_choice(self, result: Prompt, history: list[Prompt]):
        if self.output_schema.connection_type() == Replier.connection_type():
            return self.output_nodes[0].run(input=result, history=history)
        elif self.output_schema.connection_type() == Classifier.connection_type():
            selected_node = result.contents[0][self.output_schema.connection_type()]
            for output_node in self.output_nodes:
                if output_node.name == selected_node:
                    return output_node.run(input=result, history=history)
            raise Exception('No connection node found')
        elif self.output_schema.connection_type() == Replicator.connection_type():
            return [
                output_node.run(input=result, history=history)
                for output_node in self.output_nodes
            ]
        else:
            raise NotImplementedError(
                f'Connection type {self.output_schema.connection_type()} not implemented'
            )

    def _start_loop(self):
        while True:
            self.start()
            self._set_queues()
    
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

    def compile(self, closed_loop=True):
        if self.connections_input_schema_queue and closed_loop:
            AgentValidationErrors.pending_connections(_self=self)
        return self

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
            if result.role != 'user':
                return
            print(f"\n\n{colored(f'[CHAT] - {self.name}', color='red', attrs=['bold'])}")
            print(f"{colored(f'[{result.role}]:', color=debug_colors[result.role], attrs=['bold'])}") # type: ignore
            print(f"{colored(result.content_format(show_connection_type=True), debug_colors[result.role])}") # type: ignore

        return result if not self.output_nodes else self._node_choice(result, history)

    def connect_node(self, agent: 'Agent'):
        self._nodes_io(agent=agent)
        self.output_nodes.append(agent)
        if self.graph is not None:
            self.graph.add_edge(
                self.name,
                agent.name,
            )
    
    def run(self, input: Prompt, history: list[Prompt] = []):
        with self.locker:
            for index, input_squema in enumerate(self.input_schema_queue):
                for content in input.contents:
                    try:
                        input_squema(**content)
                        self.inputs_args_queue.append(
                            {'input': input, 'history': history, 'index': index}
                        )
                        return
                    except:
                        continue
            AgentValidationErrors.no_schema_found(_self=self, input=input)



if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import random

    G = nx.DiGraph()

    class ERROR_input(Responder):
        error_input: str
    
    class A_input(Responder):
        abc_input: str
    class A_output(Responder):
        a_output: str
    class A_prompt(SystemPrompt):
        background: str = 'você escolhe aleatoriamente um dos resultados e responde em JSON'
        steps: list[str] = []
        output_schema: Type[A_output]
    a = Agent(
        name='a', llm_model=None, system_prompt=None, role='user',
        input_schemas=[A_input], output_schema=A_output, graph=G
    )

    class B_input(Responder):
        abc_input: str
    class B_output(Responder):
        b_output: str
    b = Agent(
        name='b', llm_model=None, system_prompt=None, role='user',
        input_schemas=[B_input], output_schema=B_output, graph=G
    )

    class C_input(Responder):
        abc_input: str
    class C_output(Responder):
        c_output: str
    c = Agent(
        name='c', llm_model=None, system_prompt=None, role='user',
        input_schemas=[B_input], output_schema=C_output, graph=G
    )

    class D_output(Responder):
        abc_input: str
    d = Agent(
        name='d', llm_model=None, system_prompt=None, role='user',
        input_schemas=[A_output, B_output, C_output], output_schema=D_output, graph=G
    )


    a.connect_node(d)
    b.connect_node(d)
    c.connect_node(d)

    d.connect_node(a)
    d.connect_node(b)
    d.connect_node(c)

    a.compile()
    b.compile()
    c.compile()
    d.compile()


    # input()
    for i in range(20):
        input()
        choice = random.choice([
            {'a_output': 'resposta a'},
            {'b_output': 'resposta b'},
            {'c_output': 'resposta c'},
        ])
        print(choice)

        d.run(
            input=Prompt(contents=[choice], role='user'),
        )

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