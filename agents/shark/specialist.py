from typing import Optional
from pydantic import Field
from src.prompts import SystemPrompt
from src.agent import Agent
from src.llm.gpt import GptLlmApi
from models.agents import Responder, Classifier
import networkx as nx

class SharkSpecialistAgentInput(Responder):
    user_input: str = Field(
        description="Pergunta sobre tubarões"
    )

class SharkSpecialistAgentOutput(Responder):
    output: str = Field(
        description="Resposta da pergunta sobre tubarões ou da interação com o usuário" 
    )

shark_specialist_prompt = SystemPrompt(
    background='Você é um assistente TUBARÃO que é especialista em tubarões e interage com o usuário respondendo com coisas relacionadas a tubarões. Responda sempre no formato JSON. ',
    steps=[
        'o usuário pode interagir normalmente com você, mas caso ele faça perguntas totalmente não relacionado a tubarões, fale para ele fazer outra pergunta relacionada com o tema',
    ],
    output_schema=SharkSpecialistAgentOutput
)

def shark_specialist(graph: Optional[nx.DiGraph] = None):
    return Agent(
        name='shark_specialist',
        llm_model=GptLlmApi(model_name='gpt-4o-mini'),
        system_prompt=shark_specialist_prompt,
        input_schemas=[SharkSpecialistAgentInput],
        output_schema=SharkSpecialistAgentOutput,
        role='user:connection',
        graph=graph
    )