# interface_agent.py
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
app.title("Agent collaboratif intelligent")
app.geometry("850x640")

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

# === Variables globales ===
memory = charger_memoire()

# === Paramètres dynamiques des rôles ===
roles_selectionnes = {
    "analyste": ctk.BooleanVar(value=True),
    "chercheur": ctk.BooleanVar(value=True),
    "synthese": ctk.BooleanVar(value=True)
}

# === Fonctions principales ===

def update_status(message, progress=None):
    status_label.configure(text=message)
    if progress is not None:
        progress_bar.set(progress)
    app.update_idletasks()

def process_request(user_input):
    """Thread de traitement de la requête avec rôles dynamiques."""
    try:
        update_status("🌐 Recherche web en cours...", 0.2)
        web_results = web_search(user_input)
        chat_box.insert("end", f"🌐 Résultats web : {web_results}\n\n")
        memory.append({"role": "web", "content": web_results})
        sauvegarder_memoire()
        app.update()

        # Rôles sélectionnés
        roles_actifs = [role for role, var in roles_selectionnes.items() if var.get()]
        if not roles_actifs:
            roles_actifs = ["analyste", "synthese"]

        update_status(f"🤖 Agents actifs : {', '.join(roles_actifs)}", 0.4)
        time.sleep(0.3)

        update_status("🧠 Discussion entre agents...", 0.6)
        reponse = equipe_collaborative(
            user_input,
            contexte="\n".join([m["content"] for m in memory[-5:]]),
            roles=roles_actifs
        )

        chat_box.insert("end", f"🤖 Réponse : {reponse}\n\n")
        memory.append({"role": "agent", "content": reponse})
        sauvegarder_memoire()

        update_status("✅ Réponse complète générée", 1.0)
        time.sleep(0.8)
        update_status("🟢 Prêt.")
        progress_bar.set(0)

    except Exception as e:
        chat_box.insert("end", f"⚠️ Erreur : {e}\n\n")
        update_status("❌ Erreur lors du traitement", 0)

def envoyer_message():
    user_input = input_field.get().strip()
    if not user_input:
        return

    chat_box.insert("end", f"👤 Vous : {user_input}\n\n")
    memory.append({"role": "user", "content": user_input})
    sauvegarder_memoire()
    input_field.delete(0, "end")

    thread = Thread(target=process_request, args=(user_input,))
    thread.start()

def reset_memory():
    memory.clear()
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
    chat_box.delete("1.0", "end")
    chat_box.insert("end", "🧹 Mémoire effacée.\n\n")
    update_status("🟢 Prêt.", 0)


# === Interface graphique ===

# Zone de texte principale
chat_box = ctk.CTkTextbox(app, wrap="word", width=800, height=450)
chat_box.pack(pady=10)

# Chargement mémoire
if memory:
    chat_box.insert("end", "💾 Mémoire rechargée depuis la session précédente.\n\n")
    for msg in memory[-10:]:
        role_icon = "👤" if msg["role"] == "user" else "🤖" if msg["role"] == "agent" else "🌐"
        chat_box.insert("end", f"{role_icon} {msg['content']}\n\n")
else:
    chat_box.insert("end", "👋 Bonjour ! Posez votre question à l’équipe d’agents IA.\n\n")

# === Section des rôles d'agents ===
roles_frame = ctk.CTkFrame(app)
roles_frame.pack(pady=10)

ctk.CTkLabel(roles_frame, text="🧩 Sélection des agents actifs :", font=("Arial", 14, "bold")).pack(pady=5)

roles_row = ctk.CTkFrame(roles_frame)
roles_row.pack()

ctk.CTkCheckBox(roles_row, text="Analyste", variable=roles_selectionnes["analyste"]).pack(side="left", padx=10)
ctk.CTkCheckBox(roles_row, text="Chercheur", variable=roles_selectionnes["chercheur"]).pack(side="left", padx=10)
ctk.CTkCheckBox(roles_row, text="Synthèse", variable=roles_selectionnes["synthese"]).pack(side="left", padx=10)

# Barre de progression
progress_frame = ctk.CTkFrame(app)
progress_frame.pack(pady=(0, 10))

progress_bar = ctk.CTkProgressBar(progress_frame, width=600)
progress_bar.set(0)
progress_bar.pack(side="left", padx=10)

status_label = ctk.CTkLabel(progress_frame, text="🟢 Prêt.", font=("Arial", 13))
status_label.pack(side="left")

# Champ d'entrée
input_frame = ctk.CTkFrame(app)
input_frame.pack(pady=5)

input_field = ctk.CTkEntry(input_frame, width=500, placeholder_text="Posez votre question ici...")
input_field.pack(side="left", padx=10)

send_button = ctk.CTkButton(input_frame, text="Envoyer", command=envoyer_message)
send_button.pack(side="left", padx=5)

reset_button = ctk.CTkButton(input_frame, text="🧹 Effacer mémoire", command=reset_memory)
reset_button.pack(side="left", padx=5)

app.mainloop()
