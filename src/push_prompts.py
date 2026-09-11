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
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_FILE = "prompts/bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def build_prompt_name(username: str, prompt_data: dict) -> str:
    """Monta o nome versionado {username}/bug_to_user_story_v2."""
    version = prompt_data.get("version", "v2")
    return f"{username}/bug_to_user_story_{version}"


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_data["system_prompt"]),
            ("user", prompt_data["user_prompt"]),
        ]
    )

    techniques = prompt_data.get("techniques_applied", [])
    description = (
        f"{prompt_data.get('description', '').strip()} "
        f"| Técnicas: {', '.join(techniques)} | Base: {prompt_data.get('base_prompt', 'N/A')}"
    ).strip()

    client = Client()
    url = client.push_prompt(
        prompt_name,
        object=template,
        is_public=True,
        description=description,
        tags=prompt_data.get("tags", []),
    )

    print(f"   ✓ Publicado em: {url}")
    return True


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    for field in ("description", "system_prompt", "user_prompt", "version"):
        if not prompt_data.get(field, "").strip():
            errors.append(f"Campo obrigatório vazio ou ausente: {field}")

    if "[TODO]" in prompt_data.get("system_prompt", ""):
        errors.append("system_prompt ainda contém [TODO]")

    if len(prompt_data.get("techniques_applied", [])) < 2:
        errors.append("techniques_applied precisa ter ao menos 2 técnicas")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    print_section_header("Push de Prompt Otimizado para o LangSmith Hub")

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    all_prompts = load_yaml(PROMPT_FILE)
    if not all_prompts or PROMPT_KEY not in all_prompts:
        print(f"❌ Não foi possível carregar '{PROMPT_KEY}' de {PROMPT_FILE}")
        return 1

    prompt_data = all_prompts[PROMPT_KEY]

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for error in errors:
            print(f"   - {error}")
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")
    prompt_name = build_prompt_name(username, prompt_data)

    try:
        push_prompt_to_langsmith(prompt_name, prompt_data)
    except Exception as e:
        print(f"❌ Erro ao publicar prompt: {e}")
        return 1

    print(f"✅ Prompt publicado como público: {prompt_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
