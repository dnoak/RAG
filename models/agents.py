from pydantic import BaseModel
from abc import ABC, abstractmethod

class AgentSchema(ABC, BaseModel):
    @classmethod
    def annotations(cls):
        stringfy = lambda d: {k: stringfy(v) if isinstance(v, dict) else str(v) for k, v in d.items()}
        return stringfy(cls.__annotations__)

    @classmethod
    @abstractmethod
    def connection_type(cls) -> str:
        ...

class Replier(AgentSchema):#, extra='forbid'):
    @classmethod
    def connection_type(cls) -> str:
        return '__responder_output__'

class Classifier(AgentSchema):
    @classmethod
    def connection_type(cls) -> str:
        return '__classifier_output__'

class Replicator(AgentSchema):
    @classmethod
    def connection_type(cls) -> str:
        return '__replicator_output__'