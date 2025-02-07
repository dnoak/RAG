from typing import Optional
from pydantic import Field
from src.prompts import SystemPrompt
from agent import Agent
from src.llm.gpt import GptLlmApi
from models.agents import Responser, Classifier
import networkx as nx
import json
from agent import AgentProcessor
from db.shark.elastic import ElasticShark

class SharkDatabaseFormatterInput(Responser):
    user_input: str = Field(
        description="A pergunta que o usuário fez"
    )
    db_output: dict = Field(
        description="As respostas do banco de dados de tubarões"
    )

class SharkDatabaseFormatterOutput(Responser):
    input: Optional[str] = Field(
        description="Resposta da pergunta sobre tubarões" 
    )

class SharkDatabaseFormatterProcessor(AgentProcessor):
    db: ElasticShark = ElasticShark(
        index='shark_index',
        hosts='https://localhost:9200',
        basic_auth=('elastic', '+bp8O9L5xyjKMDr*KUix'),
        verify_certs=False,
    )

    def process(self, *args, **kwargs) -> dict:
        data = self.db.search(filters=kwargs['input'].content['input'], size=3)
        data = [json.dumps(shark, indent=2, ensure_ascii=False) for shark in data]
        data = '\n'.join(data)
        prompt = f"[user input]\n{kwargs['input'].content['input']}\n\n"
        prompt += "[shark database]\n" + data
        return {'input': prompt}

shark_query_prompt = SystemPrompt(
    background='Você é um assistente especialista que responde perguntas do usuário com base nas respostas de um banco de dados de tubarões e responde no formato JSON.',
    steps=[
        'responda estritamente apenas se a resposta da pergunta estiver contida no banco de dados de tubarões',
        'caso a resposta não seja encontrada, responda que a resposta não foi encontrada no banco de dados de tubarões',
    ],
    output_schema=SharkDatabaseFormatterOutput
)

def shark_query_formatter(graph: Optional[nx.DiGraph] = None):
    return Agent(
        name='shark_query_formatter',
        llm_model=GptLlmApi(model_name='gpt-4o-mini'),
        system_prompt=shark_query_prompt,
        role='assistant',
        input_schemas=[SharkDatabaseFormatterInput],
        output_schema=SharkDatabaseFormatterOutput,
        # processor=SharkDatabaseFormatterProcessor(),
        graph=graph
    )
