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

class SharkDatabaseQueryFormatterInput(Responder):
    input: str = Field(
        description="A pergunta que o usuário fez"
    )

class SharkPromptDatabaseQueryFormatterOutput(Responder):
    order: Optional[str] = Field(
        description="O nome da ordem de tubarões"
    )
    family: Optional[str] = Field(
        description="A família do tubarão"
    )
    family_common_name: Optional[str] = Field(
        description="O nome comum da família do tubarão"
    )
    genus: Optional[str] = Field(
        description="O gênero do tubarão"
    )
    species_name: Optional[str] = Field(
        description="O nome científico da espécie do tubarão"
    )
    species_common_name: Optional[str] = Field(
        description="O nome comum da espécie do tubarão"
    )

class SharkDatabaseQueryFormatterOutput(Responder):
    db_formatted_results: str = Field(
        description="A pergunta que o usuário fez e a resposta do banco de dados de tubarões"
    )

class SharkDatabaseQueryFormatterProcessor(AgentProcessor):
    db: ElasticShark = ElasticShark(
        index='shark_index',
        hosts='https://localhost:9200',
        basic_auth=('elastic', '+bp8O9L5xyjKMDr*KUix'),
        verify_certs=False,
    )

    def process(self, *args, **kwargs) -> dict:
        max_results = 3
        query = { k: v for k, v in kwargs['llm_output'].items() if v is not None}
        if query:
            data = self.db.search(filters=query, size=max_results)
            data = [json.dumps(shark, indent=2, ensure_ascii=False) for shark in data]
            data = '\n'.join(data)
        else:
            data = 'Nenhum resultado encontrado'
        prompt = f"[user input]\n{kwargs['input'].content['input']}\n\n"
        prompt += f"[shark database - Top {max_results} resultados]\n" + data 

        return {
            "db_formatted_results": prompt,
        }

shark_query_prompt = SystemPrompt(
    background='Você é um assistente que faz consultas em um banco de dados de tubarões e responde no formato JSON.',
    steps=[
        'preencha os campos com apenas as informações dadas explicitamente na conversa com o usuário',
        'preencha com `null` as informações que não foram explicitamente informadas',
    ],
    output_schema=SharkPromptDatabaseQueryFormatterOutput
)

def shark_query_formatter(graph: Optional[nx.DiGraph] = None):
    return Agent(
        name='shark_query_formatter',
        llm_model=GptLlmApi(model_name='gpt-4o-mini'),
        system_prompt=shark_query_prompt,
        role='assistant',
        input_schema=SharkDatabaseQueryFormatterInput,
        output_schema=SharkDatabaseQueryFormatterOutput,
        processor=SharkDatabaseQueryFormatterProcessor(),
        graph=graph
    )
