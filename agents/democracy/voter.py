from typing import Literal, Optional
from pydantic import Field
from src.prompts import SystemPrompt
from src.agent import Agent
from src.llm.gpt import GptLlmApi
from models.agents import Replier
import networkx as nx

class VoterInput(Replier):
    candidate_name: str = Field(
        description="Nome do candidato",
    )
    political_ideology: str = Field(
        description="Apresentação da ideologia política do candidato",
    )
    proposal_economy: str = Field(
        description="Proposta de governo para a economia",
    )
    proposal_education: str = Field(
        description="Proposta de governo para a educação",
    )
    proposal_security: str = Field(
        description="Proposta de governo para a segurança",
    )

class VoterOutput(Replier):
    vote: str = Field(
        description="Nome do candidato a ser votado",
    )

prompt = SystemPrompt(
    background='Você é uma IA que vota em uma eleição fictícia e responde o candidato a ser votado em um JSON', 
    steps=[
        'Escolha apenas um candidato a ser votado',
    ],
    output_schema=VoterOutput
)

def voter_fn(name: str, n_inputs: int, graph: Optional[nx.DiGraph] = None):
    return Agent(
        name=name,
        llm_model=GptLlmApi(model_name='gpt-4o-mini', temperature=1.2),
        system_prompt=prompt,
        role='user',
        input_schemas=[VoterInput]*n_inputs,
        output_schema=VoterOutput,
        graph=graph,
    )
