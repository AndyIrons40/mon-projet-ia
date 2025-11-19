# agents.py
from openai import OpenAI
import os
import re

# --- Configuration OpenRouter ---
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

if not client.api_key:
    raise Exception("❌ Aucune clé API détectée ! Assure-toi d'avoir OPENROUTER_API_KEY dans tes variables.")


# --- Nettoyeur / mise en forme automatique ---
def nettoyer_et_formater(texte: str) -> str:
    """Nettoie le texte pour éviter les blocs illisibles et artefacts."""
    
    # Suppression des caractères hors plage
    texte = re.sub(r"[^\x09\x0A\x0D\x20-\x7EÀ-ÖØ-öø-ÿ€’–—•«»…°]", "", texte)

    # Suppression espaces multiples
    texte = re.sub(r"\s{2,}", " ", texte)

    # Saut de ligne après les phrases
    texte = re.sub(r"\.\s+", ".\n", texte)

    # Séparation titres automatiques
    texte = re.sub(r"\b(Analyse|Conclusion|Résumé|Recherche|Synthèse)\b", r"\n\n\1", texte)

    return texte.strip()


# --- Fonction générique pour chaque agent ---
def agent(role: str, prompt: str, contexte: str = ""):
    """
    Exécute un agent avec un rôle spécifique.
    Chaque agent agit comme un expert spécialisé.
    """

    instructions = {
        "analyste": (
            "Tu es un expert en analyse de problématiques complexes. "
            "Ton rôle est d'identifier clairement les enjeux, causes, risques et implications."
        ),
        "chercheur": (
            "Tu es un chercheur et un expert en veille technologique. "
            "Tu fournis des informations fiables, factuelles et récentes (dans la limite du modèle)."
        ),
        "synthese": (
            "Tu es un expert en communication claire. "
            "Tu organises et reformules les informations en une réponse structurée, fluide et lisible."
        ),
    }

    role_prompt = instructions.get(role, "Tu es un assistant généraliste compétent.")
    
    full_prompt = (
        f"{role_prompt}\n\n"
        f"Contexte supplémentaire : {contexte}\n\n"
        f"Ta tâche : {prompt}\n\n"
        f"Réponds en français, avec une écriture claire et structurée."
    )

    try:
        response = client.chat.completions.create(
            model="nvidia/nemotron-nano-9b-v2:free",
            messages=[
                {"role": "system", "content": role_prompt},
                {"role": "user", "content": full_prompt}
            ]
        )
        texte = response.choices[0].message.content
        return nettoyer_et_formater(texte)

    except Exception as e:
        return f"[Erreur avec l'agent {role}] : {e}"


# --- Fonction de collaboration entre plusieurs agents ---
def equipe_collaborative(question: str, contexte: str = "", roles=None):
    """
    Simule une équipe d'agents collaboratifs.
    Les rôles actifs sont passés en paramètre (ex: ["analyste", "chercheur", "synthese"]).
    """

    if roles is None:
        roles = ["analyste", "chercheur", "synthese"]

    discussions = []
    resultats = {}

    # --- Étape 1 : Analyse ---
    if "analyste" in roles:
        analyse = agent("analyste", f"Analyse la question suivante : {question}", contexte)
        resultats["analyste"] = analyse
        discussions.append(f"🧩 **Analyse**\n{analyse}")

    # --- Étape 2 : Recherche ---
    if "chercheur" in roles:
        base_context = "\n\n".join(resultats.values())
        recherche = agent("chercheur", f"Complète avec les informations utiles : {question}", base_context)
        resultats["chercheur"] = recherche
        discussions.append(f"🔎 **Recherche**\n{recherche}")

    # --- Étape 3 : Synthèse ---
    if "synthese" in roles:
        base_context = "\n\n".join(resultats.values())
        synthese = agent("synthese", f"Rédige une synthèse claire et argumentée sur : {question}", base_context)
        resultats["synthese"] = synthese
        discussions.append(f"🧠 **Synthèse finale**\n{synthese}")

    # --- Résultat final propre ---
    return "\n\n".join(discussions)
