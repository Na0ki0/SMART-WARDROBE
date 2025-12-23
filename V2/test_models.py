from google import genai
import config

client = genai.Client(api_key=config.GOOGLE_API_KEY)

print("🔍 Recherche des modèles disponibles...")
try:
    # On liste les modèles
    for model in client.models.list():
        if "gemini" in model.name:
            print(f"✅ Disponible : {model.name}")
except Exception as e:
    print(f"❌ Erreur : {e}")