from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Literal, Optional, Type
from termcolor import colored
from src.prompts import SystemPrompt, Prompt
from models.ml import LlmModel
from models.llm import ResultsMetadata
from models.agents import AgentSchema, Classifier, Responder
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
    role: Literal['user', 'assistant', 'user:connection']
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
            )
    
    def _check_agents_io(self, agent: 'Agent'):
        if self.output_schema.__annotations__ == agent.input_schema.__annotations__:
            return
        stringfy = lambda d: {k: stringfy(v) if isinstance(v, dict) else str(v) for k, v in d.items()}
        schema_out = json.dumps(stringfy(self.output_schema.__annotations__), indent=4, ensure_ascii=False)
        schema_in = json.dumps(stringfy(agent.input_schema.__annotations__), indent=4, ensure_ascii=False)
        exception = colored(
            f"\n{'❌ '*20}\nConnected agent INPUT must have the self agent OUTPUT schema",
            color='yellow', attrs=['bold']
        )
        exception += colored(f"\n[Output]: {self.name}", color='red', attrs=['bold'])
        exception += colored(f"\n{schema_out}", color='red')
        exception += colored(f"\n[Input]: {agent.name}", color='green', attrs=['bold'])
        exception += colored(f"\n{schema_in}", color='green')
        raise Exception(exception)
    
    def connect_node(self, agent: 'Agent'):
        self._check_agents_io(agent)
        self.connection_nodes.append(agent)
        if self.graph is not None:
            self.graph.add_edge(
                self.name, 
                agent.name, 
            )
    
    def node_choice(self, result: Prompt, input: Prompt, debug: bool = False):
        if self.output_schema.connection_type() == Responder.connection_type():
            return self.connection_nodes[0].run(input=result, debug=debug)
        if self.output_schema.connection_type() == Classifier.connection_type():
            selected_node = result.content[self.output_schema.connection_type()]
            for connection_node in self.connection_nodes:
                if connection_node.name == selected_node:
                    return connection_node.run(input=result, debug=debug)
            raise Exception('No connection node found')
        raise NotImplementedError(f'Connection type {self.output_schema.connection_type()} not implemented')

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

        assert self.input_schema(**input.content)

        output = None
        if self.llm_model is not None:
            assert self.system_prompt is not None
            output = self.llm_response(
                input=input,
                history=history,
                debug=False
            )
            assert self.system_prompt.output_schema(**output)
        
        if self.processor is not None:
            args = asdict(self) | {
                'input': input, 
                'history': history, 
                'debug': debug
            }
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
                "user:connection": "grey",
            }
            print(f"\n\n{colored(f'[CHAT] - {self.name}', color='red', attrs=['bold'])}")
            print(f"{colored(f'[{result.role}]:', color=debug_colors[result.role], attrs=['bold'])}") # type: ignore
            print(f"{colored(result.content_format(show_connection_type=True), debug_colors[result.role])}") # type: ignore

        return result if not self.connection_nodes else self.node_choice(result, input, debug)

