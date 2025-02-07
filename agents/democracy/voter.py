from typing import Literal, Optional
from pydantic import Field
from src.prompts import SystemPrompt
from src.agent import Agent
from src.llm.gpt import GptLlmApi
from models.agents import Replier

class VoterOutput(Replier):
    vote: str = Field(
        description="Nome do candidato a ser votado",
    )
    reason: str = Field(
        description="Motivo do voto, cite os pontos principais da escolha, mas seja breve",
    )

prompt = SystemPrompt(
    background='Você é uma IA que vota em uma eleição fictícia e responde o candidato a ser votado em um JSON', 
    steps=[
        'Escolha apenas um candidato a ser votado',
        'Escreva objetivamente o motivo do voto'
    ],
    output_schema=VoterOutput
)

def voter_fn(name: str, graph):
    return Agent(
        name=name,
        llm_model=GptLlmApi(model_name='gpt-4o-mini', temperature=1.2),
        system_prompt=prompt,
        role='user',
        output_schema=VoterOutput,
        graph=graph,
    )
