from typing import Literal, Optional
from pydantic import Field
from src.prompts import SystemPrompt
from src.agent import Agent, AgentProcessor
from src.llm.gpt import GptLlmApi
from termcolor import colored
from models.agents import Replier, Replicator

class ElectionOutput(Replicator):
    winner: str = Field(
        description="Nome do candidato que ganhou a eleição."
    )

class ElectionProcessor(AgentProcessor):
    def process(self, *args, **kwargs) -> dict:
        votes = [i['vote'] for i in kwargs['input'].contents]
        winner = max(set(votes), key=votes.count)
        print('🔴 🟡 '*8 )
        print(colored(f'votes: {votes}', color='yellow', attrs=['bold']))
        print(colored(f'winner: {winner}', color='green', attrs=['bold']))
        print('🔴 🟡 '*8 )
        return {'winner': ''}

def election_fn(name: str, graph):
    return Agent(
        name=name,
        llm_model=None,
        system_prompt=None,
        role='assistant',
        output_schema=ElectionOutput,
        processor=ElectionProcessor(),
        graph=graph,
    )