from dataclasses import dataclass
from typing import Literal, Optional
from pydantic import BaseModel, Field
from src.prompts import SystemPrompt
from src.agent import Agent, AgentProcessor, LlmAgentProcessor
from src.llm.gpt import GptLlmApi
from models.agents import Response, Choice
import networkx as nx
import json

GLOBAL_GRAPH = nx.DiGraph()

class SharkChoiceInput(Response):
    input: str = Field(
        description="Resposta da pergunta sobre tubarões"
    )
class SharkChoiceOutput(Choice):
    shark_agent: Optional[bool] = Field(
        description="Caso a interação do usuário seja relacionada a conhecimentos gerais sobre tubarões ou sobre conversas aleatórias.", 
        title="shark_classifier"
    )
    shark_query: Optional[bool] = Field(
        description="Caso a pergunta seja técnica e específica sobre nomes científicos de ordens, famílias, espécies, gêneros de tubarões ou os autores que fizeram estudos sobre esses tubarões",
        title="shark_query"
    )
class SharkChoiceProcessor(LlmAgentProcessor):
    def pre_process(self, *args, **kwargs) -> dict:
        return {'input': input('User: ')}

shark_choice_prompt = SystemPrompt(
    input_schema=SharkChoiceInput,
    background='Você é um assistente especialista em classificar perguntas sobre tubarões que responde sempre no formato JSON.',
    steps=[
        'Você irá classificar o tipo da pergunta do usuário com base nas informações da pergunta dele',
        'Voce responderá em booleano e classificará apenas uma das escolhas como `true` (pelo menos uma das escolhas deve ser `true`)',
        'as outras escolhas você classificará como `false`',
    ],
    output_schema=SharkChoiceOutput
)
SHARK_CHOICE = Agent(
    name='shark_classifier',
    llm_model=GptLlmApi(model_name='gpt-4o-mini'),
    system_prompt=shark_choice_prompt,
    role='connection',
    processor=SharkChoiceProcessor(),
    graph=GLOBAL_GRAPH
)




class SharkInput(Response): 
    input: str = Field(
        description="Pergunta sobre tubarões"
    )
class SharkOutput(Response):
    output: str = Field(
        description="Resposta da pergunta sobre tubarões" 
    )
shark_prompt = SystemPrompt(
    input_schema=SharkInput,
    background='Você é um assistente TUBARÃO que é especialista em tubarões e interage com o usuário respondendo com coisas relacionadas a tubarões. Responda sempre no formato JSON. ',
    steps=[
        'o usuário pode interagir normalmente com você, mas caso ele faça perguntas totalmente não relacionado a tubarões, fale para ele fazer outra pergunta relacionada com o tema',
    ],
    output_schema=SharkOutput
)
SHARK = Agent(
    name='shark_agent',
    llm_model=GptLlmApi(model_name='gpt-4o-mini'),
    system_prompt=shark_prompt,
    role='connection',
    graph=GLOBAL_GRAPH
)





class EmojiSharkInput(Response):
    output: str = Field(
        description="Pergunta não formatada" 
    )
class EmojiSharkOutput(Response):
    formatted_output: str = Field(
        description="Resposta formatada com emojis do fundo do mar"
    )
shark_emojifier_prompt = SystemPrompt(
    input_schema=EmojiSharkInput,
    background='Você é um formatador de texto que insere muitos emojis com uma temática específica. Sua única tarefa é adicionar emojis de fundo do mar com a temática de tubarões a textos fornecidos, sem interpretar, alterar o conteúdo ou responder perguntas.', 
    steps=[
        'Formate o texto inserindo emojis do fundo do mar e tubarões, mantendo o significado original do texto.',
        'Aplique emojis apenas como enfeites em palavras-chave, mantendo o formato do texto igual.',
        'Não responda perguntas ou adicione informações novas ao texto.'
    ],
    output_schema=EmojiSharkOutput
)
@dataclass
class SharkEmojifierProcessor(LlmAgentProcessor):
    def post_process(self, *args, **kwargs) -> dict:
        return {'input': kwargs['formatted_output']}

SHARK_EMOJIFIER = Agent(
    name='shark_emojifier',
    llm_model=GptLlmApi(model_name='gpt-4o-mini'),
    system_prompt=shark_emojifier_prompt,
    role='assistant',
    graph=GLOBAL_GRAPH
)





class SharkDatabaseInput(Response):
    input: str = Field(
        description="A pergunta exata o que o usuário perguntou"
    )
class SharkDatabaseOutput(Response):
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
shark_query_prompt = SystemPrompt(
    input_schema=SharkDatabaseInput,
    background='Você é um assistente que faz consultas em um banco de dados de tubarões e responde no formato JSON.',
    steps=[
        'preencha os campos com apenas as informações dadas explicitamente na conversa com o usuário',
        'preencha com `null` as informações que não foram explicitamente informadas',
    ],
    output_schema=SharkDatabaseOutput
)

@dataclass
class SharkQueryProcessor(LlmAgentProcessor):
    def post_process(self, *args, **kwargs) -> dict:
        with open('data/wiki/sharks/sharks.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        data = data[:3]
        prompt = f"[user input]\n{kwargs['input'].content['input']}\n\n"
        prompt += "[shark database]\n" + json.dumps(data, indent=2, ensure_ascii=False)
        return {'input': prompt}

SHARK_QUERY = Agent(
    name='shark_query',
    llm_model=GptLlmApi(model_name='gpt-4o-mini'),
    system_prompt=shark_query_prompt,
    role='user',
    processor=SharkQueryProcessor(),
    graph=GLOBAL_GRAPH
)