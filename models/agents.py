from pydantic import BaseModel
from abc import ABC, abstractmethod

class AgentSchema(ABC, BaseModel):
    # @abstractmethod
    # def branch(*args, **kwargs):
    #     ...
    @classmethod
    def annotations(cls):
        stringfy = lambda d: {k: stringfy(v) if isinstance(v, dict) else str(v) for k, v in d.items()}
        return stringfy(cls.__annotations__)

    @classmethod
    @abstractmethod
    def connection_type(cls) -> str:
        ...

class Responder(AgentSchema):#, extra='forbid'):
    # @classmethod
    # def branch(cls):
    #     return False
    @classmethod
    def connection_type(cls) -> str:
        return '__responder_output__'

class Classifier(AgentSchema):
    # @classmethod
    # def branch(cls):
    #     return True
    
    @classmethod
    def connection_type(cls) -> str:
        return '__classifier_output__'