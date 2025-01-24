from dataclasses import dataclass, field, asdict
from typing import Type
from pydantic import BaseModel
import json
from src.prompts import SystemPrompt, AssistantPrompt, UserPrompt
import models.ml
import models.llm

@dataclass
class ChatActions:
    

@dataclass
class Chat:
    llm_model: models.ml.LlmModel
    history_size: int
    history: list[SystemPrompt | AssistantPrompt | UserPrompt] = field(default_factory=list)
    output_metadata: list[models.llm.ResultsMetadata] = field(default_factory=list)

    def system(self, prompt: SystemPrompt) -> 'Chat':
        self.history.append(prompt)
        return self

    def assistant(self, prompt: AssistantPrompt) -> 'Chat':
        self.history.append(prompt)
        return self

    def user(self, prompt: UserPrompt) -> 'Chat':
        self.history.append(prompt)
        return self

    def format(self) -> list[UserPrompt | AssistantPrompt | SystemPrompt]:
        return list(filter(lambda x: x.role != 'system', self.history))
    
    def agents(self):
        ...
    
    def process(self, use_history: bool, debug: bool = False) -> 'Chat':
        assert self.history[-1].role == 'user'

        history = self.format()
        history = history[-self.history_size:] if use_history else [history[-1]]

        system_prompt = list(filter(lambda x: x.role == 'system', self.history))[-1]
        
        response = self.llm_model.generate(
            system_prompt=system_prompt,
            messages=history,
            debug=debug
        )
        print(json.dumps(response.output_dict, indent=4, ensure_ascii=False))
        self.output_metadata.append(response)
        
        self.assistant(AssistantPrompt(content=response.output_text))

        return self

if __name__ == '__main__':
    from src.llm.gpt import GptLlmApi, FakeGptLlmApi
    from data.prompts.system_prompts import DOLPHIN, SHARK, DOLPHIN_SPECIES, SHARK_SPECIALIST
    
    chat = Chat(
        llm_model=FakeGptLlmApi(model_name='gpt-4o-mini'),
        history_size=5
    )
    chat.system('[1] - system')
    chat.assistant('[2] - assistant')
    chat.user('[3] - user')
    chat.assistant('[4] - assistant')
    chat.user('[5] - user')
    chat.assistant('[6] - assistant')
    chat.user('[7] - user')
    chat.system('[8] - system')
    chat.system('[9] - system')
    chat.user('[10] - user')

    print()

    chat.process(single_message=False)


