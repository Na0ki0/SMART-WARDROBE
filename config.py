import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import json

# 1. Chargement des variables (Local .env)
load_dotenv()

# Fonction ROBUSTE pour récupérer une clé
def get_key(key_name):
    # D'abord on regarde dans le .env local (Priorité Local)
    valeur = os.getenv(key_name)
    if valeur: 
        return valeur
    
    # Sinon on regarde dans les secrets Streamlit Cloud
    # On met un try/except car accéder à st.secrets sans fichier local fait planter l'appli
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except FileNotFoundError:
        pass # On est en local sans secrets.toml, ce n'est pas grave
    except Exception:
        pass 
        
    return None

API_KEY = get_key("OPENWEATHER_API_KEY")
GOOGLE_API_KEY = get_key("GEMINI_API_KEY")

# --- CONFIGURATION CLOUDINARY ---
cloudinary.config(
  cloud_name = get_key('CLOUDINARY_CLOUD_NAME'),
  api_key = get_key('CLOUDINARY_API_KEY'),
  api_secret = get_key('CLOUDINARY_API_SECRET'),
  secure = True
)

# 2. CONFIGURATION FIREBASE (La partie intelligente et blindée)
if not firebase_admin._apps:
    firebase_initialized = False

    # CAS A : On essaie d'abord le fichier LOCAL (firebase_key.json)
    # C'est le plus sûr pour le développement sur ton PC
    if os.path.exists("firebase_key.json"):
        try:
            cred = credentials.Certificate("firebase_key.json")
            firebase_admin.initialize_app(cred)
            firebase_initialized = True
            print("✅ Firebase chargé depuis fichier JSON local.")
        except Exception as e:
            st.error(f"Erreur lecture JSON local : {e}")

    # CAS B : Si pas de fichier local, on essaie les SECRETS CLOUD
    if not firebase_initialized:
        try:
            # On vérifie si 'firebase' existe dans les secrets sans faire planter
            if "firebase" in st.secrets:
                key_dict = dict(st.secrets["firebase"])
                key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")
                cred = credentials.Certificate(key_dict)
                firebase_admin.initialize_app(cred)
                firebase_initialized = True
                print("☁️ Firebase chargé depuis Secrets Streamlit.")
        except:
            pass # Pas de secrets, on continue

    # CAS C : Si rien n'a marché
    if not firebase_initialized:
        st.error("❌ ERREUR FATALE : Impossible de trouver les clés Firebase (ni fichier json, ni secrets cloud).")
        st.stop()

db = firestore.client()

# 3. CONFIGURATION GLOBALE
URL_METEO = "http://api.openweathermap.org/data/2.5/"
MODEL = "gemini-2.5-flash" 
VILLE_DEFAULT = "Paris"