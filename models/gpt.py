from dataclasses import dataclass, field
from typing import Literal
import tiktoken
import models.llm

@dataclass
class GptModelSpecs(models.llm.ModelSpecs):
    model_name: str

    def __post_init__(self):
        self._models_data = {
            'gpt-4o-mini': {
                'context_window': 128_000,
                'max_output_tokens': ...,
                'input_token_price': 0.15/1e6, # per 1M tokens
                'output_token_price': 0.6/1e6, # per 1M tokens
            },
            'gpt-4o': {
                'context_window': 128_000,
                'max_output_tokens': ...,
                'input_token_price': 5/1e6, # per 1M tokens
                'output_token_price': 15/1e6, # per 1M tokens
            }
        }

    @property
    def encoder(self):
        return tiktoken.encoding_for_model(self.model_name)
    
    @property
    def context_window(self):
        return self._models_data[self.model_name]['context_window']
    
    @property
    def max_output_tokens(self):
        return self._models_data[self.model_name]['max_output_tokens']
    
    @property
    def input_token_price(self):
        return self._models_data[self.model_name]['input_token_price']
    
    @property
    def output_token_price(self):
        return self._models_data[self.model_name]['output_token_price']