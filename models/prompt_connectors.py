from pydantic import BaseModel as PydanticBaseModel

class BaseModel(PydanticBaseModel, extra='forbid'):
    pass

class PlainTextOutput(BaseModel):
    @staticmethod
    def action() -> str:
        return 'text'

class ApiCallOutput(BaseModel):
    @staticmethod
    def action() -> str:
        return 'api_call'

class SelectorOutput(BaseModel):
    @staticmethod
    def action() -> str:
        return 'selector'