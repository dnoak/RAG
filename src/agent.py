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
        self.connection_node: Agent | None = None

    def connect(self, agent: 'Agent'):
        self.connection_node: Agent | None = agent
    
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
        processed = self.output_processor(dict_output) if self.connection_node else dict_output

        result = Prompt(
            content=processed,
            role=self.role
        )
        if self.connection_node is not None:
            return self.connection_node.run(result, debug=debug)
        return result


# @dataclass
# class AgentGraph:
#     name: str
#     agent:
#     # agents_network: list[Agent]

#     def run(self, Agent: Agent):
        



