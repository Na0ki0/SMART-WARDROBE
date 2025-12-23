import os
from dotenv import load_dotenv

# 1. On charge les variables du fichier .env dans la mémoire
load_dotenv()

# 2. On récupère les clés de manière sécurisée
# Si le fichier .env n'existe pas, ces variables vaudront 'None'
API_KEY = os.getenv("OPENWEATHER_API_KEY")
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Vérification de sécurité (Optionnel mais recommandé) ---
if not API_KEY or not GOOGLE_API_KEY:
    print("⚠️ ALERTE : Les clés API sont introuvables. Vérifie ton fichier .env !")

# 3. Le reste de la configuration
FICHIER_DB = "garde_robe.json"
URL_METEO = "http://api.openweathermap.org/data/2.5/"

# Tu peux choisir le modèle ici (1.5 est plus stable, 2.5 est expérimental)
MODEL = "gemini-2.5-flash" 

# Données utilisateur
FICHIER_PREFERENCES = "donnees_app.json"
VILLE_DEFAULT = "Paris"