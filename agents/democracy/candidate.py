from typing import Literal, Optional
from pydantic import Field
from src.prompts import SystemPrompt
from src.agent import Agent
from src.llm.gpt import GptLlmApi
from models.agents import Responder
import networkx as nx

class CandidateInput(Responder):
    feedback: str = Field(
        description="Voto do eleitor" 
    )

class VoterOutput(Responder):
    proposal: str = Field(
        description="Proposta de governo do candidato",
    )

shark_emojifier_prompt = SystemPrompt(
    background='Você é uma IA que é um candidato a ser votado. Você responde a sua proposta de governo em JSON', 
    steps=[
        'Escolha apenas um candidato a ser votado',
    ],
    output_schema=VoterOutput
)

def shark_emojifier(graph: Optional[nx.DiGraph] = None):
    return Agent(
        name='shark_emojifier',
        llm_model=GptLlmApi(model_name='gpt-4o-mini'),
        system_prompt=shark_emojifier_prompt,
        role='assistant',
        input_schemas=[VoterInput],
        output_schema=VoterOutput,
        graph=graph,
    )