import os
from typing import Optional
from src.chat import Chat
from src.prompts import SystemPrompt, AssistantPrompt, UserPrompt
from src.llm.gpt import GptLlmApi, FakeGptLlmApi
from pydantic import BaseModel as PydanticBaseModel, Field
from data.prompts.system_prompts import DOLPHIN_SPECIES, SHARK_SPECIALIST, BASE_SHARK_SELECTOR

chat = Chat(
    llm_model=GptLlmApi(model_name='gpt-4o-mini'),
    history_size=6
)
chat.system(BASE_SHARK_SELECTOR)
chat.assistant(AssistantPrompt(content='Você está pronto para começar a conversar com o tubarão martelo!'))
history = False

os.system('cls')
while True:
    question = input('[Pergunta]: ')
    if question.startswith('/history'):
        if question == '/history true':
            history = True
        elif question == '/history false':
            history = False
        continue
    if question.startswith('/system'):
        if question == '/system dolphin':
            chat.system(DOLPHIN)
            chat.assistant(AssistantPrompt(content='Você está pronto para começar a conversar com o golfinho!'))
        elif question == '/system shark':
            chat.system(SHARK)
            chat.assistant(AssistantPrompt(content='Você está pronto para começar a conversar com o tubarão!'))
        elif question == '/system dolphin_species':
            chat.system(DOLPHIN_SPECIES)
            chat.assistant(AssistantPrompt(content='Classificador de golfinhos!'))
        continue
    
    chat.user(UserPrompt(content=question))
    chat.process(use_history=history, debug=True)
    print('\n'*3)