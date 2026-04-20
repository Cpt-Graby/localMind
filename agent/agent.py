import json
import time
import os
import requests
from prompt import SYSTEM_PROMPT
from tools import execute_tool

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
MODEL = "qwen2.5:3b"


def call_llm(msg: list) -> str:
    """Testons si le llm recoit une requet"""
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + msg,
        "stream": False,
        "options": {"temperature": 0.1}
    }
    print(f"payload: {payload}")
    print("─" * 50)
    response = requests.post(
        f"{OLLAMA_HOST}/api/chat",
        json=payload,
        timeout=120
    )
    response.raise_for_status()
    return response.json()["message"]["content"]


def parse_llm_response(raw: str) -> dict:
    """Extrait le JSON de la réponse du LLM, même s'il y a du texte autour."""
    raw = raw.strip()

    # Cas idéal : réponse directement en JSON
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Cas fréquent : JSON dans un bloc ```json ... ```
    if "```" in raw:
        start = raw.find("```")
        end = raw.rfind("```")
        block = raw[start:end].strip("`").strip()
        if block.startswith("json"):
            block = block[4:].strip()
        try:
            return json.loads(block)
        except json.JSONDecodeError:
            pass

    # Dernier recours : chercher { ... }
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end > start:
        try:
            return json.loads(raw[start:end])
        except json.JSONDecodeError:
            pass

    return {"thought": "parse error", "tool": "bash", "params": {"cmd": "echo 'parse error'"}}


def run_agent(_task: str):
    print(f"\n Task: {_task}")
    print("─" * 50)

    history = []
    history.append({"role": "user", "content": f"Task: {_task}"})
    print(history)
    print("─" * 50)
    raw_response = call_llm(history)
    print("─" * 50)
    print(raw_response)
    print("─" * 50)
    decision = parse_llm_response(raw_response)
    thought = decision.get("thought", "")
    tool = decision.get("tool", "")
    params = decision.get("params", {})
    print(f"thought: {thought}.")
    print(f"[-]Tool: {tool} | Params: {params}")
    history.append({"role": "assistant", "content": raw_response})
    result = execute_tool(tool, params)

    # 5. Check fin de tâche
    if result.startswith("FINISH:"):
        summary = result[7:]
        print(f"\nDone! {summary}")
        return

    print(f"Result: {result[:200]}{'...' if len(result) > 200 else ''}")

    # 6. Ajoute le résultat à l'historique pour le prochain tour
    history.append({
        "role": "user",
        "content": f"Tool result:\n{result}"
    })


def wait_for_ollama():
    """ Tentative de connection au serveur ollama"""
    print(f"[*] Attente d'Ollama sur {OLLAMA_HOST}...")
    num_try = 30
    tries = 0
    while tries < num_try:
        try:
            response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
            if response.status_code == 200:
                print("[+] Ollama est opérationnel.")
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(2)
        tries += 1
    raise Exception("[-] Erreur : Ollama est injoignable.")


def pull_model_if_needed():
    """Vérifie la présence du modèle et le télécharge si absent"""
    response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2)
    tags = response.json().get("models", [])
    model_exists = any(m["name"].startswith(MODEL) for m in tags)
    if not model_exists:
        print(f"[*] Téléchargement du modèle {MODEL}")
        requests.post(f"{OLLAMA_HOST}/api/pull",
                      json={"name": MODEL}, timeout=None)
        print(f"[+] Modèle {MODEL} prêt.")
    else:
        print(f"[+] Modèle {MODEL} déjà présent.")


if __name__ == "__main__":
    print("\n LocalMind Agent — type your task, Ctrl+C to quit\n")
    wait_for_ollama()
    pull_model_if_needed()
    while True:
        try:
            task = input("Task > ").strip()
            if task:
                run_agent(task)
        except KeyboardInterrupt:
            print("\n bye!")
            break
