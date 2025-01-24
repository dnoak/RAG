from dataclasses import dataclass
import functools
import json
import models.llm
from abc import ABC, abstractmethod

class LlmModel(ABC):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "generate" in cls.__dict__:
            original_generate = cls.__dict__["generate"]

            @functools.wraps(original_generate)
            def wrapped_generate(self, *args, **kwargs):
                result = original_generate(self, *args, **kwargs)
                return self.validate_output(result, *args, **kwargs)
            
            setattr(cls, "generate", wrapped_generate)

    def validate_output(self, result, *args, **kwargs):
        dict_result = json.loads(result.output_text)
        assert kwargs['system_prompt'].output_schema(**dict_result)
        wrapper_key = str(kwargs['system_prompt'].output_schema.action())
        result.output_dict = {wrapper_key: dict_result}
        return result

    @abstractmethod
    def generate(self, *args, **kwargs) -> models.llm.ResultsMetadata:
        """Método abstrato a ser implementado pelas subclasses."""
        pass
