from dataclasses import dataclass
import json
import os
import pydantic
from typing import Literal
import pydantic.alias_generators
from utils.utils import load_keys, load_system_instruction, load_schema_examples

class CustomInputQueryPrompt(pydantic.BaseModel):
    input: str
    description: str | None = None
    output_format: str | list[str] | None = None

class CustomAutomationPrompt(pydantic.BaseModel): 
    system_instruction: str
    context_info: str | list[str] | None = None
    raw_data: str | list[str] | None = None
    input_query: list[CustomInputQueryPrompt] | None = None
    
    @pydantic.model_validator(mode='after')
    def at_least_one_field(self):
        if self.raw_data is None and self.input_query is None:
            raise ValueError(
                'Either "raw_data" or "input_query" must be provided.'
            )
        return self
    
    def to_dict(self):
        return self.model_dump()
    
class CustomAutomationModel(pydantic.BaseModel):
    automation_template: str
    replace_keys: dict[str, str]
    prompts: CustomAutomationPrompt

    def to_dict(self):
        return self.model_dump()

SkippedStr = pydantic.json_schema.SkipJsonSchema[str]
SkippedReplaceKeys = pydantic.json_schema.SkipJsonSchema[dict[str, str]]
SkippedInputQuery = pydantic.json_schema.SkipJsonSchema[list[CustomInputQueryPrompt] | None]

TemplateModels: dict = {}
def template_model(cls: type[pydantic.BaseModel]):
    name, mode = cls.__name__.split('_', maxsplit=1)
    name = pydantic.alias_generators.to_snake(name)
    TemplateModels[f"{mode.lower().replace('_', '-')}:{name}"] = cls 
    return cls

# # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # TEMPLATE MODELS # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # #

@template_model
class Summary_1_1(CustomAutomationModel):
    automation_template: Literal['1-1:summary']
    replace_keys: SkippedReplaceKeys = load_keys('1-1', 'summary')
    prompts: 'PromptSummary_1_1' = pydantic.Field(alias='data')

    model_config = {
        'json_schema_extra': {
            'examples': load_schema_examples('1-1', 'summary')
        }
    }

    class PromptSummary_1_1(CustomAutomationPrompt):
        system_instruction: SkippedStr = load_system_instruction('1-1', 'summary')
        input_query: SkippedInputQuery = None

# # # 1 -> N # # #
@template_model
class TodoList_1_N(CustomAutomationModel):
    automation_template: Literal['1-n:todo_list']
    replace_keys: SkippedReplaceKeys = load_keys('1-n', 'todo_list')
    prompts: 'PromptTodoList_1_N' = pydantic.Field(alias='data')

    model_config = {
        'json_schema_extra': {
            'examples': load_schema_examples('1-n', 'todo_list')
        }
    }

    class PromptTodoList_1_N(CustomAutomationPrompt):
        system_instruction: SkippedStr = load_system_instruction('1-n', 'todo_list')
        input_query: SkippedInputQuery = None


# # # N -> 1 # # #
@template_model
class HistorySummary_N_1(CustomAutomationModel):
    automation_template: Literal['n-1:history_summary']
    replace_keys: SkippedReplaceKeys = load_keys('n-1', 'history_summary')
    prompts: 'PromptHistorySummary_N_1' = pydantic.Field(alias='data')

    model_config = {
        'json_schema_extra': {
            'examples': load_schema_examples('n-1', 'history_summary')
        }
    }

    class PromptHistorySummary_N_1(CustomAutomationPrompt):
        system_instruction: SkippedStr = load_system_instruction('n-1', 'history_summary')

# # # N -> 1 # # #
@template_model
class Summary_N_1(CustomAutomationModel):
    automation_template: Literal['n-1:summary']
    replace_keys: SkippedReplaceKeys = load_keys('n-1', 'summary')
    prompts: 'PromptSummary_N_1' = pydantic.Field(alias='data')

    model_config = {
        'json_schema_extra': {
            'examples': load_schema_examples('n-1', 'summary')
        }
    }

    class PromptSummary_N_1(CustomAutomationPrompt):
        system_instruction: SkippedStr = load_system_instruction('n-1', 'summary')

# # # N -> N # # #
@template_model
class DailyVoipScore_N_N(CustomAutomationModel):
    automation_template: Literal['n-n:daily_voip_score']
    replace_keys: SkippedReplaceKeys = load_keys('n-n', 'daily_voip_score')
    prompts: 'PromptDailyVoipScore_N_N' = pydantic.Field(alias='data')

    model_config = {
        'json_schema_extra': {
            'examples': load_schema_examples('n-n', 'daily_voip_score')
        }
    }

    class PromptDailyVoipScore_N_N(CustomAutomationPrompt):
        system_instruction: SkippedStr = load_system_instruction('n-n', 'daily_voip_score')

@template_model
class Form_N_N(CustomAutomationModel):
    automation_template: Literal['n-n:form']
    replace_keys: SkippedReplaceKeys = load_keys('n-n', 'form')
    prompts: 'PromptForm_N_N' = pydantic.Field(alias='data')

    model_config = {
        'json_schema_extra': {
            'examples': load_schema_examples('n-n', 'form')
        }
    }

    class PromptForm_N_N(CustomAutomationPrompt):
        system_instruction: SkippedStr = load_system_instruction('n-n', 'form')

@template_model
class ScoreFuzzy_N_N(CustomAutomationModel):
    automation_template: Literal['n-n:score_fuzzy']
    replace_keys: SkippedReplaceKeys = load_keys('n-n', 'score_fuzzy')
    prompts: 'PromptScoreFuzzy_N_N' = pydantic.Field(alias='data')

    model_config = {
        'json_schema_extra': {
            'examples': load_schema_examples('n-n', 'score_fuzzy')
        }
    }

    class PromptScoreFuzzy_N_N(CustomAutomationPrompt):
        system_instruction: SkippedStr = load_system_instruction('n-n', 'score_fuzzy')

@template_model
class Summary_N_N(CustomAutomationModel):
    automation_template: Literal['n-n:summary']
    replace_keys: SkippedReplaceKeys = load_keys('n-n', 'summary')
    prompts: 'PromptSummary_N_N' = pydantic.Field(alias='data')

    model_config = {
        'json_schema_extra': {
            'examples': load_schema_examples('n-n', 'summary')
        }
    }

    class PromptSummary_N_N(CustomAutomationPrompt):
        system_instruction: SkippedStr = load_system_instruction('n-n', 'summary')

