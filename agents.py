# agents.py
from openai import OpenAI
import json
import os

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

if not client.api_key:
    raise Exception("❌ Aucune clé API détectée pour OpenRouter !")


# === DÉFINITION DES AGENTS ===
def agent(role, prompt):
    response = client.chat.completions.create(
        model="nvidia/nemotron-nano-9b-v2:free",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def agent_analyste(question):
    return agent("analyste", f"Analyse en profondeur la question suivante : {question}")

def agent_chercheur(question):
    return agent("chercheur", f"Fais des recherches sur Internet (ou simule-les) pour répondre à : {question}")

def agent_synthese(analyses):
    return agent("synthèse", f"Combine ces informations et rédige une réponse claire et complète :\n\n{analyses}")

# === COORDINATEUR ===
def equipe_collaborative(question, roles=None, contexte=None):
    roles = roles or ["analyste", "chercheur", "synthèse"]
    results = {}

    # Tu peux utiliser le contexte si tu veux
    contexte_txt = f"\n\nContexte utile : {contexte}" if contexte else ""

     # 1. Analyse
    if "analyste" in roles:
        results["analyse"] = agent_analyste(question + contexte_txt)

    # 2. Recherche
    if "chercheur" in roles:
        results["recherche"] = agent_chercheur(question + contexte_txt)

    # 3. Synthèse
    synthese_input = "\n\n".join(
        f"{k.upper()}:\n{v}" for k, v in results.items()
    )
    results["finale"] = agent_synthese(synthese_input)

    return results