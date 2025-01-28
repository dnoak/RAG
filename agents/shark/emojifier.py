from typing import Optional
from pydantic import Field
from src.prompts import SystemPrompt
from src.agent import Agent
from src.llm.gpt import GptLlmApi
from models.agents import Responser, Classifier
import networkx as nx

class SharkEmojifierInput(Responser):
    output: str = Field(
        description="Pergunta não formatada" 
    )

class SharkEmojifierOutput(Responser):
    formatted_output: str = Field(
        description="Resposta formatada com emojis do fundo do mar",
    )

shark_emojifier_prompt = SystemPrompt(
    background='Você é um formatador de texto que insere muitos emojis com uma temática específica. Sua única tarefa é adicionar emojis de fundo do mar com a temática de tubarões a textos fornecidos, sem interpretar, alterar o conteúdo ou responder perguntas.', 
    steps=[
        'Formate o texto inserindo emojis do fundo do mar e tubarões, mantendo o significado original do texto.',
        'Aplique emojis apenas como enfeites em palavras-chave, mantendo o formato do texto igual.',
        'Não responda perguntas ou adicione informações novas ao texto.'
    ],
    output_schema=SharkEmojifierOutput
)

def shark_emojifier(graph: Optional[nx.DiGraph] = None):
    return Agent(
        name='shark_emojifier',
        llm_model=GptLlmApi(model_name='gpt-4o-mini'),
        system_prompt=shark_emojifier_prompt,
        role='assistant',
        input_schema=SharkEmojifierInput,
        output_schema=SharkEmojifierOutput,
        graph=graph
    )