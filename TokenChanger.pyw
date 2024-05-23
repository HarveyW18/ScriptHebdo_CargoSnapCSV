import customtkinter as ctk
import sys
import os
from cryptography.fernet import Fernet

# Assurez-vous que les chemins relatifs fonctionnent après la compilation
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))

# Fonction pour mettre à jour le token chiffré
def update_token(new_token):
    script_dir = get_script_dir()
    key_file = os.path.join(script_dir, "ressources", "key.key")
    enc_file = os.path.join(script_dir, "ressources", "token.enc")

    with open(key_file, 'rb') as key_file:
        key = key_file.read()
    
    f = Fernet(key)
    encrypted_token = f.encrypt(new_token.encode())

    with open(enc_file, 'wb') as token_file:
        token_file.write(encrypted_token)

# Fonction pour gérer l'événement de mise à jour du token
def on_update_button_click():
    new_token = entry.get()
    if new_token:
        update_token(new_token)
        result_label.configure(text="Token mis à jour avec succès.", text_color="green", font=("Segoe UI", 13, "bold"))
        app.after(1500, lambda: app.destroy())
    else:
        result_label.configure(text="Veuillez entrer un token.", text_color="red", font=("Segoe UI", 13, "bold"))

# Configuration de la fenêtre principale
ctk.set_appearance_mode("system")  # Modes: "light", "dark", "system"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

app = ctk.CTk()  # Création de la fenêtre principale
app.geometry("500x200")
app.title("Mise à jour du Token")
app.iconbitmap(resource_path("ressources/icon.ico"))

# Label de description
label = ctk.CTkLabel(app, text="Entrez le nouveau token :", corner_radius=8, font=("Segoe UI", 14))
label.pack(pady=10)

# Champ de saisie pour le token
entry = ctk.CTkEntry(app, width=300, font=("Segoe UI", 14), border_width=1, border_color='#476A4A', placeholder_text="Token d'authentification")
entry.pack(pady=10)

# Bouton de mise à jour
update_button = ctk.CTkButton(app, text="Mettre à jour le token", fg_color='#476A4A', command=on_update_button_click, font=("Segoe UI", 12, "bold"))  # Correction ici
update_button.pack(pady=10)

# Label pour afficher les résultats
result_label = ctk.CTkLabel(app, text="", font=("Arial", 12))
result_label.pack(pady=10)

# Lancement de la boucle principale de l'application
app.mainloop()

