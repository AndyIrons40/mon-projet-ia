# agents.py
from openai import OpenAI
import os

# --- Configuration OpenRouter ---
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

# --- Fonction générique pour chaque agent ---
def agent(role: str, prompt: str, contexte: str = ""):
    """
    Exécute un agent avec un rôle spécifique.
    Chaque agent agit comme un expert spécialisé.
    """
    instructions = {
        "analyste": (
            "Tu es un expert en analyse de problématiques complexes. "
            "Identifie les causes, enjeux et implications du sujet."
        ),
        "chercheur": (
            "Tu es un chercheur en veille technologique. "
            "Ta mission est de compléter les informations grâce à des faits récents ou des données connues."
        ),
        "synthese": (
            "Tu es un expert en communication claire. "
            "Résume les contributions précédentes de manière structurée et concise."
        ),
    }

    role_prompt = instructions.get(role, "Tu es un assistant généraliste compétent.")
    full_prompt = f"{role_prompt}\n\nContexte : {contexte}\n\nTâche : {prompt}"

    try:
        response = client.chat.completions.create(
            model="nvidia/nemotron-nano-9b-v2:free",  # modèle rapide et gratuit sur OpenRouter
            messages=[
                {"role": "system", "content": role_prompt},
                {"role": "user", "content": full_prompt}
            ]
        )
        return response.choices[0].message.content.strip()
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

    # Étape 1 : Analyse
    if "analyste" in roles:
        analyse = agent("analyste", f"Analyse la question suivante : {question}", contexte)
        resultats["analyste"] = analyse
        discussions.append(f"🧩 **Analyse** : {analyse}")

    # Étape 2 : Recherche complémentaire
    if "chercheur" in roles:
        base_contexte = resultats.get("analyste", contexte)
        recherche = agent("chercheur", f"Approfondis les informations sur : {question}", base_contexte)
        resultats["chercheur"] = recherche
        discussions.append(f"🔎 **Recherche** : {recherche}")

    # Étape 3 : Synthèse finale
    if "synthese" in roles:
        base_contexte = "\n\n".join(resultats.values())
        synthese = agent("synthese", f"Rédige une synthèse claire et argumentée sur : {question}", base_contexte)
        resultats["synthese"] = synthese
        discussions.append(f"🧠 **Synthèse finale** : {synthese}")

    # --- Résumé final ---
    resultat_final = "\n\n".join(discussions)
    return resultat_final
