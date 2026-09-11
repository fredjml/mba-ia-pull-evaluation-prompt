"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = str(Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml")
PROMPT_KEY = "bug_to_user_story_v2"

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class TestPrompts:
    @pytest.fixture(autouse=True)
    def _load_v2(self):
        self.all_prompts = load_prompts(PROMPT_FILE)
        self.prompt = self.all_prompts[PROMPT_KEY]

    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert self.prompt.get("system_prompt", "").strip() != ""

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        system_prompt = self.prompt.get("system_prompt", "").lower()
        assert "você é" in system_prompt

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = self.prompt.get("system_prompt", "").lower()
        assert "markdown" in system_prompt and "user story" in system_prompt

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = self.prompt.get("system_prompt", "").lower()
        assert system_prompt.count("relato de bug") >= 2 and "exemplo" in system_prompt

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        full_text = yaml.dump(self.all_prompts, allow_unicode=True)
        assert "[TODO]" not in full_text

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        is_valid, errors = validate_prompt_structure(self.prompt)
        techniques = self.prompt.get("techniques_applied", [])
        assert len(techniques) >= 2
        assert not any("técnicas" in error for error in errors)

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])