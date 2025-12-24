import json
import os
import config

def _get_path_prefs(username):
    # Chaque user a son fichier de préférences dans son dossier
    return os.path.join("data", username, "preferences.json")

def _charger_db_user(username):
    path = _get_path_prefs(username) # <-- On a le bon chemin
    if not os.path.exists(path):
        donnees_base = {
            "villes_favorites": ["Paris", "Lyon", "Marseille", "Bordeaux"],
            "preferences_style": {},
            "profil_utilisateur": {}
        }
        _sauvegarder_db_user(username, donnees_base) # Appel corrigé
        return donnees_base
    
    try:
        # ERREUR DANS TON CODE : open(config.FICHIER_PREFERENCES...)
        # CORRECTION : open(path...)
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"villes_favorites": ["Paris"]}

def _sauvegarder_db_user(username, donnees):
    path = _get_path_prefs(username)
    # ERREUR DANS TON CODE : open(config.FICHIER_PREFERENCES...)
    # CORRECTION : open(path...)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(donnees, f, indent=4, ensure_ascii=False)

# --- FONCTIONS SPÉCIFIQUES AUX VILLES ---

def recuperer_villes(username):
    """Renvoie uniquement la liste des villes."""
    db = _charger_db_user(username)
    return db.get("villes_favorites", [])

def ajouter_ville(nom_ville, username):
    """Ajoute une ville à la liste."""
    db = _charger_db_user(username)
    villes = db.get("villes_favorites", [])
    
    nom_propre = nom_ville.strip().title()
    
    if nom_propre not in villes:
        villes.append(nom_propre)
        db["villes_favorites"] = villes # Mise à jour du dict
        _sauvegarder_db_user(username, db)     # Sauvegarde globale
        return True, f"✅ {nom_propre} ajoutée !"
    else:
        return False, f"⚠️ {nom_propre} est déjà là."

def supprimer_ville(nom_ville, username):
    """Supprime une ville."""
    db = _charger_db_user(username)
    villes = db.get("villes_favorites", [])
    
    if nom_ville in villes:
        villes.remove(nom_ville)
        db["villes_favorites"] = villes
        _sauvegarder_db_user(username, db)
        return True
    return False