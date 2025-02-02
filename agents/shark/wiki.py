from dataclasses import dataclass
from typing import Optional
from pydantic import Field
import requests
from src.prompts import SystemPrompt
from src.agent import Agent
from src.llm.gpt import GptLlmApi
from models.agents import Responder, Classifier
import networkx as nx
import json
from src.agent import AgentProcessor
from db.shark.elastic import ElasticShark

@dataclass
class WikipediaSearcher:
    url: str = "https://pt.wikipedia.org/w/api.php"

    def search_page(self, query: str) -> tuple[str, str] | None:
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query
        }
        response = requests.get(self.url, params=params)
        data = response.json()

        if "query" in data and "search" in data["query"]:
            page_title = data["query"]["search"][0]["title"]
            page_url = f"https://pt.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
            return page_title, page_url
        else:
            return None
    
    def get_introduction(self, page_title: str) -> str:
        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "explaintext": True,
            "exintro": True,
            "titles": page_title
        }
        response = requests.get(self.url, params=params)
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if "extract" in page_data:
                return page_data["extract"]
        return "Texto não encontrado."


class SharkWikipediaInput(Responder):
    user_input: str = Field(
        description="A pergunta que o usuário fez"
    )

class SharkPromptWikipediaOutput(Responder):
    page_title: str = Field(
        description="Palavra-chaves para fazer uma busca da url da Wikipedia"
    )

class SharkWikipediaOutput(Responder):
    output: str = Field(
        description="Introdução da Wikipédia sobre o assunto" 
    )

class SharkWikipediaProcessor(AgentProcessor):
    searcher: WikipediaSearcher = WikipediaSearcher()

    def process(self, *args, **kwargs) -> dict:
        search = kwargs['llm_output']['page_title']
        results = self.searcher.search_page(search)
        if results is None:
            return {'output': 'Nenhuma página encontrada'}
        page_title, page_url = results
        introduction = f"Página encontrada: {page_url}\n\n"
        introduction += self.searcher.get_introduction(page_title)
        return {'output': introduction}
        
shark_wikipedia_prompt = SystemPrompt(
    background='Você é um assistente especialista em fazer queries de busca de páginas da Wikipedia e sempre responde no formato JSON.',
    steps=[
        'A partir da pergunta do usuário, filtre apenas as palavras-chaves relevantes para a busca sobre o assunto da Wikipedia',
    ],
    output_schema=SharkPromptWikipediaOutput
)

def shark_wikipedia(graph: Optional[nx.DiGraph] = None):
    return Agent(
        name='shark_wikipedia',
        llm_model=GptLlmApi(model_name='gpt-4o-mini'),
        system_prompt=shark_wikipedia_prompt,
        role='user:connection',
        input_schema=SharkWikipediaInput,
        output_schema=SharkWikipediaOutput,
        processor=SharkWikipediaProcessor(),
        graph=graph
    )