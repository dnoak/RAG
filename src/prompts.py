from pydantic import BaseModel
from dataclasses import dataclass
from typing import Literal, Type
from models.agents import AgentSchema
import typing
import json

@dataclass
class Prompt:
    contents: list[dict]
    role: Literal['user', 'assistant', 'user:connection']
    
    def content_format(self, show_connection_type: bool = False):
        if not show_connection_type:
            valid_contents = [
                {k: v for k, v in content.items() if not k.startswith('__')}
                for content in self.contents
            ]
        else:
            valid_contents = self.contents
        formatted = []
        for index, valid_content in enumerate(valid_contents):
            formatted.append(f'Input [{index}]:\n')
            keys = list(valid_content.keys())
            if len(keys) == 1:
                formatted.append(str(valid_content[keys[0]]) + '\n\n')
            else:
                formatted.append(json.dumps(valid_content, indent=4, ensure_ascii=False) + '\n\n')
        if len(formatted) == 2:
            return formatted[1]
        return ''.join(formatted)
    
    def role_format(self):
        if self.role == 'user:connection':
            return 'user'
        return self.role
    

@dataclass
class SystemPrompt:
    background: str
    steps: list[str]
    output_schema: Type[AgentSchema]

    def _build_output_prompt(self):
        json_schema = self.output_schema.model_json_schema()
        type_hints = typing.get_type_hints(self.output_schema)
        output_dict = {}
        
        output_instructions = '\nInformações dos campos JSON:\n'	
        for schema_key, schema_value in json_schema['properties'].items():
            output_instructions += f" - {schema_key}: {schema_value['description']}\n"

        output_instructions += '\nFormato de resposta do JSON - '
        output_instructions += 'Siga a tipagem baseada no typing do Python\n'
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
    # test

    p = Prompt(
        contents=[
            {'output': 'saída do agente 1'},
            {'output': 'saída do agente 2'},
            {'output': 'saída do agente 3'},
        ],
        role='user'
    )

    p2 = Prompt(
        contents=[
            {'output1': 'saída do agente 1'},
            {'output2': 'saída do agente 2'},
            {'output3': 'saída do agente 3'},
        ],
        role='user'
    )

    p3 = Prompt(
        contents=[
            {'output1': 'saída do agente 1', 'output11': 'saída do agente 2'},
            {'output2': 'saída do agente 2', 'output22': 'saída do agente 3'},
            {'output3': 'saída do agente 3'},
        ],
        role='user:connection'
    )

    p4 = Prompt(
        contents=[
            {'output1': 'saída do agente 1'}
        ],
        role='user:connection'
    )

    p5 = Prompt(
        contents=[
            {'output1': 'saída do agente 1', 'output11': 'saída do agente 2'},
        ],
        role='user'
    )

    print(p.content_format())
    print('\n\n')
    print(p2.content_format())
    print('\n\n')
    print(p3.content_format())
    print('\n\n')
    print(p4.content_format())
    print('\n\n')
    print(p5.content_format())