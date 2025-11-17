import requests
import yaml
import time

OLLAMA_URL = "http://localhost:11434/api/generate"

# Load prompt templates from config/prompts.yaml
def load_prompts():
    start = time.perf_counter()
    with open("config/prompts.yaml", "r") as f:
        data = yaml.safe_load(f)
    prompts = data.get("prompts", {})
    if isinstance(prompts, dict):
        prompts = {k: (v.get("template") if isinstance(v, dict) else v)
                for k, v in prompts.items()}
    elapsed = time.perf_counter() - start
    print(f"[Load Prompts] elapsed={elapsed:.2f}s", flush=True)
    return prompts

def answer_questions_with_rag(retriever):
    prompts = load_prompts()
    answers = {}

    for criterion, template in prompts.items():
        relevant_chunks = retriever.retrieve(template, top_k=2)
        context_parts = []
        total = 0
        for ch in relevant_chunks:
            if total + len(ch) > 6000:
                context_parts.append(ch[:max(0, 6000 - total)])
                break
            context_parts.append(ch)
            total += len(ch)
        context = "\n\n".join(context_parts)
        full_prompt = f"{template}\n\nRelevant Context:\n{context}"
        try:
            start = time.perf_counter()
            print(f"[LLM-A] criterion={criterion} ctx_chars={len(context)}", flush=True)
            response = requests.post(OLLAMA_URL, json={
                "model": "mistral:latest",
                "prompt": full_prompt,
                "stream": False,
                "options": {"num_predict": 32, "temperature": 0.2, "num_ctx": 2048},
                "keep_alive": "30s"
            })
            elapsed = time.perf_counter() - start
            print(f"[LLM-A] status={response.status_code} elapsed={elapsed:.2f}s resp_chars={len(response.text)}", flush=True)

           # print(f"[{criterion}] Status: {response.status_code}")
            # print(f"[{criterion}] Response: {response.text}")
            if(response.status_code == 200):
                result = response.json()
                answers[criterion] = result.get("response", "No response returned").strip()
            else:
                answers[criterion] = "No response returned"
                break
        except Exception as e:
            print(f"[LLM-A] error criterion={criterion} err={e}", flush=True)
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


def evaluate_checklist_with_rag(retriever, items, model: str = "mistral:latest"):
    """
    Evaluate each checklist item using RAG and a local LLM.
    items: list of {criterion, question, weight}
    Returns dict: criterion -> {score, justification, raw}
    """
    results = {}
    for item in items:
        criterion = item.get("criterion")
        question = item.get("question") or str(criterion)
        relevant = retriever.retrieve(question, top_k=2)
        context_parts = []
        total = 0
        for ch in relevant:
            if total + len(ch) > 6000:
                context_parts.append(ch[:max(0, 6000 - total)])
                break
            context_parts.append(ch)
            total += len(ch)
        context = "\n\n".join(context_parts)
        prompt = _build_prompt(context, question)
        try:
            start = time.perf_counter()
            print(f"[LLM-C] criterion={criterion} ctx_chars={len(context)}", flush=True)
            response = requests.post(OLLAMA_URL, json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": 32, "temperature": 0.2, "num_ctx": 2048},
                "keep_alive": "30s"
            })
            elapsed = time.perf_counter() - start
            if response.status_code == 200:
                raw = response.json().get("response", "").strip()
                score, just = _parse_score_and_justification(raw)
                print(f"[LLM-C] status=200 elapsed={elapsed:.2f}s score={score}", flush=True)
                results[criterion] = {"score": score if score is not None else 0, "justification": just, "raw": raw}
            else:
                print(f"[LLM-C] status={response.status_code} elapsed={elapsed:.2f}s", flush=True)
                results[criterion] = {"score": 0, "justification": "No response returned", "raw": ""}
        except Exception as e:
            print(f"[LLM-C] error criterion={criterion} err={e}", flush=True)
            results[criterion] = {"score": 0, "justification": f"Error: {e}", "raw": ""}
    return results
