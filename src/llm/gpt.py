import json
import logging
import os
import random
import re
from typing import Any
from types import SimpleNamespace
from openai import OpenAI
from dataclasses import dataclass
from termcolor import colored
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
    
    def debug(self, messages: list[dict], result: Any) -> None:
        chat_colors = {
            "system": "yellow",
            "assistant": "green",
            "user": "blue",
        }
        for message in messages:
            print(
                colored(f"[{message['role']}]:", color=chat_colors[message['role']], attrs=['bold']),
                colored(message['content'], chat_colors[message['role']])
            )
        print(
            colored(f"[{result.choices[0].message.role}]:", color=chat_colors[result.choices[0].message.role], attrs=['bold']),
            colored(result.choices[0].message.content, chat_colors[result.choices[0].message.role])
        )
    
    def generate(self, messages: list[dict], debug: bool = False) -> models.llm.ResultsMetadata:
        result, process_time = self._timed_gpt_generate(messages=messages)
        if debug: self.debug(messages, result)
        
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
    fake_process_time: float = 0.1234

    def __post_init__(self):
        super().__post_init__()
        self._timed_gpt_generate: function = self._mock_timed_gpt_generate

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
        return self._generate_api_response(
            input_prompts=''.join([m['content'] for m in kwargs['messages']]),
            fake_llm={'[Fake] response': ['1', '2', '3']}
        )
    
