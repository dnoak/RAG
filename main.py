from src.prompts import Prompt
from src.agent import Agent
from agents.emoji_shark_2 import SHARK_SYS_PROMPT, SHARK_EMOJI
from src.llm.gpt import GptLlmApi

# r = EMOJI_SHARK_AGENT.run(
#     input=Prompt(
#         content={'input': 'Olá'}, 
#         role='user'
#     ), 
#     debug=True
# )

# while True:
#     user_input = input('User: ')
#     res = EMOJI_SHARK_AGENT.run(
#         input=Prompt(
#             content={'input': user_input}, 
#             role='user'
#         ), 
#         debug=True
#     )
#     print('\n\n\n')

#     [print(r) for r in res]

a1 = Agent(
    name='Shark Specialist',
    system_prompt=SHARK_SYS_PROMPT,
    role='connection',
    input_processor=lambda x: {'input': input('User: ')},
    llm_model=GptLlmApi(model_name='gpt-4o-mini'),
)

a2 = Agent(
    name='Shark Emojifier',
    system_prompt=SHARK_EMOJI,
    role='assistant',
    llm_model=GptLlmApi(model_name='gpt-4o-mini'),
)

a1.connect(a2)
a2.connect(a1)

r = a1.run(
    input=Prompt(
        content={}, 
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