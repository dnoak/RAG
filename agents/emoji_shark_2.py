from pydantic import BaseModel as PydanticBaseModel, Field
from src.prompts import SystemPrompt
from src.agent import Agent
from src.llm.gpt import GptLlmApi

class BaseModel(PydanticBaseModel, extra='forbid'):
    pass

class EmojiSharkInput(BaseModel):
    input: str = Field(
        description="Resposta da pergunta sobre tubarões"
    )
class EmojiSharkUnformattedOutput(BaseModel):
    unformatted_output: str = Field(
        description="Resposta da pergunta sobre tubarões"
    )
SHARK_SYS_PROMPT = SystemPrompt(
    input_schema=EmojiSharkInput,
    background='Você é um assistente TUBARÃO MARTELO que é especialista em tubarões e interage com o usuário respondendo apenas com coisas relacionadas a tubarões. Responda sempre no formato JSON.',
    steps=[
        'o usuário pode interagir normalmente com você, mas caso ele faça perguntas totalmente não relacionado a tubarões, fale para ele fazer outra pergunta relacionada com o tema' 
    ],
    output_schema=EmojiSharkUnformattedOutput
)


class EmojiSharkUnformattedInput(BaseModel):
    unformatted_output: str = Field(
        description="Pergunta não formatada" 
    )
class EmojiSharkFormattedOutput(BaseModel):
    output: str = Field(
        description="Resposta formatada com emojis do fundo do mar"
    )
SHARK_EMOJI = SystemPrompt(
    input_schema=EmojiSharkUnformattedInput,
    background='Você é um formatador que insere muitos emojis em textos e responde no formato JSON.', 
    steps=[
        'Formate o texto inserindo emojis do fundo do mar com a temática de tubarões.',
        'Coloque emojis em cada palavra chave de cada parte do texto.'
    ],
    output_schema=EmojiSharkFormattedOutput
)