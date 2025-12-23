import requests
import config

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
                    date.append(prevision['dt_txt'])
                    temp.append(prevision['main']['temp'])
                    description.append(prevision['weather'][0]['description'])
        
        return date, temp, description
    else:
        return {"erreur": "Erreur lors de la connexion à la météo !"}, None, None
    
def analyser_meteo(temperature, description):
    if temperature < 5:
        return "Il fait très froid. Prends des vêtements chauds ! 🧥❄️"
    elif 5 <= temperature <= 15:
        return "Il fait frais. Pense à prendre une veste ou un pull. 🍂🧣"
    else:
        return "Il fait chaud. Opte pour des vêtements légers ! ☀️👕"