from typing import Optional
from pydantic import Field
from src.prompts import SystemPrompt
from src.agent import Agent
from src.llm.gpt import GptLlmApi
from models.agents import Responser, Classifier
import networkx as nx
import json
from src.agent import AgentProcessor, LlmAgentProcessor

class SharkDatabaseInput(Responser):
    input: str = Field(
        description="A pergunta exata o que o usuário perguntou"
    )

class SharkDatabaseOutput(Responser):
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

class SharkDatabaseProcessor(LlmAgentProcessor):
    def post_process(self, *args, **kwargs) -> dict:
        with open('data/wiki/sharks/sharks.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        data = data[:3]
        prompt = f"[user input]\n{kwargs['input'].content['input']}\n\n"
        prompt += "[shark database]\n" + json.dumps(data, indent=2, ensure_ascii=False)
        return {'input': prompt}

shark_query_prompt = SystemPrompt(
    input_schema=SharkDatabaseInput,
    background='Você é um assistente especialista que responde perguntas do usuário com base nas respostas de um banco de dados de tubarões e responde no formato JSON.',
    steps=[
        'responda estritamente apenas se a resposta da pergunta estiver contida no banco de dados de tubarões',
        'caso a resposta não seja encontrada, responda que a resposta não foi encontrada no banco de dados de tubarões',
    ],
    output_schema=SharkDatabaseOutput
)

def shark_db_formatter(graph: Optional[nx.DiGraph] = None):
    return Agent(
        name='shark_query',
        llm_model=GptLlmApi(model_name='gpt-4o-mini'),
        system_prompt=shark_query_prompt,
        role='assistant',
        processor=SharkDatabaseProcessor(),
        graph=graph
    )