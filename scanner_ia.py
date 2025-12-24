from google import genai
from google.genai import types
import PIL.Image
import json
import config
import os

client = genai.Client(api_key=config.GOOGLE_API_KEY)

def analyser_vetement_sur_image(chemin_image):
    # ... (Ta fonction d'analyse reste identique, je ne la copie pas pour gagner de la place)
    # GARDE TON CODE ACTUEL POUR CETTE FONCTION analyser_vetement_sur_image
    # ...
    # Juste assure-toi que chemin_image est bien passé en absolu
    message = []
    chemin_absolu = os.path.abspath(chemin_image)
    try:
        img = PIL.Image.open(chemin_image)
    except Exception as e:
        return [{"erreur": f"Image invalide: {e}"}]

    prompt = """
    Tu es un assistant de mode expert. Analyse cette photo de vêtement.
    Champs requis JSON : nom, type (haut, bas, t-shirt, chaussures, veste), couleur, style, coupe, chaleur (1-10).
    """
    try:
        response = client.models.generate_content(
            model=config.MODEL,
            contents=[prompt, img],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        donnees_json = json.loads(response.text)
        donnees_json['nb_portes'] = 0
        donnees_json['chemin_image'] = chemin_absolu
        message.append({"donnee": donnees_json})
        return message
    except Exception as e:
        message.append({"erreur": f"Erreur API: {e}"})
        return message

def sauvegarder_dans_dressing(nouvel_objet, username):
    if not nouvel_objet: return

    db = []
    # On construit le chemin VERS LE FICHIER DE L'USER
    path = os.path.join("data", username, "garde_robe.json")
    
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            try:
                db = json.load(f)
            except:
                db = []

    # DÉTECTION DOUBLONS
    for v in db:
        if v.get('chemin_image') == nouvel_objet['chemin_image']:
            return {"erreur": f"⏩ DÉJÀ FAIT : {nouvel_objet['nom']}"}

    # SAUVEGARDE
    if db:
        max_id = max(v['id'] for v in db)
        nouvel_id = max_id + 1
    else:
        nouvel_id = 1
        
    nouvel_objet['id'] = nouvel_id
    db.append(nouvel_objet)
    
    # CORRECTION ICI : On écrit bien dans 'path' et PAS dans config.FICHIER_DB
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
    
    return {"message": f"✅ AJOUTÉ : {nouvel_objet['nom']}"}

def scanner_dossier_images(username):
    message = []
    # On scanne le dossier PERSO
    dossier_images_user = os.path.join("data", username, "images")

    if not os.path.exists(dossier_images_user):
        return {"erreur": f"Dossier introuvable : {dossier_images_user}"}

    fichiers = os.listdir(dossier_images_user)
    images_trouvees = [f for f in fichiers if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

    if not images_trouvees:
        return {"erreur": f"📭 Ton dossier images est vide."}

    message.append(f"📂 Scan de {len(images_trouvees)} images pour {username}...\n")

    for fichier in images_trouvees:
        chemin_complet = os.path.join(dossier_images_user, fichier)
        resultat = analyser_vetement_sur_image(chemin_complet)

        for item in resultat:
            if "donnee" in item:
                # CORRECTION ICI : On passe le username !
                sauvegarde = sauvegarder_dans_dressing(item["donnee"], username)
                
                if sauvegarde and "message" in sauvegarde:
                    message.append(sauvegarde["message"])
                elif sauvegarde and "erreur" in sauvegarde:
                    message.append(sauvegarde["erreur"])
            elif "erreur" in item:
                message.append(item["erreur"])

    return message