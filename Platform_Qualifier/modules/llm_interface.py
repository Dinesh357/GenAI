import requests
import yaml

OLLAMA_URL = "http://localhost:11434/api/generate"

# Load prompt templates from config/prompts.yaml
def load_prompts():
    with open("config/prompts.yaml", "r") as f:
        return yaml.safe_load(f)["prompts"]

def answer_questions_with_rag(retriever):
    prompts = load_prompts()
    answers = {}

    for criterion, template in prompts.items():
        relevant_chunks = retriever.retrieve(template)
        context = "\n\n".join(relevant_chunks)
        full_prompt = f"{template}\n\nRelevant Context:\n{context}"
        try:
            response = requests.post(OLLAMA_URL, json={
                "model": "llama2",
                "prompt": full_prompt,
                "stream": False
            })

           # print(f"[{criterion}] Status: {response.status_code}")
            # print(f"[{criterion}] Response: {response.text}")
            if(response.status_code == 200):
                result = response.json()
                answers[criterion] = result.get("response", "No response returned").strip()
            else:
                answers[criterion] = "No response returned"
                break
        except Exception as e:
            answers[criterion] = f"Error: {str(e)}"

    return answers


# New helpers for requirements-compliant prompting and parsing
def _build_prompt(context: str, question: str) -> str:
    return (
        "Context:\n" + context + "\n\n" +
        "Question: " + question + "\n\n" +
        "Respond with:\n" +
        "Score: <0-3>\n" +
        "Justification: <brief explanation>\n"
    )


def _parse_score_and_justification(text: str):
    score = None
    justification = ""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for l in lines:
        if l.lower().startswith("score:"):
            try:
                score_val = ''.join(ch for ch in l.split(":", 1)[1] if ch.isdigit())
                score = int(score_val) if score_val != '' else None
            except Exception:
                score = None
        elif l.lower().startswith("justification:") and not justification:
            justification = l.split(":", 1)[1].strip()
    # Fallback: try to find a digit 0-3 anywhere
    if score is None:
        for ch in text:
            if ch in "0123":
                try:
                    score = int(ch)
                    break
                except Exception:
                    pass
    return score, justification or text.strip()


def evaluate_checklist_with_rag(retriever, items, model: str = "llama2"):
    """
    Evaluate each checklist item using RAG and a local LLM.
    items: list of {criterion, question, weight}
    Returns dict: criterion -> {score, justification, raw}
    """
    results = {}
    for item in items:
        criterion = item.get("criterion")
        question = item.get("question") or str(criterion)
        relevant = retriever.retrieve(question)
        context = "\n\n".join(relevant)
        prompt = _build_prompt(context, question)
        try:
            response = requests.post(OLLAMA_URL, json={
                "model": model,
                "prompt": prompt,
                "stream": False
            })
            if response.status_code == 200:
                raw = response.json().get("response", "").strip()
                score, just = _parse_score_and_justification(raw)
                results[criterion] = {"score": score if score is not None else 0, "justification": just, "raw": raw}
            else:
                results[criterion] = {"score": 0, "justification": "No response returned", "raw": ""}
        except Exception as e:
            results[criterion] = {"score": 0, "justification": f"Error: {e}", "raw": ""}
    return results
