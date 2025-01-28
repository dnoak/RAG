from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Literal, Optional, Type
from src.prompts import SystemPrompt, Prompt
from models.ml import LlmModel
from models.llm import ResultsMetadata
from models.agents import AgentSchema
import networkx as nx
import json
# @dataclass
# class Agent:
#     name: str
#     llm_model: LlmModel
#     pipeline: list[SystemPrompt]
    
#     def run(
#             self, input: Prompt, 
#             history: list[Prompt] = [], 
#             debug: bool = False
#         ) -> list[Prompt]:
#         responses = [input]
#         for system_prompt in self.pipeline:
#             assert system_prompt.input_schema(**responses[-1].content)
#             response = self.llm_model.generate(
#                 system_prompt=system_prompt,
#                 input=responses[-1],
#                 history=history,
#                 debug=debug
#             )
#             responses.append(Prompt(
#                 content=json.loads(response.output_text), 
#                 role='connection'
#             ))
#         responses[-1].role = 'assistant'
#         return responses

# @dataclass(kw_only=True)
# class _AgentProcessor:
#     pre_processor: Optional[Callable] = lambda x: x
#     pre_processor_schema: Optional[Type[AgentSchema]]
#     post_processor: Optional[Callable] = lambda x: x
#     post_processor_schema: Optional[Type[AgentSchema]]

# @dataclass(kw_only=True)
# class _Agent:
#     name: str
#     system_prompt: SystemPrompt
#     role: Literal['user', 'assistant', 'connection']
#     processor: _AgentProcessor
#     # input_processor: Callable = lambda x: x
#     # output_processor: Callable = lambda x: x
#     # output_processor_schema: Type[AgentSchema]

#     # criar external_action (ou algo assim) como funçao de processamento

#     llm_model: LlmModel

#     def __post_init__(self):
#         self.connection_nodes: list[Agent] = []

#     def connect_node(self, agent: 'Agent'):
#         self.connection_nodes.append(agent)

#     def node_choice(self, result: Prompt, input: Prompt, debug: bool = False):
#         if not self.system_prompt.output_schema.branch():
#             assert len(self.connection_nodes) <= 1
#             return self.connection_nodes[0].run(input=result, debug=debug)
        
#         selected_node_dict = {k: v for k, v in result.content.items() if v}
#         assert len(selected_node_dict) == 1
#         selected_node_name = list(selected_node_dict.keys())[0]

#         for connection_node in self.connection_nodes:
#             if connection_node.name == selected_node_name:
#                 return connection_node.run(input=input, debug=debug)
#         raise Exception('No connection node found')

#     def run(
#             self, input: Prompt, 
#             history: list[Prompt] = [], 
#             debug: bool = False
#         ) -> Prompt:
#         input.content = self.input_processor(input.content)
        
#         assert self.system_prompt.input_schema(**input.content)
        
#         response = self.llm_model.generate(
#             system_prompt=self.system_prompt,
#             input=input,
#             history=history,
#             debug=debug
#         )

#         dict_output = json.loads(response.output_text)
#         processed = self.output_processor(dict_output) if self.connection_nodes else dict_output

#         assert self.system_prompt.output_schema(**processed)

#         result = Prompt(
#             content=processed,
#             role=self.role
#         )

#         return result if not self.connection_nodes else self.node_choice(result, input, debug)

@dataclass(kw_only=True)
class AgentProcessor(ABC):
    metadata: list[Any] = field(default_factory=list)

    # def llm_response(self, *args, **kwargs) -> dict:
    #     response = kwargs['llm_model'].generate(
    #         system_prompt=kwargs['system_prompt'],
    #         input=kwargs['input'],
    #         history=kwargs['history'],
    #         debug=kwargs['debug']
    #     )
    #     self.metadata.append(response)
    #     return json.loads(response.output_text)

    # @abstractmethod
    # def pre_process(self, *args, **kwargs) -> dict:
    #     return kwargs['input'].content
    
    @abstractmethod
    def process(self, *args, **kwargs) -> dict:
        ...
    
    # @abstractmethod
    # def post_process(self, *args, **kwargs) -> dict:
    #     return kwargs['output']


# @dataclass(kw_only=True)
# class LlmAgentProcessor(AgentProcessor):
#     # role: Literal['user', 'assistant', 'connection'] = 'assistant'
#     # metadata: list[ResultsMetadata] = field(default_factory=list)

#     # def pre_process(self, input: dict) -> dict:
#     #     return input
    
#     def process(self, *args, **kwargs) -> dict:
#         response = kwargs['llm_model'].generate(
#             system_prompt=kwargs['system_prompt'],
#             input=kwargs['input'],
#             history=kwargs['history'],
#             debug=kwargs['debug']
#         )
#         self.metadata.append(response)
#         return json.loads(response.output_text)

#     # def post_process(self, output: dict) -> dict:
#     #     return output


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

    # input_processor: Callable = lambda x: x
    # output_processor: Callable = lambda x: x
    # output_processor_schema: Type[AgentSchema]

    # criar external_action (ou algo assim) como funçao de processamento

    def __post_init__(self):
        self.connection_nodes: list[Agent] = []
        # self.graph = nx.DiGraph()
        if self.graph is not None:
            self.graph.add_node(self.name)

    def connect_node(self, agent: 'Agent'):
        self.connection_nodes.append(agent)
        if self.graph is not None:
            self.graph.add_edge(self.name, agent.name)

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

        return result if not self.connection_nodes else self.node_choice(result, input, debug)

