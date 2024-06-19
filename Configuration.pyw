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

# Fonction pour lire les configurations cryptées
def read_configurations():
    script_dir = get_script_dir()
    key_file = os.path.join(script_dir, "ressources", "key.key")
    enc_config_file = os.path.join(script_dir, "ressources", "config.enc")

    try:
        with open(key_file, 'rb') as key_file:
            key = key_file.read()
        
        f = Fernet(key)

        with open(enc_config_file, 'rb') as config_file:
            encrypted_config = config_file.read()

        decrypted_config = f.decrypt(encrypted_config).decode().split(',')
        
        # Récupérer les adresses e-mail comme une liste
        smtp_password, email_from, email_to, smtp_server, smtp_port, token, path = decrypted_config

        return smtp_password, email_from, email_to, smtp_server, smtp_port, token, path
    except FileNotFoundError:
        return None


# Fonction pour mettre à jour les configurations cryptées
def update_configurations(smtp_password, email_from, email_to, smtp_server, smtp_port, token, path):
    script_dir = get_script_dir()
    key_file = os.path.join(script_dir, "ressources", "key.key")
    enc_token_file = os.path.join(script_dir, "ressources", "token.enc")
    enc_config_file = os.path.join(script_dir, "ressources", "config.enc")

    with open(key_file, 'rb') as key_file:
        key = key_file.read()
    
    f = Fernet(key)
    encrypted_token = f.encrypt(token.encode())
    # Convertir la liste d'adresses e-mail en une chaîne séparée par des virgules
    encrypted_config = f.encrypt(f"{smtp_password},{email_from},{email_to},{smtp_server},{smtp_port},{token},{path}".encode())

    with open(enc_token_file, 'wb') as token_file:
        token_file.write(encrypted_token)

    with open(enc_config_file, 'wb') as config_file:
        config_file.write(encrypted_config)


# Fonction pour gérer l'événement de mise à jour
def on_update_button_click():
    smtp_password = entry_smtp_password.get()
    email_from = entry_email_from.get()
    email_to = entry_email_to.get()
    smtp_server = entry_smtp_server.get()
    smtp_port = entry_smtp_port.get()
    new_token = entry_token.get()
    path = entry_path.get()

    
    if all([smtp_password, email_from, email_to, smtp_server, smtp_port, new_token, path]):
        update_configurations(smtp_password, email_from, email_to, smtp_server, smtp_port, new_token, path)
        result_label.configure(text="Configurations mises à jour avec succès.", text_color="green", font=("Segoe UI", 13, "bold"))
        app.after(1500, lambda: app.destroy())
    else:
        result_label.configure(text="Veuillez remplir tous les champs.", text_color="red", font=("Segoe UI", 13, "bold"))

# Lecture des configurations actuelles
configurations = read_configurations()

# Configuration de l'email par défaut
if configurations:
    SMTP_PASSWORD, EMAIL_FROM, EMAIL_TO, SMTP_SERVER, SMTP_PORT, TOKEN, PATH = configurations
else:
    EMAIL_FROM = "mail.info@nomdedomaine.com"
    EMAIL_TO = "service@nomdedomaine.com"
    SMTP_SERVER = "smtp.office365.com"
    SMTP_PORT = 587
    SMTP_PASSWORD = ""
    TOKEN = "ENTREZ VOTRE TOKEN"
    PATH = r"K:\\"

# Configuration de la fenêtre principale
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("450x740")
app.title("Mise à jour des configurations")
app.iconbitmap(resource_path("ressources/icon.ico"))

# Label de titre
title_label = ctk.CTkLabel(app, text="Mise à jour des configurations", font=("Segoe UI", 20, "bold"))
title_label.pack(pady=25)

# Labels et champs de saisie
label_token = ctk.CTkLabel(app, text="Entrez le nouveau token :", corner_radius=8, font=("Segoe UI", 14))
label_token.pack(pady=5)
entry_token = ctk.CTkEntry(app, width=300, font=("Segoe UI", 14), border_width=1, border_color='#476A4A', placeholder_text="Token d'authentification")
entry_token.insert(0, TOKEN)
entry_token.pack(pady=5)

label_smtp_password = ctk.CTkLabel(app, text="Entrez le mot de passe SMTP :", corner_radius=8, font=("Segoe UI", 14))
label_smtp_password.pack(pady=5)
entry_smtp_password = ctk.CTkEntry(app, width=300, font=("Segoe UI", 14), border_width=1, border_color='#476A4A', placeholder_text="Mot de passe SMTP", show="*")
entry_smtp_password.insert(0, SMTP_PASSWORD)
entry_smtp_password.pack(pady=5)

label_email_from = ctk.CTkLabel(app, text="Entrez l'email d'expédition :", corner_radius=8, font=("Segoe UI", 14))
label_email_from.pack(pady=5)
entry_email_from = ctk.CTkEntry(app, width=300, font=("Segoe UI", 14), border_width=1, border_color='#476A4A', placeholder_text="Email d'expédition")
entry_email_from.insert(0, EMAIL_FROM)
entry_email_from.pack(pady=5)

label_email_to = ctk.CTkLabel(app, text="Entrez l'email de destination :", corner_radius=8, font=("Segoe UI", 14))
label_email_to.pack(pady=5)
entry_email_to = ctk.CTkEntry(app, width=300, font=("Segoe UI", 14), border_width=1, border_color='#476A4A', placeholder_text="Emails de destination (séparés par des virgules)")
entry_email_to.insert(0, EMAIL_TO)
entry_email_to.pack(pady=5)

label_smtp_server = ctk.CTkLabel(app, text="Entrez le serveur SMTP :", corner_radius=8, font=("Segoe UI", 14))
label_smtp_server.pack(pady=5)
entry_smtp_server = ctk.CTkEntry(app, width=300, font=("Segoe UI", 14), border_width=1, border_color='#476A4A', placeholder_text="Serveur SMTP")
entry_smtp_server.insert(0, SMTP_SERVER)
entry_smtp_server.pack(pady=5)

label_smtp_port = ctk.CTkLabel(app, text="Entrez le port SMTP :", corner_radius=8, font=("Segoe UI", 14))
label_smtp_port.pack(pady=5)
entry_smtp_port = ctk.CTkEntry(app, width=300, font=("Segoe UI", 14), border_width=1, border_color='#476A4A', placeholder_text="Port SMTP")
entry_smtp_port.insert(0, str(SMTP_PORT))
entry_smtp_port.pack(pady=5)


label_path = ctk.CTkLabel(app, text="Entrez le chemin de destination :", corner_radius=8, font=("Segoe UI", 14))
label_path.pack(pady=5)
entry_path = ctk.CTkEntry(app, width=300, font=("Segoe UI", 14), border_width=1, border_color='#476A4A', placeholder_text="Chemin de destination")
entry_path.insert(0, PATH)
entry_path.pack(pady=5)

update_button = ctk.CTkButton(app, text="Mettre à jour les configurations", fg_color='#476A4A', command=on_update_button_click, font=("Segoe UI", 12, "bold"))
update_button.pack(pady=25)

result_label = ctk.CTkLabel(app, text="", font=("Arial", 12))
result_label.pack()

app.mainloop()
