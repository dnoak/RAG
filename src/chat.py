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

    def system(self, message: str) -> 'Chat':
        self.history.append(Message(role="system", content=message))
        return self

    def assistant(self, message: str) -> 'Chat':
        self.history.append(Message(role="assistant", content=message))
        return self

    def user(self, message: str) -> 'Chat':
        self.history.append(Message(role="user", content=message))
        return self
    
    # @staticmethod
    # def debug(history: list[Message] | list[dict]) -> None:
    #     chat_colors = {
    #         "system": "yellow",
    #         "assistant": "green",
    #         "user": "blue",
    #     }
    #     for message in history:
    #         if isinstance(message, dict):
    #             message = Message(**message)
    #         print(
    #             colored(f"[{message.role}]:", color=chat_colors[message.role], attrs=['bold']),
    #             colored(message.content, chat_colors[message.role])
    #         )

    def format(self) -> list[dict]:
        history = filter(lambda x: x.role != 'system', self.history)
        history = list(map(lambda x: x.dump(), history))
        return history
    
    def process(self, use_history: bool, debug: bool = False) -> 'Chat':
        assert self.history[-1].role == 'user'
        history = self.format()
        last_system = list(filter(lambda x: x.role == 'system', self.history))[-1]
        history.insert(-1, last_system.dump())
        
        if use_history:
            history = history[-self.history_size:]
        else:
            history = history[-2:]
        
        response = self.llm_model.generate(
            messages=history,
            debug=debug
        )
        self.output_metadata.append(response)
        self.assistant(response.output_text)
        
        # if debug:
        #     history.append(self.history[-1].dump())
        #     self.debug(history)
                
        return self



if __name__ == '__main__':
    from src.llm.gpt import GptLlmApi, FakeGptLlmApi
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


