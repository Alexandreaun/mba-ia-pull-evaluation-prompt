
from typing import Dict
from dotenv import load_dotenv
from typing import Dict
from langchain_core.messages import HumanMessage
from utils import get_eval_llm, extract_json_from_response

load_dotenv()

def get_evaluator_llm():
    return get_eval_llm(temperature=0)

def calculate_f1_score(question: str, answer: str, reference: str) -> Dict[str, float]:
    evaluator_prompt=f"""
Você é um avaliador especializado em medir a qualidade de respostas geradas por IA.

Sua tarefa é calcular PRECISION e RECALL para determinar o F1-Score.

PERGUNTA DO USUÁRIO:
{question}

RESPOSTA GERADA PELO MODELO:
{answer}

RESPOSTA ESPERADA (Referência):
{reference}

INSTRUÇÕES:

1. PRECISION (0.0 a 1.0):
   - Quantas informações na resposta gerada são CORRETAS e RELEVANTES?
   - Penalizar informações incorretas, inventadas ou desnecessárias
   - 1.0 = todas informações são corretas e relevantes
   - 0.0 = nenhuma informação é correta ou relevante

2. RECALL (0.0 a 1.0):
   - Quantas informações da resposta esperada estão PRESENTES na resposta gerada?
   - Penalizar informações importantes que foram omitidas
   - 1.0 = todas informações importantes estão presentes
   - 0.0 = nenhuma informação importante está presente

3. RACIOCÍNIO:
   - Explique brevemente sua avaliação
   - Cite exemplos específicos do que estava correto/incorreto

IMPORTANTE: Retorne APENAS um objeto JSON válido no formato:
{{
  "precision": <valor entre 0.0 e 1.0>,
  "recall": <valor entre 0.0 e 1.0>,
  "reasoning": "<sua explicação em até 100 palavras>"
}}

NÃO adicione nenhum texto antes ou depois do JSON.
"""

    try:
        llm = get_evaluator_llm()
        response = llm.invoke([HumanMessage(content=evaluator_prompt)])
        result = extract_json_from_response(response.content)

        precision = float(result.get("precision", 0.0))
        recall = float(result.get("recall", 0.0))

        # Calcular F1-Score
        if (precision + recall) > 0:
            f1_score = 2 * (precision * recall) / (precision + recall)
        else:
            f1_score = 0.0

        return {
            "score": round(f1_score, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "reasoning": result.get("reasoning", "")
        }

    except Exception as e:
        print(f"❌ Erro ao avaliar F1-Score: {e}")
        return {
            "score": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "reasoning": f"Erro na avaliação: {str(e)}"
        }

def f1_score_evaluator(
        inputs: dict,
        outputs: dict,
        reference_outputs: dict,
    ) -> dict:

    question = inputs.get("bug_report")

    user_story = (
        outputs.get("user_story")
        or outputs.get("answer")
        or ""
    )

    reference = reference_outputs.get("reference", "")

    scores = calculate_f1_score(
        question=question,
        answer=user_story,
        reference=reference,
    )

    return {
    "key": "f1_score",
    "score": scores["score"],
    "comment": (
        f"precision={scores['precision']} | "
        f"recall={scores['recall']} | "
        f"f1={scores['score']}"
    ),
}