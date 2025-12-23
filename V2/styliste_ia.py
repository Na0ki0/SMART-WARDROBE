from google import genai
from google.genai import types
import PIL.Image
import json
import config
import os

# Client
client = genai.Client(api_key=config.GOOGLE_API_KEY)

def demander_conseil_styliste(vetements_dispo, meteo_temp, meteo_desc):
    """
    Charge les images des vêtements propres et les envoie à Gemini pour une analyse visuelle.
    Ne contient aucun print. Retourne un dict résultat ou un dict erreur.
    """
    
    # 1. PRÉPARATION DES DONNÉES
    candidats_json = []    # La liste textuelle descriptive pour l'IA
    images_a_envoyer = []  # La liste des objets images (pixels) pour l'IA
    
    # Compteur pour savoir si on a au moins essayé de traiter des vêtements
    vetements_propres_trouves = False

    for v in vetements_dispo:
        # Règle de propreté (identique à gestion_dressing)
        if v['type'] == 't-shirt':
            limite = 1 
        elif v['type'] in ['bas', 'haut']:
            limite = 3
        else:
            limite = 100
        
        if v.get('nb_portes', 0) < limite:
            vetements_propres_trouves = True
            chemin = v.get('chemin_image')
            
            # On tente de charger l'image silencieusement
            try:
                if chemin and os.path.exists(chemin):
                    # Ouverture de l'image
                    img = PIL.Image.open(chemin)
                    
                    # Ajout à la liste d'envoi multimodal
                    images_a_envoyer.append(img)
                    
                    # Ajout des métadonnées correspondantes
                    # 'index_image' fait le lien : l'image N°0 dans la liste correspond à ce JSON
                    candidats_json.append({
                        "index_image": len(images_a_envoyer) - 1, 
                        "id": v['id'],
                        "nom": v['nom'],
                        "type": v['type'],
                        "couleur": v['couleur'],
                        "style": v['style']
                    })
                # Si l'image n'existe pas, on ignore silencieusement ce vêtement pour l'analyse visuelle
                # (Ou on pourrait l'ajouter sans index_image, mais pour le styliste visuel, on filtre)
            except Exception:
                # En cas d'image corrompue, on continue sans planter et sans print
                continue

    # 2. GESTION DES ERREURS (Retours pour app.py)
    if not vetements_propres_trouves:
        return {"erreur": "Tous tes vêtements sont sales ! Lance une machine. 🧼"}

    if not candidats_json:
        return {"erreur": "J'ai trouvé des vêtements propres, mais aucune image valide associée (chemins incorrects ?)."}

    # 3. CONSTRUCTION DU PROMPT
    inventaire_str = json.dumps(candidats_json, ensure_ascii=False)

    prompt = f"""
    Tu es un styliste de mode personnel expert doté de la vue.
    
    CONTEXTE :
    - Météo : {meteo_temp}°C, {meteo_desc}
    - INVENTAIRE : Tu as reçu une série d'images. Ci-dessous se trouve la liste JSON descriptive de ces images.
    - CORRESPONDANCE : Le champ 'index_image' dans le JSON correspond à la position de l'image dans la liste des fichiers reçus (0 = 1ère image, etc.).
    
    LISTE DES VÊTEMENTS (JSON) :
    {inventaire_str}

    TA MISSION :
    Regarde attentivement les images pour voir les textures, les nuances exactes et le style réel.
    Compose la meilleure tenue (Haut + Bas + (optionnel) Veste/Chaussures) en utilisant les IDs fournis.
    
    RÈGLES :
    1. Adapte-toi à la météo ({meteo_temp}°C).
    2. VISUEL : Utilise ta vision pour associer les couleurs et motifs (ex: ne mets pas deux motifs qui jurent).
    3. Si < 15°C, ajoute une veste.
    
    FORMAT DE RÉPONSE (JSON STRICT) :
    {{
        "message": "Phrase expliquant ton choix en citant un détail visuel (ex: 'Ce bleu s'accorde bien avec la texture du pantalon...')",
        "ids_choisis": [12, 5]
    }}
    """

    # 4. APPEL API MULTIMODAL
    # L'API Gemini prend une liste mixte : [Prompt (str), Image (PIL), Image (PIL)...]
    contenu_multimodal = [prompt] + images_a_envoyer

    try:
        response = client.models.generate_content(
            model=config.MODEL,
            contents=contenu_multimodal,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        return json.loads(response.text)

    except Exception as e:
        return {"erreur": f"Erreur du Styliste Visuel : {e}"}