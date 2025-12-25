import config

def recuperer_villes(username):
    """Récupère la liste des villes depuis Firestore."""
    try:
        doc_ref = config.db.collection("users").document(username)
        doc = doc_ref.get()
        
        if doc.exists:
            # On renvoie la liste ou une liste vide si le champ n'existe pas
            return doc.to_dict().get("villes_favorites", [])
        return []
    except Exception as e:
        print(f"Erreur lecture villes : {e}")
        return []

def ajouter_ville(nom_ville, username):
    """Ajoute une ville dans la liste Firestore."""
    nom_propre = nom_ville.strip().title()
    
    try:
        doc_ref = config.db.collection("users").document(username)
        doc = doc_ref.get()
        
        if doc.exists:
            donnees = doc.to_dict()
            villes = donnees.get("villes_favorites", [])
            
            if nom_propre not in villes:
                villes.append(nom_propre)
                # MISE À JOUR DANS LE CLOUD
                doc_ref.update({"villes_favorites": villes})
                return True, f"✅ {nom_propre} ajoutée (Cloud) !"
            else:
                return False, f"⚠️ {nom_propre} est déjà là."
        return False, "Utilisateur introuvable."
        
    except Exception as e:
        return False, f"Erreur Cloud : {e}"

def supprimer_ville(nom_ville, username):
    """Supprime une ville de la liste Firestore."""
    try:
        doc_ref = config.db.collection("users").document(username)
        doc = doc_ref.get()
        
        if doc.exists:
            donnees = doc.to_dict()
            villes = donnees.get("villes_favorites", [])
            
            if nom_ville in villes:
                villes.remove(nom_ville)
                # MISE À JOUR DANS LE CLOUD
                doc_ref.update({"villes_favorites": villes})
                return True
                
        return False
    except Exception as e:
        print(f"Erreur suppression : {e}")
        return False