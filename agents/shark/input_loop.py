from typing import Optional
from pydantic import Field
from src.prompts import SystemPrompt
from src.agent import Agent
from src.llm.gpt import GptLlmApi
from models.agents import Responder, Classifier
from src.agent import AgentProcessor
import networkx as nx

class SharkAgentInput(Responder):
    loop_output: str = Field(
        description="Pergunta sobre tubarões"
    )

class SharkAgentOutput(Responder):
    input: str = Field(
        description="Resposta da pergunta sobre tubarões" 
    )

class SharkAgentProcessor(AgentProcessor):
    def process(self, *args, **kwargs) -> dict:
        return {'input': input('User: ')}

def shark_input_loop(graph: Optional[nx.DiGraph] = None):
    return Agent(
        name='shark_input_loop',
        llm_model=None,
        system_prompt=None,
        role='connection',
        input_schema=SharkAgentInput,
        output_schema=SharkAgentOutput,
        processor=SharkAgentProcessor(),
        graph=graph
    )
        