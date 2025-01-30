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
from src.prompts import SystemPrompt, Prompt

debug_colors = {
    "request": "red",
    "system": "yellow",
    "assistant": "green",
    "user": "blue",
}

@dataclass
class GptLlmApi(models.ml.LlmModel):
    model_name: str
    
    def __post_init__(self):
        self.openai_client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        self.model_specs = models.gpt.GptModelSpecs(model_name=self.model_name)

    @utils.utils.Timer.timer
    def _timed_gpt_generate(
            self, system_prompt: SystemPrompt, 
            input: Prompt,
            history: list[Prompt],
            debug: bool
        ) -> Any:
        dict_messages = [{'role': h.role_format(), 'content': h.content_format()} for h in history]
        dict_messages += [{'role': input.role_format(), 'content': input.content_format()}]
        dict_messages += [{'role': system_prompt.role, 'content': system_prompt.content}]
        
        response =  self.openai_client.chat.completions.create(
            messages=dict_messages, # type: ignore
            model=self.model_name,
            max_tokens=None,
            response_format={"type": "json_object"},
        )

        if debug:
            print(f"\n\n{colored('[OPENAI REQUEST]', color='red', attrs=['bold'])}")
            for dict_message in dict_messages:
                role = dict_message['role']
                content = dict_message['content']
                print(f"{colored(f'[{role}]:', color=debug_colors[role], attrs=['bold'])}") # type: ignore
                print(f"{colored(content, debug_colors[role])}") # type: ignore

            role = response.choices[0].message.role
            content = response.choices[0].message.content
            print(f"{colored(f'[{role}]:', color=debug_colors[role], attrs=['bold'])}") # type: ignore
            print(f"{colored(content, debug_colors[role])}") # type: ignore
            print(f"{colored('[OPENAI REQUEST]', color='red', attrs=['bold'])}\n\n")
        return response

    def generate(
            self, system_prompt: SystemPrompt,
            input: Prompt,
            history: list[Prompt], 
            debug: bool = False
        ) -> models.llm.ResultsMetadata:
        
        result, process_time = self._timed_gpt_generate(system_prompt, input, history, debug)
        
        return models.llm.ResultsMetadata(
            model_name=self.model_name,
            input_text=input.content_format(),
            input_history=[h.content for h in history],
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
    
