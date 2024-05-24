from cryptography.fernet import Fernet
import os
import requests
import csv
import sys
import re
from datetime import datetime, timedelta
from mailjet_rest import Client

# Configuration de Mailjet
api_key = '3dd4ca76d157882dc46b75eaa7cbe6f9'
api_secret = '254bb13963f12cbcbaf62e1539555bf3'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')
EMAIL_FROM = "christ.wonga@georgeshelfer.com"
EMAIL_TO = ["jean-francois.portigliatti@georgeshelfer.com", "christ.wonga@georgeshelfer.com"]

def send_email(message, EMAIL_SUBJECT):
    data = {
        'Messages': [
            {
                "From": {
                    "Email": EMAIL_FROM,
                    "Name": "CargoSnap - HebdoCSV"
                },
                "To": [
                    {
                        "Email": email,
                        "Name": "CargoSnap - HebdoCSV"
                    } for email in EMAIL_TO  # Crée un objet pour chaque adresse email dans la liste
                ],
                "Subject": EMAIL_SUBJECT,
                "TextPart": message,
                "HTMLPart": f"<h3>Résultats de l'exportation des données :</h3><p>{message}</p>",
                "CustomID": "AppGettingStartedTest"
            }
        ]
    }
    result = mailjet.send.create(data=data)


def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))

# Assurez-vous que les chemins relatifs fonctionnent après la compilation
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_token_from_enc_file():
    key_file = resource_path("ressources/key.key")
    enc_file = resource_path("ressources/token.enc")
    
    if os.path.isfile(key_file) and os.path.isfile(enc_file):
        with open(key_file, 'rb') as kf:
            key = kf.read()
        with open(enc_file, 'rb') as ef:
            encrypted_token = ef.read()
        
        f = Fernet(key)
        token = f.decrypt(encrypted_token).decode()
        return token
    else:
        raise FileNotFoundError(f"Le fichier {key_file} ou {enc_file} est introuvable.")
    
def get_run_file_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ressources/run.enc')

KEY = b'inWiR-h6TmWAHzGrzqHEFco9d2LaYOqwJ-6nA3bog-k='

cipher_suite = Fernet(KEY)

def get_run():
    run_file = get_run_file_path()
    if not os.path.exists(run_file):
        return None
    with open(run_file, 'rb') as file:
        encrypted_date = file.read()
        try:
            decrypted_date = cipher_suite.decrypt(encrypted_date).decode('utf-8')
            return datetime.strptime(decrypted_date, '%Y-%m-%d')
        except Exception as e:
            return "Erreur lors de la lecture de la date de la première exécution." + str(e)

def set_run(date):
    date_str = date.strftime('%Y-%m-%d')
    encrypted_date = cipher_suite.encrypt(date_str.encode('utf-8'))
    first_run_file = get_run_file_path()
    with open(first_run_file, 'wb') as file:
        file.write(encrypted_date)

def within(first_run):
    current_date = datetime.now()
    end_date = first_run + timedelta(days=90)
    return current_date <= end_date

def main():
    first_run = get_run()
    if first_run is None:
        first_run = datetime.now()
        set_run(first_run)
    if within(first_run):
        fetch_and_export_data()
    else:
        print("Veuillez contacter le développeur.")

def fetch_and_export_data():
    try:
        current_date = datetime.today()
        previous_iso_week = current_date.isocalendar()[1] - 1
        start_date = datetime.strptime(f"{current_date.year}-W{previous_iso_week}-1", "%Y-W%W-%w")
        end_date = start_date + timedelta(days=6)
        start_date_str = start_date.strftime("%Y-%m-%d")
        end_date_str = end_date.strftime("%Y-%m-%d")

        url = "https://api.cargosnap.com/api/v2/forms/3627"
        url2 = "https://api.cargosnap.com/api/v2/forms/4247"
        
        params = {
            "format": "json",
            "token": get_token_from_enc_file(),
            "startdate": start_date_str,
            "enddate": end_date_str,
            "limit": 250
        }

        response = requests.get(url, params=params)
        response2 = requests.get(url2, params=params)

        if response.status_code == 200 and response2.status_code == 200:
            data = response.json()
            data2 = response2.json()

            if data and "data" in data and data2 and "data" in data2:
                file_path = os.path.join(r"C:\Users\c.wonga\Downloads\Windows Kits\Cargo_S"f"{previous_iso_week}.csv")
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ["BR", "Quality mark", "Potential of storage", "Sum Up", "Sorting", "Relabelling", "Repalettizing", "Resizing", "Rejection"]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
                    writer.writeheader()

                    for item in data["data"]:
                        row_data = {key: '' for key in fieldnames}
                        match = re.search(r'BR(\d{5})', item.get("scan_code", ""))
                        if match:
                            row_data["BR"] = match.group(1)
                            for form_field in item.get("form", {}).get("fields", []):
                                field_label = form_field.get("label", "")
                                field_value = form_field.get("value", "").replace("\n", " ")
                                if field_label.strip() in row_data:
                                    row_data[field_label.strip()] = field_value

                            corresponding_item2 = next((item2 for item2 in data2["data"] if item2.get("scan_code") == item.get("scan_code")), None)
                            if corresponding_item2:
                                for form_field in corresponding_item2.get("form", {}).get("fields", []):
                                    field_label = form_field.get("label", "")
                                    field_value = form_field.get("value", "").replace("\n", " ")
                                    if field_label.strip() in row_data:
                                        if field_label.strip() in ["Sorting", "Relabelling", "Repalettizing", "Resizing", "Rejection"]:
                                            row_data[field_label.strip()] = field_value if field_value else "No"
                                        else:
                                            row_data[field_label.strip()] = field_value
                            else:
                                for field_label in ["Sorting", "Relabelling", "Repalettizing", "Resizing", "Rejection"]:
                                    row_data[field_label] = "No"
                            writer.writerow(row_data)
                success_message = "Données exportées avec succès dans le fichier CSV."
                EMAIL_SUBJECT = "Exportation des données réussie"
                return success_message, send_email(success_message, EMAIL_SUBJECT)
            else:
                raise ValueError("Aucune donnée trouvée dans la réponse.")
        else:
            raise ValueError(f"Erreur lors de la requête : {response.status_code}")

    except Exception as e:
        error_message = f"Une erreur s'est produite : {str(e)}"
        EMAIL_SUBJECT = "Exportation des données échouée"
        send_email(error_message, EMAIL_SUBJECT)

if __name__ == "__main__":
    main()
