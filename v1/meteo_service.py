import requests
import config

def obtenir_prevision_meteo(ville):
    url = f"{config.URL_METEO}forecast?q={ville}&appid={config.API_KEY}&units=metric&lang=fr"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        limite = min(40, len(data['list']))
        date = []
        temp = []
        description = []
        
        for i in range(8, limite, 8):
            prevision = data['list'][i]
            date.append(prevision['dt_txt'])
            temp.append(prevision['main']['temp'])
            description.append(prevision['weather'][0]['description'])
        
        return date, temp, description
    else:
        print("Erreur lors de la connexion à la météo !")
        return None, None, None
    
def analyser_meteo(temperature, description):
    if temperature < 5:
        return "Il fait très froid. Prends des vêtements chauds ! 🧥❄️"
    elif 5 <= temperature <= 15:
        return "Il fait frais. Pense à prendre une veste ou un pull. 🍂🧣"
    else:
        return "Il fait chaud. Opte pour des vêtements légers ! ☀️👕"