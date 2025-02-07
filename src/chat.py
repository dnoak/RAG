from dataclasses import dataclass, field
from src.prompts import Prompt, SystemPrompt
from agent import Agent
import models.llm

@dataclass
class Chat:
    llm_model: str
    history_size: int
    history: list[Prompt | SystemPrompt] = field(default_factory=list)
    metadata_history: list[models.llm.ResultsMetadata] = field(default_factory=list)

    def format_history(self):
        
 
    def process(self, agent: Agent, input: dict, debug: bool = False):
        agent.run(
            input=Prompt(
                content=input, 
                role='user'
            ),
            history=self.history, 
            debug=debug
        )
        

        
    