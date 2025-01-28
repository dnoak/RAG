from typing import Optional
from pydantic import Field
from src.prompts import SystemPrompt
from src.agent import Agent
from src.llm.gpt import GptLlmApi
from models.agents import Responser, Classifier
import networkx as nx

class SharkSpecialistAgentInput(Responser):
    input: str = Field(
        description="Pergunta sobre tubarões"
    )

class SharkSpecialistAgentOutput(Responser):
    output: str = Field(
        description="Resposta da pergunta sobre tubarões" 
    )

shark_specialist_prompt = SystemPrompt(
    background='Você é um assistente TUBARÃO que é especialista em tubarões e interage com o usuário respondendo com coisas relacionadas a tubarões. Responda sempre no formato JSON. ',
    steps=[
        'o usuário pode interagir normalmente com você, mas caso ele faça perguntas totalmente não relacionado a tubarões, fale para ele fazer outra pergunta relacionada com o tema',
    ],
    output_schema=SharkSpecialistAgentOutput
)

def shark_specialist_unformatted(graph: Optional[nx.DiGraph] = None):
    return Agent(
        name='shark_specialist',
        llm_model=GptLlmApi(model_name='gpt-4o-mini'),
        system_prompt=shark_specialist_prompt,
        input_schema=SharkSpecialistAgentInput,
        output_schema=SharkSpecialistAgentOutput,
        role='connection',
        graph=graph
    )