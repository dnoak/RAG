from typing import Literal, Optional
from pydantic import BaseModel, Field
from src.prompts import SystemPrompt
from src.agent import Agent
from src.llm.gpt import GptLlmApi
from models.agents import Response, Choice


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
    system_prompt=shark_choice_prompt,
    role='connection',
    input_processor=lambda x: {'input': input('User: ')},
    llm_model=GptLlmApi(model_name='gpt-4o-mini'),
)


class SharkInput(Response): 
    input: str = Field(
        description="Resposta da pergunta sobre tubarões"
    )
class SharkOutput(Response):
    input: str = Field(
        description="A cópia exata da pergunta o que o usuário fez" 
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
    system_prompt=shark_prompt,
    role='connection',
    llm_model=GptLlmApi(model_name='gpt-4o-mini'),
)





class EmojiSharkInput(Response):
    input: str = Field(
        description="Pergunta não formatada" 
    )
class EmojiSharkOutput(Response):
    output: str = Field(
        description="Resposta formatada com emojis do fundo do mar"
    )
shark_emojifier_prompt = SystemPrompt(
    input_schema=EmojiSharkInput,
    background='Você é um formatador que insere muitos emojis em textos e responde no formato JSON.', 
    steps=[
        'Formate o texto inserindo emojis do fundo do mar com a temática de tubarões.',
        'Coloque emojis em cada palavra chave de cada parte do texto.'
    ],
    output_schema=EmojiSharkOutput
)
SHARK_EMOJIFIER = Agent(
    name='shark_emojifier',
    system_prompt=shark_emojifier_prompt,
    role='assistant',
    llm_model=GptLlmApi(model_name='gpt-4o-mini'),
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
    genera: Optional[str] = Field(
        description="O gênero do tubarão"
    )
    species: Optional[str] = Field(
        description="O nome científico da espécie do tubarão"
    )
    common_name: Optional[str] = Field(
        description="O nome comum da espécie tubarão"
    )
shark_query_prompt = SystemPrompt(
    input_schema=SharkDatabaseInput,
    background='Você é um assistente que faz consultas em um banco de dados de tubarões e responde no formato JSON.',
    steps=[
        'preencha os campos com apenas as informações dadas implicita ou explicitamente na conversa com o usuário',
    ],
    output_schema=SharkDatabaseOutput
)
SHARK_QUERY = Agent(
    name='shark_query',
    system_prompt=shark_query_prompt,
    role='assistant',
    llm_model=GptLlmApi(model_name='gpt-4o-mini'),
)