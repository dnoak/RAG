import os
from typing import Optional
from src.chat import Chat
from src.prompts import SystemPrompt, AssistantPrompt, UserPrompt
from src.llm.gpt import GptLlmApi, FakeGptLlmApi
from pydantic import BaseModel as PydanticBaseModel, Field
from models.prompt_connectors import TextOutput, ApiCallOutput

class DolphinClassifierOutput(ApiCallOutput):
    species: str = Field(
        description="Espécie do golfinho"
    )
    subspecies: Optional[str | int | dict] = Field(
        description="Subspécie do golfinho"
    )
    colors: Optional[list[str]] = Field(
        description="Cor do golfinho"
    )
    gender: Optional[str] = Field(
        description="Gênero do golfinho"
    )

class SharkSpecialistOutput(TextOutput):
    response: str = Field(
        description="Resposta da pergunta sobre tubarões"
    )

    @staticmethod
    def action() -> str:
        return 'shark_api_call'


DOLPHIN_SPECIES = SystemPrompt(
    background='Você é um assistente virtual que monta queries estruturadas em JSON de perguntas sobre golfinhos.',   
    steps=[
        'Você irá preencher as informações do golfinho na query caso elas estejam explícitas ou implícitas na pergunta.',
        'caso a pergunta ou interação não seja sobre golfinhos, preencha a query com onomatopeias do fundo do mar com emojis',
    ],
    output_schema=DolphinClassifierOutput
)


SHARK_SPECIALIST = SystemPrompt(
    background='Você é um TUBARÃO MARTELO que é especialista em tubarões, mas interage apenas com coisas relacionadas a tubarões e da a resposta em formato JSON.',
    steps=[
        'caso o usuário fale algo totalmente não relacionado a tubarões, fale para ele fazer outra pergunta relacionada com o tema' 
    ],
    output_schema=SharkSpecialistOutput
)
