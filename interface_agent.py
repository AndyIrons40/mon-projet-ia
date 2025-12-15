# interface_agent.py — version multi-chercheurs corrigée

import customtkinter as ctk
from threading import Thread
from agents import equipe_collaborative
from web_tools import web_search
import time
import json
import os

# === Configuration générale ===
ctk.set_appearance_mode("dark")
app = ctk.CTk()
app.title("Agent collaboratif intelligent — Multi-chercheurs")
app.geometry("850x650")

# === Fichier mémoire persistante ===
MEMORY_FILE = "memoire.json"

# === Fonctions mémoire ===
def charger_memoire():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def sauvegarder_memoire():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

memory = charger_memoire()

# === Sélection dynamique des rôles ===
roles_selectionnes = {
    "analyste": ctk.BooleanVar(value=True),
    "chercheur_google": ctk.BooleanVar(value=True),
    "chercheur_duckduckgo": ctk.BooleanVar(value=True),
    "chercheur_wikipedia": ctk.BooleanVar(value=False),
    "comparateur": ctk.BooleanVar(value=True),
    "synthese": ctk.BooleanVar(value=True)
}

# === Interface : Mise à jour du statut ===
def update_status(message, progress=None):
    status_label.configure(text=message)
    if progress is not None:
        progress_bar.set(progress)
    app.update_idletasks()

# ============================================================
#           FONCTION PRINCIPALE DE TRAITEMENT
# ============================================================
def process_request(user_input):
    try:
        # Construction de la liste des moteurs sélectionnés
        engines = []
        if roles_selectionnes["chercheur_google"].get():
            engines.append("google")
        if roles_selectionnes["chercheur_duckduckgo"].get():
            engines.append("duckduckgo")
        if roles_selectionnes["chercheur_wikipedia"].get():
            engines.append("wikipedia")

        update_status("🌐 Recherche web…", 0.2)

        # Requête web
        raw_web = web_search(user_input, engines)

        # Conversion propre des résultats, même si ce sont des dicts
        converted_results = []
        for src, res in raw_web.items():
            if isinstance(res, dict):
                # On convertit proprement en texte lisible
                text = json.dumps(res, ensure_ascii=False, indent=2)
            else:
                text = str(res)
  
            converted_results.append(f"{src.upper()} :\n{text}")

        web_results_text = "\n\n".join(converted_results)


        chat_box.insert("end", f"🌐 Résultats web :\n{web_results_text}\n\n")
        memory.append({"role": "web", "content": web_results_text})
        sauvegarder_memoire()

        # Récupération des rôles actifs
        roles_actifs = [r for r, v in roles_selectionnes.items() if v.get()]
        if not roles_actifs:
            roles_actifs = ["analyste", "synthese"]

        update_status(f"🤖 Agents actifs : {', '.join(roles_actifs)}", 0.4)
        time.sleep(0.2)

        update_status("🧠 Collaboration des agents…", 0.6)

        # Contexte = 5 derniers messages mémoire
        # Conversion robuste du contexte (évite les dicts)
        contexte_txt = "\n".join([
            m["content"] if isinstance(m["content"], str) else json.dumps(m["content"], ensure_ascii=False)
            for m in memory[-5:]
        ])


        # Appel de l’équipe d'agents
        reponse = equipe_collaborative(
            question=user_input,
            contexte=contexte_txt,
            roles=roles_actifs
        )

        chat_box.insert("end", f"🤖 Réponse collaborative :\n{reponse}\n\n")
        memory.append({"role": "agent", "content": reponse})
        sauvegarder_memoire()

        update_status("✅ Réponse générée", 1.0)
        time.sleep(0.5)
        update_status("🟢 Prêt.")
        progress_bar.set(0)

    except Exception as e:
        chat_box.insert("end", f"⚠️ Erreur : {e}\n\n")
        update_status("❌ Erreur", 0)

# ============================================================
#           INTERACTION UTILISATEUR
# ============================================================
def envoyer_message():
    user_input = input_field.get().strip()
    if not user_input:
        return

    chat_box.insert("end", f"👤 Vous : {user_input}\n\n")
    memory.append({"role": "user", "content": user_input})
    sauvegarder_memoire()

    input_field.delete(0, "end")
    Thread(target=process_request, args=(user_input,)).start()

def reset_memory():
    memory.clear()
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
    chat_box.delete("1.0", "end")
    chat_box.insert("end", "🧹 Mémoire effacée.\n\n")
    update_status("🟢 Prêt.", 0)

# ============================================================
#           INTERFACE GRAPHIQUE TK
# ============================================================
chat_box = ctk.CTkTextbox(app, wrap="word", width=800, height=420)
chat_box.pack(pady=10)

if memory:
    chat_box.insert("end", "💾 Mémoire chargée.\n\n")
    for msg in memory[-10:]:
        icon = "👤" if msg["role"] == "user" else "🤖" if msg["role"] == "agent" else "🌐"
        chat_box.insert("end", f"{icon} {msg['content']}\n\n")
else:
    chat_box.insert("end", "👋 Bonjour ! Posez votre question à l'équipe d'agents IA.\n\n")

# Sélection des rôles
roles_frame = ctk.CTkFrame(app)
roles_frame.pack(pady=5)

ctk.CTkLabel(roles_frame, text="🧩 Agents activés :", font=("Arial", 14, "bold")).pack()

row1 = ctk.CTkFrame(roles_frame)
row1.pack(pady=5)
ctk.CTkCheckBox(row1, text="Analyste", variable=roles_selectionnes["analyste"]).pack(side="left", padx=10)
ctk.CTkCheckBox(row1, text="Comparateur", variable=roles_selectionnes["comparateur"]).pack(side="left", padx=10)
ctk.CTkCheckBox(row1, text="Synthèse", variable=roles_selectionnes["synthese"]).pack(side="left", padx=10)

row2 = ctk.CTkFrame(roles_frame)
row2.pack(pady=5)
ctk.CTkLabel(row2, text="🔎 Chercheurs web :", font=("Arial", 13)).pack(side="left", padx=5)
ctk.CTkCheckBox(row2, text="Google", variable=roles_selectionnes["chercheur_google"]).pack(side="left", padx=8)
ctk.CTkCheckBox(row2, text="DuckDuckGo", variable=roles_selectionnes["chercheur_duckduckgo"]).pack(side="left", padx=8)
ctk.CTkCheckBox(row2, text="Wikipedia", variable=roles_selectionnes["chercheur_wikipedia"]).pack(side="left", padx=8)

# Barre de progression
progress_frame = ctk.CTkFrame(app)
progress_frame.pack(pady=10)

progress_bar = ctk.CTkProgressBar(progress_frame, width=600)
progress_bar.set(0)
progress_bar.pack(side="left", padx=10)

status_label = ctk.CTkLabel(progress_frame, text="🟢 Prêt.", font=("Arial", 13))
status_label.pack()

# Champ d'entrée
input_frame = ctk.CTkFrame(app)
input_frame.pack(pady=5)

input_field = ctk.CTkEntry(input_frame, width=500, placeholder_text="Posez votre question ici…")
input_field.pack(side="left", padx=10)

send_button = ctk.CTkButton(input_frame, text="Envoyer", command=envoyer_message)
send_button.pack(side="left", padx=5)

reset_button = ctk.CTkButton(input_frame, text="🧹 Effacer mémoire", command=reset_memory)
reset_button.pack(side="left", padx=5)

app.mainloop()
