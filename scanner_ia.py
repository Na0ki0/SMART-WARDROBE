from google import genai
from google.genai import types
import PIL.Image
import json
import config
import os
import cloudinary.uploader

client = genai.Client(api_key=config.GOOGLE_API_KEY)

def analyser_vetement_sur_image(chemin_image):
    """Analyse l'image locale pour extraire les données JSON via Gemini."""
    message = []
    chemin_absolu = os.path.abspath(chemin_image)
    
    try:
        img = PIL.Image.open(chemin_image)
    except Exception as e:
        return [{"erreur": f"Image invalide: {e}"}]

    prompt = """
    Tu es un assistant de mode expert. Analyse cette photo de vêtement.
    Champs requis JSON : nom, type (haut, bas, t-shirt, chaussures, veste), couleur, style, coupe, chaleur (1-10).
    Réponds UNIQUEMENT avec le JSON, sans balises markdown.
    """
    try:
        response = client.models.generate_content(
            model=config.MODEL,
            contents=[prompt, img],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        texte_reponse = response.text
        
        # Nettoyage Markdown
        if "```json" in texte_reponse: texte_reponse = texte_reponse.replace("```json", "").replace("```", "")
        elif "```" in texte_reponse: texte_reponse = texte_reponse.replace("```", "")
            
        donnees_json = json.loads(texte_reponse)
        
        if isinstance(donnees_json, list):
            if len(donnees_json) > 0: donnees_json = donnees_json[0]
            else: return [{"erreur": "L'IA a renvoyé une liste vide."}]
        
        donnees_json['nb_portes'] = 0
        donnees_json['chemin_image'] = chemin_absolu 
        
        message.append({"donnee": donnees_json})
        return message

    except Exception as e:
        message.append({"erreur": f"Erreur API ou Parsing: {e}"})
        return message

def sauvegarder_dans_dressing(nouvel_objet, username):
    if not nouvel_objet: return {"erreur": "Objet vide"}

    try:
        collection_ref = config.db.collection("users").document(username).collection("garde_robe")
        
        # Vérification doublons par nom
        docs = collection_ref.where("nom", "==", nouvel_objet['nom']).stream()
        for doc in docs:
             return {"erreur": f"⏩ DÉJÀ PRÉSENT (Nom similaire) : {nouvel_objet['nom']}"}

        # Ajout Firestore
        update_time, doc_ref = collection_ref.add(nouvel_objet)
        doc_ref.update({"id": doc_ref.id})
        
        return {"message": f"✅ AJOUTÉ : {nouvel_objet['nom']}"}
        
    except Exception as e:
        return {"erreur": f"Erreur sauvegarde Cloud : {e}"}

def traiter_et_sauvegarder_image(chemin_complet, username):
    logs = []
    
    # 1. Analyse IA
    resultat = analyser_vetement_sur_image(chemin_complet)

    for item in resultat:
        if "donnee" in item:
            donnees = item["donnee"]
            
            # 2. Upload Cloudinary
            try:
                reponse_cloud = cloudinary.uploader.upload(
                    chemin_complet,
                    folder=f"smart_wardrobe/{username}" 
                )
                url_image = reponse_cloud['secure_url']
                donnees['chemin_image'] = url_image
                
                # 3. Sauvegarde Firestore
                sauvegarde = sauvegarder_dans_dressing(donnees, username)
                
                if sauvegarde and "message" in sauvegarde:
                    logs.append(sauvegarde["message"])
                    # 4. Suppression locale
                    try:
                        os.remove(chemin_complet)
                    except: pass
                    
                elif sauvegarde and "erreur" in sauvegarde:
                    logs.append(sauvegarde["erreur"])
                    
            except Exception as e_cloud:
                logs.append(f"❌ Erreur Upload Cloudinary : {e_cloud}")

        elif "erreur" in item:
            logs.append(item["erreur"])
            
    return logs