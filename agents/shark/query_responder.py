from typing import Optional
from pydantic import Field
from src.prompts import SystemPrompt
from src.agent import Agent
from src.llm.gpt import GptLlmApi
from models.agents import Responder, Classifier
import networkx as nx
import json
from src.agent import AgentProcessor
from db.shark.elastic import ElasticShark

class SharkDatabaseResponderInput(Responder):
    db_formatted_results: str = Field(
        description="A pergunta que o usuário fez"
    )

class SharkDatabaseResponderOutput(Responder):
    output: Optional[str] = Field(
        description="Resposta da pergunta sobre tubarões" 
    )

shark_query_prompt = SystemPrompt(
    background='Você é um assistente especialista que responde perguntas do usuário com base nas respostas de um banco de dados de tubarões e responde no formato JSON.',
    steps=[
        'responda estritamente apenas se a resposta da pergunta estiver contida no banco de dados de tubarões',
        'caso a resposta não seja encontrada, responda que a resposta não foi encontrada no banco de dados de tubarões',
    ],
    output_schema=SharkDatabaseResponderOutput
)

def shark_query_responder(graph: Optional[nx.DiGraph] = None):
    return Agent(
        name='shark_query_responder',
        llm_model=GptLlmApi(model_name='gpt-4o-mini'),
        system_prompt=shark_query_prompt,
        role='user',
        input_schema=SharkDatabaseResponderInput,
        output_schema=SharkDatabaseResponderOutput,
        graph=graph
    )
