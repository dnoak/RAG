from dataclasses import dataclass, field, asdict
from termcolor import cprint, colored
import models.ml
import models.llm

@dataclass
class Message:
    role: str
    content: str

    def dump(self):
        return asdict(self)


@dataclass
class Chat:
    llm_model: models.ml.LlmModel
    history_size: int
    history: list[Message] = field(default_factory=list)
    output_metadata: list[models.llm.ResultsMetadata] = field(default_factory=list)

    def __post_init__(self):
        self.chat_colors = {
            "system": "yellow",
            "assistant": "green",
            "user": "blue",
        }

    def system(self, message: str) -> 'Chat':
        self.history.append(Message(role="system", content=message))
        return self

    def assistant(self, message: str) -> 'Chat':
        self.history.append(Message(role="assistant", content=message))
        return self

    def user(self, message: str) -> 'Chat':
        self.history.append(Message(role="user", content=message))
        return self
    
    def debug(self) -> None:
        for message in self.history:
            print(
                colored(f"[{message.role}]:", color=self.chat_colors[message.role], attrs=['bold']),
                colored(message.content, self.chat_colors[message.role])
            )

    def format(self, last_n_system_messages: int = 0) -> list[dict]:
        history = []
        for h in self.history[::-1]:
            if h.role == 'system':
                if last_n_system_messages > 0: 
                    history.append(h)
                    last_n_system_messages -= 1
            else:
                history.append(h)
        history = list(map(lambda x: x.dump(), history))
        return history[::-1]#[-self.max_messages:]
    
    def process(self, single_message: bool, last_n_system_messages: int = 1) -> 'Chat':
        if single_message:
            user = self.history[-1]
            assert user.role == 'user'
            system = list(filter(lambda x: x.role == 'system', self.history))[-1]
            history = [system.dump(), user.dump()]
        else:
            history = self.format(
                last_n_system_messages=last_n_system_messages
            )[-self.history_size:]
        
        response = self.llm_model.generate(
            messages=history
        )
        self.output_metadata.append(response)
        self.assistant(response.output_text)
        return self




if __name__ == '__main__':
    from main.llm.gpt import GptLlmApi, FakeGptLlmApi
    chat = Chat(
        llm_model=FakeGptLlmApi(model_name='gpt-4o-mini'),
        max_messages=5
    )
    # chat.system('[1] - system')
    # chat.assistant('[2] - assistant')
    # chat.user('[3] - user')
    # chat.assistant('[4] - assistant')
    # chat.user('[5] - user')
    # chat.assistant('[6] - assistant')
    # chat.user('[7] - user')
    # chat.system('[8] - system')
    # chat.system('[9] - system')
    # chat.user('[10] - user')

    # print()
    # chat.debug()
    # [print(x) for x in chat.format(last_n_system_messages=1)]

    chat.system

