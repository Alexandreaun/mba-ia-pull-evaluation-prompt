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

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def fetch_prompt_data():
    prompt_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
    return load_prompts(str(prompt_path))

class TestPrompts:
    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        prompt_data = fetch_prompt_data()
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' não encontrado no YAML"
        assert prompt_data["system_prompt"].strip(), "Campo 'system_prompt' está vazio"

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        prompt_data = fetch_prompt_data()
        assert "persona" in prompt_data, "Campo 'persona' não encontrado no YAML"
        persona = prompt_data["persona"].strip()
        assert persona, "Campo 'persona' está vazio"
        persona_lower = persona.lower()
        assert "você é" in persona_lower or "voce e" in persona_lower, (
        "Persona deve definir um papel (ex: 'Você é um Product Manager')"
    )

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        prompt_data = fetch_prompt_data()
        text_fields = [
        prompt_data.get("system_prompt", ""),
        prompt_data.get("output_format", ""),
        prompt_data.get("user_prompt", ""),
    ]
        combined = "\n".join(text_fields).lower()
        has_user_story_format = (
            "como um" in combined
            and "eu quero" in combined
            and "para que" in combined
    )
        has_markdown_format = (
            "markdown" in combined
            or "# user story" in combined
            or "## critérios" in combined
    )
        assert has_user_story_format or has_markdown_format, (
            "Prompt deve exigir formato User Story padrão "
            "(Como um / Eu quero / Para que) ou formato Markdown"
    )

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        prompt_data = fetch_prompt_data()
        examples = prompt_data["examples"]
        assert len(examples) >= 2, (
            f"Few-shot requer pelo menos 2 exemplos, encontrados: {len(examples)}"
    )
        for i, example in enumerate(examples, start=1):
            assert "input" in example, f"Exemplo {i} não possui 'input'"
            assert "output" in example, f"Exemplo {i} não possui 'output'"
            bug_report = example["input"].get("bug_report", "").strip()
            reference = example["output"].get("reference", "").strip()
            assert bug_report, f"Exemplo {i}: 'input.bug_report' está vazio"
            assert reference, f"Exemplo {i}: 'output.reference' está vazio"

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        prompt_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "[TODO]" not in content, "Prompt ainda contém [TODOs]"

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        prompt_data = fetch_prompt_data()
        techniques = prompt_data["techniques"]
        assert len(techniques) >= 2, (
            f"É necessário pelo menos 2 técnicas aplicadas, encontrados: {len(techniques)}"
    )

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])