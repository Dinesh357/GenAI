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
