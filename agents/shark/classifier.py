from typing import Optional
from pydantic import Field
from src.prompts import SystemPrompt
from agent import Agent, AgentProcessor
from src.llm.gpt import GptLlmApi
from models.agents import Responder, Classifier
import networkx as nx

class SharkClassifierInput(Responder):
    input: str = Field(
        description="Resposta da pergunta sobre tubarões"
    )

class SharkPromptClassifierOutput(Classifier):
    shark_specialist: Optional[bool] = Field(
        description="Caso a interação do usuário seja relacionada a conhecimentos gerais sobre tubarões ou sobre conversas aleatórias como saudações e apresentações.", 
    )
    shark_query_formatter: Optional[bool] = Field(
        description="Caso a pergunta seja técnica e específica sobre nomes científicos de ordens, famílias, espécies, gêneros de tubarões ou os autores que fizeram estudos sobre esses tubarões",
    )
    shark_wikipedia: Optional[bool] = Field(
        description="Caso o usuário fale para fazer uma pesquisa na internet ou diretamente na wikipedia, ou quando o usuário usa a tag #wikipedia ou #wiki dentro da sua pergunta",
    )

class SharkClassifierOutput(Classifier):
    user_input: str = Field(
        description="A pergunta que o usuário fez"
    )

class SharkClassifierProcessor(AgentProcessor):
    def process(self, *args, **kwargs) -> dict:
        query = {k: v for k, v in kwargs['llm_output'].items() if v}
        user_input = {'user_input': kwargs['input'].contents[0]['input']}
        if not query:
            return {Classifier.connection_type(): 'shark_specialist'} | user_input
        assert len(query) == 1, query
        return {Classifier.connection_type(): list(query.keys())[0]} | user_input

shark_choice_sys_prompt = SystemPrompt(
    background='Você é um assistente especialista em classificar perguntas sobre tubarões que responde sempre no formato JSON.',
    steps=[
        'Você irá classificar o tipo da pergunta do usuário com base nas informações da pergunta dele',
        'Voce responderá em booleano e classificará **APENAS UMA** das escolhas como `true`',
        'todas as outras escolhas restantes você classificará como `false`',
        '**NUNCA** deixe de responder uma das escolhas como `true`',
    ],
    output_schema=SharkPromptClassifierOutput
)

def shark_classifier(graph: Optional[nx.DiGraph] = None):
    return Agent(
        name='shark_classifier',
        llm_model=GptLlmApi(model_name='gpt-4o-mini'),
        system_prompt=shark_choice_sys_prompt,
        role='user:connection',
        input_schemas=[SharkClassifierInput],
        output_schema=SharkClassifierOutput,
        processor=SharkClassifierProcessor(),
        graph=graph
    )