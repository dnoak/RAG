from pydantic import BaseModel as PydanticBaseModel, Field
from src.prompts import SystemPrompt
from src.agent import Agent
from src.llm.gpt import GptLlmApi

class BaseModel(PydanticBaseModel, extra='forbid'):
    pass

class EmojiSharkSpecialistInput(BaseModel):
    input: str = Field(
        description="Resposta da pergunta sobre tubarões"
    )
class EmojiSharkSpecialistUnformattedOutput(BaseModel):
    unformatted_output: str = Field(
        description="Resposta da pergunta sobre tubarões"
    )
SHARK_SPECIALIST = SystemPrompt(
    input_schema=EmojiSharkSpecialistInput,
    background='Você é um assistente TUBARÃO MARTELO que é especialista em tubarões e interage com o usuário respondendo apenas com coisas relacionadas a tubarões. Responda sempre no formato JSON.',
    steps=[
        'o usuário pode interagir normalmente com você, mas caso ele faça perguntas totalmente não relacionado a tubarões, fale para ele fazer outra pergunta relacionada com o tema' 
    ],
    output_schema=EmojiSharkSpecialistUnformattedOutput
)


class EmojiSharkSpecialistUnformattedInput(BaseModel):
    unformatted_output: str = Field(
        description="Pergunta não formatada" 
    )
class EmojiSharkSpecialistFormattedOutput(BaseModel):
    output: str = Field(
        description="Resposta formatada com emojis do fundo do mar"
    )
SHARK_SPECIALIST_EMOJI = SystemPrompt(
    input_schema=EmojiSharkSpecialistUnformattedInput,
    background='Você é um formatador que insere muitos emojis em textos que responde em JSON.', 
    steps=[
        'Formate o texto inserindo emojis do fundo do mar com a temática de tubarões.',
        'Coloque emojis em cada palavra chave de cada parte do texto.'
    ],
    output_schema=EmojiSharkSpecialistFormattedOutput
)

EMOJI_SHARK_AGENT = Agent(
    name='Shark Specialist',
    llm_model=GptLlmApi(model_name='gpt-3.5-turbo'),
    pipeline=[SHARK_SPECIALIST, SHARK_SPECIALIST_EMOJI]
)