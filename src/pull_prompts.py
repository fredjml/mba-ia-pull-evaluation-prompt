"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_NAME = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = "prompts/bug_to_user_story_v1.yml"


def _extract_role_and_template(message) -> tuple[str, str]:
    """Identifica role (system/user) e template a partir de uma mensagem do ChatPromptTemplate puxado do Hub."""
    cls_name = type(message).__name__.lower()
    if "system" in cls_name:
        role = "system"
    elif "human" in cls_name or "user" in cls_name:
        role = "user"
    else:
        role = "unknown"

    prompt = getattr(message, "prompt", None)
    template = getattr(prompt, "template", None) if prompt else None
    return role, template or ""


def pull_prompts_from_langsmith():
    """Conecta ao LangSmith e faz pull do prompt inicial (baixa qualidade)."""
    print(f"Puxando prompt do LangSmith Hub: {PROMPT_NAME}")

    pulled_prompt = hub.pull(PROMPT_NAME)

    system_prompt = ""
    user_prompt = ""
    for message in getattr(pulled_prompt, "messages", []):
        role, template = _extract_role_and_template(message)
        if role == "system":
            system_prompt = template
        elif role == "user":
            user_prompt = template

    # Fallback: prompt sem estrutura de chat (PromptTemplate simples)
    if not system_prompt and not user_prompt:
        user_prompt = getattr(pulled_prompt, "template", "")

    return {
        "bug_to_user_story_v1": {
            "description": "Prompt de baixa qualidade puxado do LangSmith Prompt Hub (ponto de partida do desafio)",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "pulled_from": PROMPT_NAME,
            "tags": ["bug-analysis", "user-story", "baixa-qualidade"],
        }
    }


def main():
    """Função principal"""
    print_section_header("Pull de Prompt do LangSmith Prompt Hub")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    try:
        prompt_data = pull_prompts_from_langsmith()
    except Exception as e:
        print(f"❌ Erro ao puxar prompt do LangSmith: {e}")
        return 1

    if not save_yaml(prompt_data, OUTPUT_PATH):
        print("❌ Falha ao salvar o prompt localmente.")
        return 1

    print(f"✅ Prompt salvo em: {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

