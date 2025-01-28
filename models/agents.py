from pydantic import BaseModel
from abc import ABC, abstractmethod

class AgentSchema(ABC, BaseModel):
    @abstractmethod
    def branch(*args, **kwargs):
        ...

class Responser(AgentSchema):#, extra='forbid'):
    @classmethod
    def branch(cls):
        return False

class Classifier(AgentSchema):
    @classmethod
    def branch(cls):
        return True