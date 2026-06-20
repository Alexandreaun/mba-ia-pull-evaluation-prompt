from langsmith.evaluation import evaluate
from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT
from pathlib import Path
from langsmith.wrappers import wrap_openai
from openai import OpenAI
import yaml
import os
from typing import Any, Dict, Literal
from dotenv import load_dotenv
from prompt_evaluator_f1 import f1_score_evaluator

load_dotenv()

DATASET_NAME = "bug_to_user_story"
BASE_DIR = Path(__file__).parent

def get_openai_client():
    return wrap_openai(OpenAI())

# Setup
oai_client = get_openai_client()

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def fetch_prompt_data():
    prompt_path = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
    return load_prompts(str(prompt_path))

prompt = fetch_prompt_data()


def execute_text_prompt(
    prompt_data: Dict[str, Any],
    inputs: dict,
    oai_client,
    input_key: str = "bug_report",
    model: str | None = None,
    temperature: float | None = None,
    instruction_role: Literal["developer", "system"] = "developer",
) -> dict:
    if model is None:
        model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    if temperature is None:
        temperature = float(os.getenv("LLM_TEMPERATURE", "0"))

    if input_key not in inputs:
        raise KeyError(
            f"Input obrigatório '{input_key}' não encontrado. "
            f"Inputs recebidos: {list(inputs.keys())}"
        )

    system_prompt = prompt_data.get("system_prompt", "").strip()
    user_prompt = prompt_data.get("user_prompt", "").strip()

    if not system_prompt:
        raise ValueError("Campo 'system_prompt' está vazio ou não encontrado.")

    if not user_prompt:
        raise ValueError("Campo 'user_prompt' está vazio ou não encontrado.")

    formatted_user_prompt = user_prompt.format(
        bug_report=inputs[input_key]
    )

    response = oai_client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {
                "role": instruction_role,
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": formatted_user_prompt,
            },
        ],
    )

    user_story = response.choices[0].message.content or ""

    return {
        "user_story": user_story.strip()
    }

def run_evaluators(inputs: dict) -> dict:
    """Target function for evaluate()."""
    return execute_text_prompt(prompt, inputs, oai_client, input_key="bug_report")

# Evaluators
correctness_evaluator = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT,
    feedback_key="correctness",
    model=os.getenv("EVAL_MODEL", ""),
    continuous=True
)

helpfulness_judge = create_llm_as_judge(
    prompt="""
Você está avaliando o quão útil é a resposta gerada.

RELATO DO BUG:
{bug_report}

USER STORY GERADA PELO MODELO:
{user_story}

RESPOSTA ESPERADA (Ground Truth):
{reference}

INSTRUÇÕES:

Pontuação de 0 a 1.

Uma pontuação de 1 significa que a resposta é útil para Produto, Engenharia e QA,
possui critérios de aceitação acionáveis, inclui contexto técnico quando necessário,
e ajuda a implementar e testar a correção.

Retorne uma pontuação e uma justificativa concisa.
""",
    feedback_key="helpfulness",
    model=os.getenv("EVAL_MODEL", ""),
    continuous=True
)

clarity_judge = create_llm_as_judge(
    prompt="""
Você é um avaliador especializado em medir a CLAREZA de respostas geradas por IA.

RELATO DO BUG:
{bug_report}

USER STORY GERADA PELO MODELO:
{user_story}

RESPOSTA ESPERADA (Ground Truth):
{reference}

INSTRUÇÕES:

Avalie a CLAREZA da resposta gerada com base nos critérios:

1. ORGANIZAÇÃO (0.0 a 1.0):
   - A resposta tem estrutura lógica e bem organizada?
   - Informações estão em ordem sensata?

2. LINGUAGEM (0.0 a 1.0):
   - Usa linguagem simples e direta?
   - Evita jargões desnecessários?
   - Fácil de entender?

3. AUSÊNCIA DE AMBIGUIDADE (0.0 a 1.0):
   - A resposta é clara e sem ambiguidades?
   - Não deixa dúvidas sobre o que está sendo comunicado?

4. CONCISÃO (0.0 a 1.0):
   - É concisa sem ser curta demais?
   - Não tem informações redundantes?

Calcule a MÉDIA dos 4 critérios para obter o score final.

IMPORTANTE: Retorne APENAS um objeto JSON válido no formato:
{{
  "score": <valor entre 0.0 e 1.0>,
  "reasoning": "<explicação detalhada da avaliação em até 100 palavras>"
}}

NÃO adicione nenhum texto antes ou depois do JSON.
""" ,
    feedback_key="clarity",
    model=os.getenv("EVAL_MODEL", ""),
    continuous=True
)

precision_judge = create_llm_as_judge(
    prompt="""
Você é um avaliador especializado em detectar PRECISÃO e ALUCINAÇÕES em respostas de IA.

RELATO DO BUG:
{bug_report}

USER STORY GERADA PELO MODELO:
{user_story}

RESPOSTA ESPERADA (Ground Truth):
{reference}

INSTRUÇÕES:

Avalie a PRECISÃO da resposta gerada:

1. AUSÊNCIA DE ALUCINAÇÕES (0.0 a 1.0):
   - A resposta contém informações INVENTADAS ou não verificáveis?
   - Todas as afirmações são baseadas em fatos?
   - 1.0 = nenhuma alucinação detectada
   - 0.0 = resposta cheia de informações inventadas

2. FOCO NA PERGUNTA (0.0 a 1.0):
   - A resposta responde EXATAMENTE o que foi perguntado?
   - Não divaga ou adiciona informações não solicitadas?
   - 1.0 = totalmente focada
   - 0.0 = completamente fora do tópico

3. CORREÇÃO FACTUAL (0.0 a 1.0):
   - As informações estão CORRETAS quando comparadas com a referência?
   - Não há erros ou imprecisões?
   - 1.0 = todas informações corretas
   - 0.0 = informações incorretas

Calcule a MÉDIA dos 3 critérios para obter o score final.

IMPORTANTE: Retorne APENAS um objeto JSON válido no formato:
{{
  "score": <valor entre 0.0 e 1.0>,
  "reasoning": "<explicação detalhada em até 100 palavras, cite exemplos>"
}}

NÃO adicione nenhum texto antes ou depois do JSON.
""",
    feedback_key="precision",
    model=os.getenv("EVAL_MODEL", ""),
    continuous=True
)

def helpfulness_evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    bug_report = inputs.get("bug_report", "")
    user_story = outputs.get("user_story", "")
    reference = reference_outputs.get("reference", "")

    return helpfulness_judge(
        bug_report=bug_report,
        user_story=user_story,
        reference=reference,
    )

def clarity_evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    bug_report = inputs.get("bug_report", "")
    user_story = outputs.get("user_story", "")
    reference = reference_outputs.get("reference", "")

    return clarity_judge(
        bug_report=bug_report,
        user_story=user_story,
        reference=reference,
    )

def precision_evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    bug_report = inputs.get("bug_report", "")
    user_story = outputs.get("user_story", "")
    reference = reference_outputs.get("reference", "")

    return precision_judge(
        bug_report=bug_report,
        user_story=user_story,
        reference=reference,
    )

evaluators = [
    correctness_evaluator,
    helpfulness_evaluator,
    clarity_evaluator,
    precision_evaluator,
    f1_score_evaluator
]

# Run evaluation
results = evaluate(
    run_evaluators,
    data=DATASET_NAME,
    evaluators=evaluators,
    experiment_prefix="BugToUserStoryEval",
    max_concurrency=1
)

print("="*80)
print(f"EXPERIMENT: {results.experiment_name}")
print("="*80)