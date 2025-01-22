from pydantic import BaseModel, Field
from dataclasses import dataclass, field
import datetime
from typing import Literal, Type
import re
import json

@dataclass
class OutputSchema:
    schema: Type[BaseModel] | BaseModel
    attribute_keys: dict[str, str] = field(
        default_factory=lambda: {
            'type': 'Tipo',
            'anyOf': 'Tipos',
            'enum': 'Tipo Literal',
            'description': 'Descrição',
            'required': 'Obrigatório',
        }
    )

    def build(self) -> str:
        prompt_dict = ['{']
        json_schema = self.schema.model_json_schema()
        required = json_schema['required'] if 'required' in json_schema else []
        for property, attribute in json_schema['properties'].items():
            prompt_dict.append(f'{" "*4}"{property}": "..."')
            for attribute_key, attribute_value in attribute.items():
                if attribute_key in self.attribute_keys:
                    prompt_dict.append(f'{" "*8}// - {self.attribute_keys[attribute_key]}: {attribute_value}')
            if property in required:
                prompt_dict.append(f'{" "*8}// - {self.attribute_keys["required"]}: true')
            else:
                prompt_dict.append(f'{" "*8}// - {self.attribute_keys["required"]}: false')

        return '\n'.join(prompt_dict) + '\n}'

@dataclass
class SystemPrompt:
    background: str
    steps: list[str]
    output: str | OutputSchema

    def build(self):
        prompt = self.background + '\n'
        for i, step in enumerate(self.steps):
            prompt += f"({i+1}) {step}\n"
        prompt += '\nFormato de resposta com sua estrutura comentada (com //):\n\n'
        prompt += self.output if isinstance(self.output, str) else self.output.build()
        return prompt


if __name__ == '__main__':
    s = SystemPrompt(
        background='Você é um assistente virtual que monta queries estruturadas em JSON de perguntas sobre golfinhos.',   
        steps=[
            'Você irá preencher as informações do golfinho na query caso elas estejam explícitas ou implícitas na pergunta.',
            'caso a pergunta não seja sobre golfinhos, preencha a query com onomatopeias do fundo do mar com emojis',
        ],
        output=OutputSchema(schema=ComplexDolphinOutput()).build()
    )

    print()
    print(s.build())
