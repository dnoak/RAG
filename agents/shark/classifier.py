from typing import Optional
from pydantic import Field
from src.prompts import SystemPrompt
from src.agent import Agent
from src.llm.gpt import GptLlmApi
from models.agents import Responser, Classifier
import networkx as nx

class SharkClassifierInput(Responser):
    input: str = Field(
        description="Resposta da pergunta sobre tubarões"
    )

class SharkClassifierOutput(Classifier):
    shark_specialist: Optional[bool] = Field(
        description="Caso a interação do usuário seja relacionada a conhecimentos gerais sobre tubarões ou sobre conversas aleatórias.", 
        # title="shark_classifier"
    )
    shark_query: Optional[bool] = Field(
        description="Caso a pergunta seja técnica e específica sobre nomes científicos de ordens, famílias, espécies, gêneros de tubarões ou os autores que fizeram estudos sobre esses tubarões",
        # title="shark_query"
    )

shark_choice_sys_prompt = SystemPrompt(
    background='Você é um assistente especialista em classificar perguntas sobre tubarões que responde sempre no formato JSON.',
    steps=[
        'Você irá classificar o tipo da pergunta do usuário com base nas informações da pergunta dele',
        'Voce responderá em booleano e classificará apenas uma das escolhas como `true` (pelo menos uma das escolhas deve ser `true`)',
        'as outras escolhas você classificará como `false`',
    ],
    output_schema=SharkClassifierOutput
)

def shark_classifier(graph: Optional[nx.DiGraph] = None):
    return Agent(
        name='shark_classifier',
        llm_model=GptLlmApi(model_name='gpt-4o-mini'),
        system_prompt=shark_choice_sys_prompt,
        role='connection',
        input_schema=SharkClassifierInput,
        output_schema=SharkClassifierOutput,
        graph=graph
    )