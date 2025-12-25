import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import json

# 1. Chargement des variables (Local vs Cloud)
load_dotenv() # Pour le local (.env)

# Fonction pour récupérer une clé (soit du .env, soit des secrets Streamlit)
def get_key(key_name):
    # D'abord on regarde dans le .env local
    valeur = os.getenv(key_name)
    if valeur: return valeur
    # Sinon on regarde dans les secrets Streamlit Cloud
    if key_name in st.secrets:
        return st.secrets[key_name]
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

# 2. CONFIGURATION FIREBASE (La partie intelligente)
if not firebase_admin._apps:
    # Cas 1 : Streamlit Cloud (On lit le JSON depuis les secrets)
    if "firebase" in st.secrets:
        # On recrée le dictionnaire depuis les secrets
        key_dict = dict(st.secrets["firebase"])
        # Petite correction pour le format de la clé privée parfois capricieux
        key_dict["private_key"] = key_dict["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred)
    
    # Cas 2 : Local (On lit le fichier physique)
    elif os.path.exists("firebase_key.json"):
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
    
    else:
        st.error("❌ Impossible de trouver les clés Firebase (ni fichier, ni secrets).")

db = firestore.client()

# 3. CONFIGURATION GLOBALE
URL_METEO = "http://api.openweathermap.org/data/2.5/"
MODEL = "gemini-2.5-flash" 
VILLE_DEFAULT = "Paris"