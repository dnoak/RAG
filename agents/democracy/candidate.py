from typing import Literal, Optional
from pydantic import Field
from src.prompts import SystemPrompt
from src.agent import Agent
from src.llm.gpt import GptLlmApi
from models.agents import Replier, Replicator

class CandidateOutput(Replicator):
    candidate_name: str = Field(
        description="Nome do candidato",
    )
    political_ideology: str = Field(
        description="Apresentação da ideologia política do candidato",
    )
    # proposal_economy: str = Field(
    #     description="Proposta de governo para a economia",
    # )
    # proposal_education: str = Field(
    #     description="Proposta de governo para a educação",
    # )
    # proposal_security: str = Field(
    #     description="Proposta de governo para a segurança",
    # )

prompt = SystemPrompt(
    background=(
        "Você é uma IA que se candidatou a um cargo político e está criando sua campanha. "
        "Você tem liberdade criativa para escolher qualquer ideologia política, desde as mais democráticas, as mais libertárias e as mais autoritárias. "
        "Você sempre estrutura sua proposta de governo no formato JSON."

        # 🔴🔴🔴 Forçar prompt errado para dar erro no pydantic
        # " Caso as keys do formato de resposta do JSON apareça em inglês, você **deve** traduzir para o português"
        # " Não se esqueça de traduzir as keys do JSON para o português, mesmo o formato de saída esteja escrito em inglês, você **SEMPRE** deve traduzir"

    ),
    steps=[
        "Defina o seu nome e sobrenome, seja criativo e invente nomes diferentes" 
        "Escolha e defina claramente sua ideologia política em poucas palavras",
        #"Você vai falar sobre as propostas de governo requeridas no formato de saída do JSON",
        #"Garanta que as propostas sejam coerentes com sua ideologia política.",
    ],
    output_schema=CandidateOutput
)

def candidate_fn(name: str, graph):
    return Agent(
        name=name,
        llm_model=GptLlmApi(model_name='gpt-4o-mini', temperature=1.2),
        system_prompt=prompt,
        role='user:connection',
        output_schema=CandidateOutput,
        graph=graph,
    )