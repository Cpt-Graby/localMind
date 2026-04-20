import time
import os
import requests

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
MODEL = "qwen2.5:7b"


def test_chat():
    """Testons si le llm recoit une requet"""
    payload = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": "Réponds 'Prêt' si tu m'entends."
        }],
        "stream": False,
        "options": {"temperature": 0.1}
    }
    response = requests.post(
        f"{OLLAMA_HOST}/api/chat",
        json=payload,
        timeout=120
    )
    response.raise_for_status()
    print(response.json()["messages"]["content"])


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
    raise Exception("[-] Erreur : Ollama est injoignable après 60 secondes.")


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
                print(f"{task}")
                test_chat()
        except KeyboardInterrupt:
            print("\n bye!")
            break
