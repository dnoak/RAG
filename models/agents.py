from pydantic import BaseModel
from abc import ABC, abstractmethod

class AgentSchema(ABC, BaseModel):
    @abstractmethod
    def branch(*args, **kwargs):
        ...

class Response(AgentSchema):#, extra='forbid'):
    @classmethod
    def branch(cls):
        return False

class Choice(AgentSchema):
    @classmethod
    def branch(cls):
        return True