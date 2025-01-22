import os
from src.chat import Chat
from src.prompt_query import SystemPrompt
from src.llm.gpt import GptLlmApi, FakeGptLlmApi
from src.prompt_query import OutputSchema
from pydantic import BaseModel, Field



class SimpleDolphinOutput(BaseModel):
    response: str = Field(
        default='...',
        description="Resposta da pergunta sobre golfinhos"
    )

class SimpleSharkOutput(BaseModel):
    response: str = Field(
        default='...',
        description="Resposta da pergunta sobre shibas"
    )

class DolphinClassifierOutput(BaseModel):
    species: str | None = Field(
        default=None,
        description="Espécie do golfinho"
    )
    subspecies: str | None = Field(
        default=None,
        description="Subspécie do golfinho"
    )
    color: str | None = Field(
        default=None,
        description="Cor do golfinho"
    )


agents = {
    'dolphin': SystemPrompt(
        background='Você é um assistente virtual que responde apenas perguntas sobre golfinhos em JSON.',
        steps=[
            'responda a pergunta do usuário usando rimas utilizando emojis do fundo do mar',
            'caso a pergunta não seja sobre golfinhos, responda **apenas** com emojis temáticos de golfinhos e fundo do mar, sem usar texto.',
        ],
        output=OutputSchema(schema=SimpleDolphinOutput()).build()
    ),

    'dolphin_species': SystemPrompt(
        background='Você é um assistente virtual que monta queries estruturadas em JSON de perguntas sobre golfinhos.',   
        steps=[
            'Você irá preencher as informações do golfinho na query caso elas estejam explícitas ou implícitas na pergunta.',
            'caso a pergunta não seja sobre golfinhos, preencha a query com onomatopeias do fundo do mar com emojis',
        ],
        output=OutputSchema(schema=DolphinClassifierOutput()).build()
    ),

    'shark': SystemPrompt(
        background='Você é um assistente virtual que responde apenas perguntas sobre tubarões em JSON.',
        steps=[
            'responda a pergunta do usuário usando rimas utilizando emojis do fundo do mar',
            'caso a pergunta não seja sobre tubarões, responda **apenas** com emojis temáticos de tubarões e fundo do mar, sem usar texto.',
        ],
        output=OutputSchema(schema=SimpleSharkOutput()).build()
    ),
}

chat = Chat(
    llm_model=GptLlmApi(model_name='gpt-4o-mini'),
    history_size=5
)
chat.system(agents['dolphin'].build())
chat.assistant('Você está pronto para começar a conversar com o golfinho')
while True:
    question = input('[Pergunta]: ')
    if question.startswith('/system'):
        if question == '/system dolphin':
            chat.system(agents['dolphin'].build())
            chat.assistant('Você está pronto para começar a conversar com o golfinho!')
        elif question == '/system shark':
            chat.system(agents['shark'].build())
            chat.assistant('Você está pronto para começar a conversar com o tubarão!')
        elif question == '/system dolphin_species':
            chat.system(agents['dolphin_species'].build())
            chat.assistant('Classificador de golfinhos!')
        continue

    chat.user(question)
    chat.process(single_message=True)

    os.system('cls')
    chat.debug()