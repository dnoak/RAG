import json
import logging
import os
import random
import re
from typing import Any
from types import SimpleNamespace
from openai import OpenAI
from dataclasses import dataclass
import time
import ast
import utils.utils
import models.gpt
import models.llm
import models.ml

@dataclass
class GptLlmApi(models.ml.LlmModel):
    model_name: str
    
    def __post_init__(self):
        self.openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        self.model_specs = models.gpt.GptModelSpecs(model_name=self.model_name)

    @utils.utils.Timer.timer
    def _timed_gpt_generate(self, messages: list[dict]) -> Any:
        return self.openai_client.chat.completions.create(
            messages=messages, # type: ignore
            model=self.model_name,
            max_tokens=None,
            response_format={"type": "json_object"},
        )
    
    def generate(self, messages: list[dict]) -> models.llm.ResultsMetadata:
        result, process_time = self._timed_gpt_generate(messages)
        return models.llm.ResultsMetadata(
            model_name=self.model_name,
            input_text=''.join([m['content'] for m in messages]),
            input_tokens=result.usage.prompt_tokens,
            output_text=result.choices[0].message.content,
            output_tokens=result.usage.completion_tokens,
            process_time=process_time
        )

@dataclass
class FakeGptLlmApi(GptLlmApi):
    fake_process_time: float = 1.1234
    # faker = Faker()

    def __post_init__(self):
        super().__post_init__()
        self._timed_gpt_generate: function = self._mock_timed_gpt_generate
    
    def _decode_stringfied_data(self, encoded_str: str) -> list[dict]:
        pattern = re.compile(r'\[(\d+)\](.*?)\n\n', re.DOTALL)
        matches = pattern.findall(encoded_str.strip())
        result = []
        for match in matches:
            index, content = match
            lines = content.strip().split('\n')
            if len(lines) < 2:
                continue
            input_data = lines[0].split(':', 1)[1].strip()
            response_format = lines[1].split(':', 1)[1].strip()
            result.append({
                'input': input_data,
                'output_format': ast.literal_eval(response_format)
            })
        return result
    
    def _generate_api_response(self, input_prompts, fake_llm):
        content = json.dumps(fake_llm, indent=4, ensure_ascii=False)
        response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content))],
            usage=SimpleNamespace(
                prompt_tokens = len(self.model_specs.encoder.encode(input_prompts)),
                completion_tokens = len(self.model_specs.encoder.encode(content)))
        )
        return response

    @utils.utils.Timer.timer
    def _mock_timed_gpt_generate(self, **kwargs) -> Any:
        time.sleep(self.fake_process_time)
        input_list = self._decode_stringfied_data(kwargs['input_query'])
        fake_llm = {
            i: random.choice(data['output_format']) 
            for i, data in enumerate(input_list)
        }
        return self._generate_api_response(
            input_prompts=''.join([v for v in kwargs.values()]),
            fake_llm=fake_llm)
    
