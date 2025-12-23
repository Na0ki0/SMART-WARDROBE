from google import genai
from google.genai import types
import PIL.Image
import json
import config
import os
import shutil

# Configuration
client = genai.Client(api_key=config.GOOGLE_API_KEY)
DOSSIER_IMAGES = "images"  # Le nom de ton dossier

def analyser_vetement_sur_image(chemin_image):
    message = []
    message.append({"message": f"👀 Analyse de : {os.path.basename(chemin_image)} ..."})
    
    chemin_absolu = os.path.abspath(chemin_image)

    try:
        img = PIL.Image.open(chemin_image)
    except Exception as e:
        message.append({"erreur": f" Fichier ignoré (pas une image valide) : {e}"})
        return message

    # Prompt
    prompt = """
    Tu es un assistant de mode expert. Analyse cette photo de vêtement.
    Extrais les informations suivantes.
    
    Champs requis :
    - nom (str): nom court et descriptif (ex: "Jean Slim Bleu")
    - type (str): choisir strictement parmi ["haut", "bas", "t-shirt", "chaussures", "veste"]
    - couleur (str): la couleur principale
    - style (str): le style (ex: streetwear, casual, chic, sport)
    - coupe (str): la coupe (ex: slim, oversize, droit, ajusté)
    - chaleur (int): une note de 1 (très léger) à 10 (très chaud)
    """

    try:
        response = client.models.generate_content(
            model=config.MODEL,
            contents=[prompt, img],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        donnees_json = json.loads(response.text)
        donnees_json['nb_portes'] = 0
        donnees_json['chemin_image'] = chemin_absolu

        message.append({"donnee": donnees_json})
        
        return message

    except Exception as e:
        message.append({"erreur": f"Erreur API Gemini : {e}"})
        return message

def sauvegarder_dans_dressing(nouvel_objet):
    if not nouvel_objet: return

    db = []
    if os.path.exists(config.FICHIER_DB):
        with open(config.FICHIER_DB, 'r', encoding='utf-8') as f:
            try:
                db = json.load(f)
            except json.JSONDecodeError:
                db = []

    # --- DÉTECTION DOUBLONS ---
    for v in db:
        # 1. Même chemin de fichier
        if v.get('chemin_image') == nouvel_objet['chemin_image']:
            return {"erreur": f"⏩ DÉJÀ FAIT : {nouvel_objet['nom']} (Image déjà connue)."}

        # 2. Même vêtement (Nom + Couleur)
        if v['nom'] == nouvel_objet['nom'] and v['couleur'] == nouvel_objet['couleur']:
            return {"erreur": f"⏩ DÉJÀ FAIT : {nouvel_objet['nom']} (Vêtement existant)."}

    # --- SAUVEGARDE ---
    if db:
        max_id = max(v['id'] for v in db)
        nouvel_id = max_id + 1
    else:
        nouvel_id = 1
        
    nouvel_objet['id'] = nouvel_id
    db.append(nouvel_objet)
    
    with open(config.FICHIER_DB, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    
    return {"message": f"✅ AJOUTÉ : {nouvel_objet['nom']} (ID: {nouvel_id})"}

def scanner_dossier_images():
    message = []
    # Parcourt le dossier 'images' et traite tout ce qui s'y trouve.
    if not os.path.exists(DOSSIER_IMAGES):
        return {"erreur": f"Le dossier '{DOSSIER_IMAGES}' n'existe pas ! Crée-le et mets tes photos dedans."}

    fichiers = os.listdir(DOSSIER_IMAGES)
    images_trouvees = [f for f in fichiers if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

    if not images_trouvees:
        return {"erreur": f"📭 Le dossier '{DOSSIER_IMAGES}' est vide (aucune image .jpg/.png trouvée)."}

    message.append(f"📂 Dossier trouvé : {len(images_trouvees)} images à traiter.\n")

    for fichier in images_trouvees:
        chemin_complet = os.path.join(DOSSIER_IMAGES, fichier)
        
        # On lance l'analyse
        resultat = analyser_vetement_sur_image(chemin_complet)

        for item in resultat:
            if item and "message" in item:
                message.append(item["message"])
            if item and "erreur" in item:
                message.append(item["erreur"])
            # On tente de sauvegarder (la fonction gère les doublons)
            if item and "donnee" in item:
                sauvegarde = sauvegarder_dans_dressing(item["donnee"])
                if sauvegarde and "erreur" in sauvegarde:
                    message.append(sauvegarde["erreur"])
                elif sauvegarde and "message" in sauvegarde:
                    message.append(sauvegarde["message"])

        message.append("-" * 20) # Séparateur visuel

    return message