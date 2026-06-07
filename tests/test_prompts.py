"""
Testes automatizados para validação de prompts.
"""
from queue import Empty
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def fetch_prompt_data():
    prompt_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
    return load_prompts(str(prompt_path))

class TestPrompts:

    prompt_data = fetch_prompt_data()
    
    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""        
        assert "system_prompt" in self.prompt_data, "Campo 'system_prompt' ausente"
        assert str(self.prompt_data["system_prompt"]).strip() != "", "Campo 'system_prompt' está vazio"

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        assert "system_prompt" in self.prompt_data, "Campo 'system_prompt' ausente"
        system_prompt_text = self.prompt_data["system_prompt"].lower()
        assert "você é" in system_prompt_text or "voce e" in system_prompt_text, "Definição de persona ('você é...') ausente no system_prompt"

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        assert "system_prompt" in self.prompt_data, "Campo 'system_prompt' ausente"
        combined = self.prompt_data["system_prompt"].lower()
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
        assert has_user_story_format or has_markdown_format, "Prompt não exige formato Markdown ou User Story padrão"

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        assert "system_prompt" in self.prompt_data, "Campo 'system_prompt' ausente"
        system_prompt_text = self.prompt_data["system_prompt"]
        idx = system_prompt_text.find("Exemplos:")
        assert idx != -1, "Seção 'Exemplos' não encontrada no prompt"        
        examples_yaml = yaml.safe_load(system_prompt_text[idx:])
        examples_section = examples_yaml.get("Exemplos", {})
        
        assert examples_section, "Seção 'Exemplos' não encontrada no prompt"
        
        for example_name, example_content in examples_section.items():
            assert "input" in example_content, "input não contém exemplos"
            assert "output" in example_content, "output não contém exemplos"
            assert example_content["input"], "input não contém exemplos"
            assert example_content["output"], "output não contém exemplos"

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        prompt_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "[TODO]" not in content, "Prompt ainda contém [TODOs]"

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = self.prompt_data.get("techniques_applied", [])
        assert len(techniques) >= 2, f"Espera-se pelo menos 2 técnicas, encontradas: {len(techniques)}"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])