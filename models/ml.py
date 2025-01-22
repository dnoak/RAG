from dataclasses import dataclass
import models.llm
from abc import abstractmethod

@dataclass
class LlmModel:
    @abstractmethod
    def generate(*args, **kwargs) -> models.llm.ResultsMetadata: ...
