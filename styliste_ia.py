import os
import json
import config
from google import genai
from google.genai import types

# Initialisation du client
client = genai.Client(api_key=config.GOOGLE_API_KEY)

def demander_conseil_styliste(vetements, temperature, description_meteo):
    """
    Version Cloud V5 : Envoie les métadonnées (texte) au lieu des images.
    C'est plus rapide, plus fiable et ne consomme pas de bande passante inutile.
    """
    
    # 1. On prépare une liste "légère" pour l'IA (seulement les infos utiles)
    # On filtre pour ne garder que les vêtements propres (ou on laisse le gestionnaire le faire)
    inventaire_texte = []
    
    for v in vetements:
        # On vérifie si le vêtement est disponible (propre)
        # Note: Tu peux adapter cette condition selon ta logique
        if v.get('nb_portes', 0) < 5: 
            info = {
                "id": v.get('id'),
                "nom": v.get('nom'),
                "type": v.get('type'),
                "couleur": v.get('couleur'),
                "style": v.get('style'),
                "chaleur": v.get('chaleur')
            }
            inventaire_texte.append(info)

    if not inventaire_texte:
        return {"erreur": "Aucun vêtement propre ou disponible dans la liste."}

    # 2. Le Prompt (Texte uniquement)
    prompt = f"""
    Tu es un styliste personnel expert.
    
    CONTEXTE :
    - Météo : {description_meteo}, Température : {temperature}°C.
    - Garde-robe disponible (JSON) : {json.dumps(inventaire_texte, ensure_ascii=False)}
    
    TA MISSION :
    Choisis UNE seule tenue complète et cohérente adaptée à la météo.
    
    RÈGLES STRICTES :
    1. Choisis des articles compatibles (Style et Couleur).
    2. La "chaleur" cumulée doit être adaptée à la température ({temperature}°C).
    3. Renvoie UNIQUEMENT un JSON contenant la liste des IDs choisis et une explication courte.
    
    FORMAT ATTENDU :
    {{
        "ids_choisis": ["id_1", "id_2", ...],
        "explication": "J'ai choisi cette tenue car..."
    }}
    Ne mets pas de markdown (```json). Juste le JSON brut.
    """

    # 3. Appel à Gemini
    try:
        response = client.models.generate_content(
            model=config.MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        # 4. Nettoyage de la réponse
        texte_reponse = response.text
        if "```json" in texte_reponse: texte_reponse = texte_reponse.replace("```json", "").replace("```", "")
        elif "```" in texte_reponse: texte_reponse = texte_reponse.replace("```", "")
            
        resultat = json.loads(texte_reponse)
        return resultat

    except Exception as e:
        print(f"Erreur Styliste IA : {e}")
        return {"erreur": "Le styliste est momentanément indisponible."}