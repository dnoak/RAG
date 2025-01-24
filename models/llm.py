import dataclasses
from dataclasses import dataclass
from typing import Any, Optional
from abc import abstractmethod

@dataclass
class DefaultModel:
    def to_dict(self):
        return dataclasses.asdict(self)

@dataclass
class CostsMetadata(DefaultModel):
    model_name: str
    currency: str
    input_token_price: float
    output_token_price: float
    input_costs: float
    output_costs: float
    total: float

@dataclass
class ResultsMetadata(DefaultModel):
    model_name: str
    input_text: str
    input_tokens: int
    output_text: str
    output_dict: Optional[dict]
    output_tokens: int
    process_time: float

@dataclass
class FormattedResults(DefaultModel):
    results: list[dict]
    costs: CostsMetadata
    process_time: float

@dataclass
class ModelSpecs(DefaultModel):
    model_name: str

    @property
    @abstractmethod
    def encoder(self) -> Any: ...
    
    @property
    @abstractmethod
    def context_window(self) -> int: ...
    
    @property
    @abstractmethod
    def max_output_tokens(self) -> int: ...
    
    @property
    @abstractmethod
    def input_token_price(self) -> float: ...
    
    @property
    @abstractmethod
    def output_token_price(self) -> float: ...