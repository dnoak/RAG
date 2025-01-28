from dataclasses import dataclass
from typing import Callable, Literal
from src.prompts import SystemPrompt, Prompt
from models.ml import LlmModel
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


@dataclass(kw_only=True)
class Agent:
    name: str
    system_prompt: SystemPrompt
    role: Literal['user', 'assistant', 'connection']
    input_processor: Callable = lambda x: x
    output_processor: Callable = lambda x: x
    llm_model: LlmModel

    def __post_init__(self):
        self.connection_nodes: list[Agent] = []

    def connect_node(self, agent: 'Agent'):
        self.connection_nodes.append(agent)

    def node_choice(self, result: Prompt, input: Prompt, debug: bool = False):
        if not self.system_prompt.output_schema.branch():
            assert len(self.connection_nodes) <= 1
            return self.connection_nodes[0].run(input=result, debug=debug)
        
        selected_node_dict = {k: v for k, v in result.content.items() if v}
        assert len(selected_node_dict) == 1
        selected_node_name = list(selected_node_dict.keys())[0]

        for connection_node in self.connection_nodes:
            if connection_node.name == selected_node_name:
                return connection_node.run(input=input, debug=debug)
        raise Exception('No connection node found')

    def run(
            self, input: Prompt, 
            history: list[Prompt] = [], 
            debug: bool = False
        ) -> Prompt:
        input.content = self.input_processor(input.content)
        
        assert self.system_prompt.input_schema(**input.content)
        
        response = self.llm_model.generate(
            system_prompt=self.system_prompt,
            input=input,
            history=history,
            debug=debug
        )

        dict_output = json.loads(response.output_text)
        processed = self.output_processor(dict_output) if self.connection_nodes else dict_output

        assert self.system_prompt.output_schema(**processed)

        result = Prompt(
            content=processed,
            role=self.role
        )

        return result if not self.connection_nodes else self.node_choice(result, input, debug)


# @dataclass
# class AgentGraph:
#     name: str
#     agent:
#     # agents_network: list[Agent]

#     def run(self, Agent: Agent):
        



