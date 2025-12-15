# agents.py
from openai import OpenAI
import os
from web_tools import search_duckduckgo, search_wikipedia, search_google_serper

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)


# ----------------------------------------------------------
# Agent IA générique
# ----------------------------------------------------------
def agent(role: str, prompt: str, contexte: str = ""):
    instructions = {
        "analyste": "Tu es un expert en analyse de problématiques complexes.",
        "chercheur_google": "Tu es un chercheur utilisant Google Search (via Serper API).",
        "chercheur_duckduckgo": "Tu es un chercheur utilisant DuckDuckGo Instant API.",
        "chercheur_wikipedia": "Tu es un chercheur basé sur Wikipedia API.",
        "comparateur": "Tu compares objectivement plusieurs informations et tu évalues la fiabilité.",
        "synthese": "Tu synthétises clairement et avec structure.",
    }

    role_prompt = instructions.get(role, "Tu es un assistant généraliste.")
    full_prompt = f"{role_prompt}\n\nContexte : {contexte}\n\nTâche : {prompt}"

    try:
        r = client.chat.completions.create(
            model="nvidia/nemotron-nano-9b-v2:free",
            messages=[
                {"role": "system", "content": role_prompt},
                {"role": "user", "content": full_prompt}
            ]
        )
        return r.choices[0].message.content.strip()
    except Exception as e:
        return f"[Erreur agent {role}] {e}"


# ----------------------------------------------------------
# Coordination des agents
# ----------------------------------------------------------
def equipe_collaborative(question: str, contexte: str = "", roles=None):
    if roles is None:
        roles = [
            "analyste",
            "chercheur_google",
            "chercheur_duckduckgo",
            "chercheur_wikipedia",
            "comparateur",
            "synthese"
        ]

    discussions = []
    resultats = {}

    # ANALYSE
    if "analyste" in roles:
        analyse = agent("analyste", f"Analyse : {question}", contexte)
        resultats["analyse"] = analyse
        discussions.append(f"🧩 Analyse :\n{analyse}\n")

    # CHERCHEURS WEB
    recherches = []

    if "chercheur_google" in roles:
        g = search_google_serper(question)
        recherches.append(("Google", g))
        discussions.append(f"🔎 Google :\n{g}\n")

    if "chercheur_duckduckgo" in roles:
        d = search_duckduckgo(question)
        recherches.append(("DuckDuckGo", d))
        discussions.append(f"🔎 DuckDuckGo :\n{d}\n")

    if "chercheur_wikipedia" in roles:
        w = search_wikipedia(question)
        recherches.append(("Wikipedia", w))
        discussions.append(f"🔎 Wikipedia :\n{w}\n")

    # COMPARATEUR
    if "comparateur" in roles:
        texte_comparaison = "\n\n".join([f"{src} :\n{res}" for src, res in recherches])
        comparaison = agent("comparateur", "Compare ces résultats et évalue leur fiabilité.", texte_comparaison)
        resultats["comparaison"] = comparaison
        discussions.append(f"📊 Comparaison :\n{comparaison}\n")

    # SYNTHÈSE FINALE
    if "synthese" in roles:
        contenu_total = "\n\n".join(resultats.values())
        synth = agent("synthese", f"Rédige une synthèse complète sur : {question}", contenu_total)
        discussions.append(f"🧠 Synthèse finale :\n{synth}\n")

    return "\n".join(discussions)
