"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import sys
import os
from dotenv import load_dotenv
from langchain_core.prompts.chat import ChatPromptTemplate
from langsmith import Client
from typing import Dict, Any, Optional
from prompt_registry import registry
from utils import load_yaml, validate_prompt_structure

load_dotenv()

PROMPT_KEY = "bug_to_user_story"
USERNAME = os.getenv("USERNAME_LANGSMITH_HUB")

def build_prompt_template(prompt_data: Dict[str, Any]) -> ChatPromptTemplate:
    system_prompt = prompt_data.get("system_prompt", "").strip()
    user_prompt = prompt_data.get("user_prompt", "").strip()

    if not system_prompt:
        raise ValueError("Campo 'system_prompt' está vazio ou não encontrado.")

    if not user_prompt:
        raise ValueError("Campo 'user_prompt' está vazio ou não encontrado.")

    return ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", user_prompt),
        ]
    )

def build_langsmith_tags(prompt_data: Dict[str, Any]) -> list[str]:
    prompt = registry.get_prompt(PROMPT_KEY)

    tags = [
        f"v{prompt.version}",
        f"model:{prompt.model}"
    ]

    return tags

def build_langsmith_description(prompt_data: Dict[str, Any]) -> str:
    description = prompt_data.get("description", "")
    techniques = prompt_data.get("techniques_applied", [])
    input_variables = prompt_data.get("input_variables", [])

    techniques_text = ", ".join(techniques)
    input_variables_text = ", ".join(input_variables)

    return f"""
        {description}

        Techniques applied:
        {techniques_text}

        Input variables:
        {input_variables_text}
        """.strip()

def push_prompt_to_langsmith(
    client: Client,
    prompt_data: Dict[str, Any],
    prompt_template: ChatPromptTemplate
) -> bool:
    full_prompt_name = f"{USERNAME}/{PROMPT_KEY}"

    tags = build_langsmith_tags(prompt_data)
    description = build_langsmith_description(prompt_data)

    url = client.push_prompt(
        full_prompt_name,
        object=prompt_template,
        tags=tags,
        description=description
    )

    if url:
        print(f"Prompt URL: {url}")

    return url is not None


def main() -> int:
    prompt = registry.get_prompt(PROMPT_KEY)

    if prompt is None:
        print(f"Erro: prompt '{PROMPT_KEY}' não encontrado no registry.")
        return 1

    prompt_data = load_yaml(str(prompt.path))

    if prompt_data is None:
        print("Erro ao carregar prompt YAML.")
        return 1

    is_valid, errors = validate_prompt_structure(prompt_data)

    if not is_valid:
        print(f"Erros encontrados: {errors}")
        return 1
    
    prompt_template = build_prompt_template(prompt_data)

    if prompt_template is None:
        print("Erro ao carregar prompt template.")
        return 1

    client = Client()

    success = push_prompt_to_langsmith(
        client, 
        prompt_data, 
        prompt_template
    )

    if success:
        print("Prompt enviado com sucesso ao LangSmith Hub")
        return 0

    print("Erro ao enviar prompt ao LangSmith Hub")
    return 1
    

if __name__ == "__main__":
    sys.exit(main())
