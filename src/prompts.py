from pydantic import BaseModel
from dataclasses import dataclass
from typing import Literal, Type
import typing
import json

@dataclass
class Prompt:
    content: dict
    role: Literal['user', 'assistant', 'connection']
    
    def content_format(self):
        return json.dumps(self.content, indent=4, ensure_ascii=False)
    
    def role_format(self):
        if self.role == 'connection':
            return 'assistant'
        return self.role
    

@dataclass
class SystemPrompt:
    input_schema: Type[BaseModel]
    background: str
    steps: list[str]
    output_schema: Type[BaseModel]

    def _build_output_prompt(self):
        json_schema = self.output_schema.model_json_schema()
        type_hints = typing.get_type_hints(self.output_schema)
        output_dict = {}
        
        output_instructions = '\nInformações dos campos JSON:\n'	
        for schema_key, schema_value in json_schema['properties'].items():
            output_instructions += f" - {schema_key}: {schema_value['description']}\n"
        # output_instructions += '\n'

        output_instructions += '\nFormato de resposta do JSON - siga a tipagem informada:\n' 
        for type_key, type_value in type_hints.items():
            if isinstance(type_value, type):
                type_value = type_value.__name__
            else:
                type_value = str(type_value).replace('typing.', '')
            output_dict[type_key] = f"{type_value}"
        return output_instructions + json.dumps(output_dict, indent=4, ensure_ascii=False)
    
    @property
    def role(self) -> str:
        return 'system'
    
    @property
    def content(self) -> str:
        prompt = self.background + '\n'
        for i, step in enumerate(self.steps):
            prompt += f"({i+1}) {step}\n"
        prompt += self._build_output_prompt()
        return prompt

if __name__ == '__main__':
    from data.prompts.system_prompts import DOLPHIN, SHARK, DOLPHIN_SPECIES, SHARK_SPECIALIST
    import json
    import typing

    s =  DOLPHIN_SPECIES

    tp = typing.get_type_hints(s.output_schema)
    nk = {}
    for key, value in tp.items():
        if isinstance(value, type):
            type_str = value.__name__
        else:
            type_str = str(value).replace('typing.', '')
        nk[key] = type_str

    print()
    print(s.content)
