from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Literal, Optional, Type

from termcolor import colored
from src.prompts import SystemPrompt, Prompt
from models.ml import LlmModel
from models.llm import ResultsMetadata
from models.agents import AgentSchema
import networkx as nx
import json

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
    role: Literal['user', 'assistant', 'connection']
    input_schema: type[AgentSchema]
    output_schema: type[AgentSchema]
    processor: Optional[AgentProcessor] = None
    graph: Optional[nx.DiGraph] = None
    metadata: list[Any] = field(default_factory=list)

    def __post_init__(self):
        self.connection_nodes: list[Agent] = []
        if self.graph is not None:
            self.graph.add_node(
                self.name, 
                #input=self.input_schema, 
                #output=self.output_schema
            )

    def connect_node(self, agent: 'Agent'):
        self.connection_nodes.append(agent)
        if self.graph is not None:
            self.graph.add_edge(
                self.name, 
                agent.name, 
                #input=self.input_schema
            )

    def node_choice(self, result: Prompt, input: Prompt, debug: bool = False):
        if not self.output_schema.branch():
            assert len(self.connection_nodes) <= 1
            return self.connection_nodes[0].run(input=result, debug=debug)
        
        selected_node_dict = {k: v for k, v in result.content.items() if v}
        assert len(selected_node_dict) == 1
        selected_node_name = list(selected_node_dict.keys())[0]

        for connection_node in self.connection_nodes:
            if connection_node.name == selected_node_name:
                return connection_node.run(input=input, debug=debug)
        raise Exception('No connection node found')

    def llm_response(
            self, input: Prompt,
            history: list[Prompt] = [],
            debug: bool = False
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

    def run(
            self, input: Prompt, 
            history: list[Prompt] = [], 
            debug: bool = False
        ) -> Prompt:

        args = asdict(self) | {
            'input': input, 
            'history': history, 
            'debug': debug
        }

        # print(colored(json.dumps(input.content, indent=4, ensure_ascii=False), color='yellow', attrs=['bold']))
        # print(colored(json.dumps(self.input_schema.model_json_schema(), indent=4, ensure_ascii=False), color='green', attrs=['bold']))
        assert self.input_schema(**input.content)

        output = None
        if self.llm_model is not None:
            assert self.system_prompt is not None
            output = self.llm_response(
                input=input,
                history=history,
                debug=debug
            )
            assert self.system_prompt.output_schema(**output)
        
        if self.processor is not None:
            output = self.processor.process(**args | {'llm_output': output})

        if output is None:
            raise Exception('No output')
        
        assert self.output_schema(**output)

        result = Prompt(
            content=output,
            role=self.role
        )
        
        if debug:
            debug_colors = {
                "system": "yellow",
                "assistant": "green",
                "user": "blue",
                "connection": "grey",
            }
            print(f"\n\n{colored(f'[CHAT] - {self.name}', color='red', attrs=['bold'])}")
            print(f"{colored(f'[{result.role}]:', color=debug_colors[result.role], attrs=['bold'])}") # type: ignore
            print(f"{colored(result.content_format(), debug_colors[result.role])}") # type: ignore


        return result if not self.connection_nodes else self.node_choice(result, input, debug)

