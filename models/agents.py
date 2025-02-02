from pydantic import BaseModel
from abc import ABC, abstractmethod

class AgentSchema(ABC, BaseModel):
    # @abstractmethod
    # def branch(*args, **kwargs):
    #     ...
    @abstractmethod
    def connection_type(*args, **kwargs):
        ...

class Responder(AgentSchema):#, extra='forbid'):
    # @classmethod
    # def branch(cls):
    #     return False
    @classmethod
    def connection_type(cls):
        return '__responder_output__'

class Classifier(AgentSchema):
    # @classmethod
    # def branch(cls):
    #     return True
    
    @classmethod
    def connection_type(cls):
        return '__classifier_output__'