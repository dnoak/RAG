from src.prompts import Prompt
from src.agent import Agent
from agents.emoji_shark import SHARK_SYS_PROMPT, SHARK_EMOJI
from src.llm.gpt import GptLlmApi
from agents.shark_2 import SHARK_CHOICE, SHARK, SHARK_EMOJIFIER, SHARK_QUERY


choice = SHARK_CHOICE
shark = SHARK
emojifier = SHARK_EMOJIFIER
query = SHARK_QUERY


choice.connect_node(shark)
choice.connect_node(query)

shark.connect_node(emojifier)
emojifier.connect_node(choice)

query.connect_node(choice)


r = choice.run(
    input=Prompt(
        content={'input': 'Fale o nome do autor que descobriu o Squatina albipunctata'},
        role='user'
    ), 
    debug=True
)


# while True:
#     user_input = input('User: ')
#     res = a1.run(
#         input=Prompt(
#             content={'input': user_input}, 
#             role='user'
#         ), 
#         debug=True
#     )
#     print('\n\n\n')