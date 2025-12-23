import requests
import config
from datetime import datetime

def obtenir_prevision_meteo(ville):
    url = f"{config.URL_METEO}forecast?q={ville}&appid={config.API_KEY}&units=metric&lang=fr"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        date = []
        temp = []
        description = []

        for prevision in data['list']:
                # On ne garde que celles qui concernent "12:00:00"
                if "12:00:00" in prevision['dt_txt']:
                    date_brute = prevision['dt_txt']
                    date_belle = formater_date_fr(date_brute)
                    date.append(date_belle)
                    temp.append(prevision['main']['temp'])
                    description.append(prevision['weather'][0]['description'] + " " + obtenir_emoji(prevision['weather'][0]['description']))
        return date, temp, description
    else:
        return {"erreur": "Erreur lors de la connexion à la météo !"}, None, None
    
def obtenir_meteo_actuelle(ville):
    url = f"{config.URL_METEO}weather?q={ville}&appid={config.API_KEY}&units=metric&lang=fr"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        temperature = data['main']['temp']
        description = data['weather'][0]['description'] + " " + obtenir_emoji(data['weather'][0]['description'])
        return temperature, description
    else:
        return None, None
    
def analyser_meteo(temperature, description):
    if temperature < 5:
        return "Il fait très froid. Prends des vêtements chauds ! 🧥❄️"
    elif 5 <= temperature <= 15:
        return "Il fait frais. Pense à prendre une veste ou un pull. 🍂🧣"
    else:
        return "Il fait chaud. Opte pour des vêtements légers ! ☀️👕"
    
def obtenir_emoji(description):
    description = description.lower()
    if "pluie" in description:
        return "🌧️"
    elif "nuage" in description:
        return "☁️"
    elif "soleil" in description or "clair" in description:
        return "☀️"
    elif "neige" in description:
        return "❄️"
    elif "orage" in description:
        return "⛈️"
    else:
        return "🌤️"

def formater_date_fr(date_str):
    """Transforme '2023-12-25 12:00:00' en 'Lundi 25 décembre'"""
    # 1. On convertit le texte en objet Date
    dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    
    # 2. Listes manuelles (pour éviter les bugs de serveur)
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    
    # 3. On construit la belle chaîne
    return f"{jours[dt.weekday()]} {dt.day} {mois[dt.month-1]}"