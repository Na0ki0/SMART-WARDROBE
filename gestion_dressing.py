import config
import os
from firebase_admin import firestore
import cloudinary.uploader # Nécessaire pour la suppression
from styliste_ia import demander_conseil_styliste
import copy

def get_ref_dressing(username):
    return config.db.collection("users").document(username).collection("garde_robe")

def charger_garde_robe(username):
    try:
        docs = get_ref_dressing(username).stream()
        vetements = []
        for doc in docs:
            v = doc.to_dict()
            v['id'] = doc.id
            vetements.append(v)
            
        manquants_types = types_sans_propres(vetements)
        return vetements, manquants_types
    except Exception as e:
        print(f"Erreur chargement dressing : {e}")
        return [], []

def porter_vetement(username, id_vetement):
    try:
        doc_ref = get_ref_dressing(username).document(str(id_vetement))
        doc_ref.update({"nb_portes": firestore.Increment(1)})
    except Exception as e:
        print(f"Erreur porter vêtement : {e}")

def laver_vetement(username, id_vetement):
    try:
        doc_ref = get_ref_dressing(username).document(str(id_vetement))
        doc_ref.update({"nb_portes": 0})
    except Exception as e:
        print(f"Erreur lavage : {e}")

def supprimer_vetement(username, id_vetement):
    """Supprime de Firestore ET de Cloudinary."""
    try:
        doc_ref = get_ref_dressing(username).document(str(id_vetement))
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            chemin_image = data.get('chemin_image', '')
            
            # --- SUPPRESSION CLOUDINARY ---
            if "cloudinary.com" in str(chemin_image):
                try:
                    # L'URL ressemble à : .../upload/v12345/smart_wardrobe/Paul/image.jpg
                    # Il faut extraire : smart_wardrobe/Paul/image (sans extension)
                    
                    # 1. On sépare après le mot "upload/"
                    partie_utile = chemin_image.split("upload/")[1]
                    
                    # 2. On enlève le numéro de version (v12345/) s'il existe
                    if "/" in partie_utile:
                        elements = partie_utile.split("/")
                        # Si le premier élément commence par 'v' et est suivi de chiffres, on le saute
                        if elements[0].startswith("v") and elements[0][1:].isdigit():
                            elements = elements[1:]
                        chemin_clean = "/".join(elements)
                    else:
                        chemin_clean = partie_utile

                    # 3. On enlève l'extension (.jpg, .png)
                    public_id = os.path.splitext(chemin_clean)[0]
                    
                    # 4. Destruction
                    cloudinary.uploader.destroy(public_id)
                    print(f"🗑️ Image Cloudinary supprimée : {public_id}")
                    
                except Exception as e:
                    print(f"⚠️ Erreur suppression image Cloudinary (non bloquant) : {e}")
            
            # --- SUPPRESSION LOCALE (Sécurité si ancien fichier) ---
            elif chemin_image and os.path.exists(chemin_image):
                try:
                    os.remove(chemin_image)
                except:
                    pass

            # --- SUPPRESSION FIRESTORE ---
            doc_ref.delete()
            return True, "🗑️ Vêtement supprimé (DB + Image)."
            
        return False, "Vêtement introuvable."
    except Exception as e:
        return False, f"Erreur suppression : {e}"

# --- FONCTIONS UTILITAIRES (Inchangées) ---

def est_propre(v):
    if v.get('type') == 't-shirt': limite = 1
    elif v.get('type') in ['bas', 'haut']: limite = 3
    else: limite = 100
    return v.get('nb_portes', 0) < limite

def types_sans_propres(vetements, types_a_verifier=None):
    types = set(v.get('type', 'inconnu') for v in vetements)
    cible = types_a_verifier if types_a_verifier is not None else types
    return [t for t in cible if not any(est_propre(v) and v.get('type') == t for v in vetements)]

def choisir_tenue(vetements, temperature, description):
    reponse_ia = demander_conseil_styliste(vetements, temperature, description)
    if reponse_ia and "ids_choisis" in reponse_ia:
        tenue = []
        ids_choisis_str = [str(x) for x in reponse_ia['ids_choisis']]
        for v in vetements:
            if str(v['id']) in ids_choisis_str:
                tenue.append(v)
        return tenue
    elif reponse_ia and "erreur" in reponse_ia:
        return {"erreur": f"{reponse_ia['erreur']}"}
    else:
        return {"erreur": "L'IA n'a pas trouvé d'inspiration..."}

def prevision_semaine(vetements, date, temperature, description_meteo):
    vetements_simules = copy.deepcopy(vetements)
    tenues_semaine = []
    
    for i in range(len(date)):
        tenue = choisir_tenue(vetements_simules, temperature[i], description_meteo[i])
        tenues_semaine.append(tenue)
        
        if isinstance(tenue, list):
            for v_choisi in tenue:
                for v_stock in vetements_simules:
                    if str(v_stock['id']) == str(v_choisi['id']):
                        v_stock['nb_portes'] += 1
                        break
    return tenues_semaine