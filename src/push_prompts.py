"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header
from prompt_registry import registry
from langsmith import Client

load_dotenv()

prompt = registry.get_prompt("bug-to-user-story")
prompt_template = load_prompt(prompt.path)

client = Client()

def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    url = client.push_prompt(
    "bug-to-user-story", 
    object=prompt_template, 
    tags=[
        f"v{prompt.version}",
        f"model: {prompt.model}",
    ], 
    description=prompt.description
)

return url is not None


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    ...


def main():
    is_valid, errors = validate_prompt(prompt_template)
    if is_valid:
        push_prompt_to_langsmith(prompt.name, prompt_template)
        print(f"Prompt enviado com sucesso ao LangSmith Hub")
    else:
        print(f"Erros encontrados: {errors}")


if __name__ == "__main__":
    sys.exit(main())
