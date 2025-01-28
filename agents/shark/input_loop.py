from typing import Optional
from pydantic import Field
from src.prompts import SystemPrompt
from src.agent import Agent
from src.llm.gpt import GptLlmApi
from models.agents import Responser, Classifier
from src.agent import AgentProcessor, LlmAgentProcessor
import networkx as nx

class SharkInputLoopInput(Responser):
    formatted_output: str = Field(
        description="Pergunta sobre tubarões"
    )

class SharkInputLoopOutput(Responser):
    input: str = Field(
        description="Resposta da pergunta sobre tubarões" 
    )

class SharkReconnectLoopProcessor(AgentProcessor):
    # def pre_process(self, *args, **kwargs) -> dict:
    #     return {'formatted_output': input('User: ')}
    
    def process(self, *args, **kwargs) -> dict:
        return {'input': kwargs['input'].content['formatted_output']}
    #     kwargs['input'].content = {'formatted_output': kwargs['formatted_output']}
    #     return 
        # return {'input': kwargs['input'].content['formatted_output']}
    
    # def post_process(self, *args, **kwargs) -> dict:

shark_input_loop_prompt = SystemPrompt(
    input_schema=SharkInputLoopInput,
    background='',
    steps=[],
    output_schema=SharkInputLoopOutput
)

def shark_input_loop(graph: Optional[nx.DiGraph] = None):
    return Agent(
        name='shark_input_loop',
        system_prompt=shark_input_loop_prompt,
        role='connection',
        processor=SharkReconnectLoopProcessor(),
        graph=graph
    )
        