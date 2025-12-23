import json
import os
import config

def _charger_db_globale():
    """
    Fonction interne pour charger tout le JSON de préférences.
    Si le fichier n'existe pas, il initialise une structure vide.
    """
    if not os.path.exists(config.FICHIER_PREFERENCES):
        # Structure de base par défaut
        donnees_base = {
            "villes_favorites": ["Paris", "Lyon", "Marseille", "Bordeaux"],
            "preferences_style": {}, # Prêt pour plus tard
            "profil_utilisateur": {} # Prêt pour plus tard
        }
        _sauvegarder_db_globale(donnees_base)
        return donnees_base
    
    try:
        with open(config.FICHIER_PREFERENCES, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"villes_favorites": ["Paris"]} # Sécurité crash

def _sauvegarder_db_globale(donnees):
    """Fonction interne pour écraser le JSON avec les nouvelles données."""
    with open(config.FICHIER_PREFERENCES, 'w', encoding='utf-8') as f:
        json.dump(donnees, f, indent=4, ensure_ascii=False)

# --- FONCTIONS SPÉCIFIQUES AUX VILLES ---

def recuperer_villes():
    """Renvoie uniquement la liste des villes."""
    db = _charger_db_globale()
    return db.get("villes_favorites", [])

def ajouter_ville(nom_ville):
    """Ajoute une ville à la liste."""
    db = _charger_db_globale()
    villes = db.get("villes_favorites", [])
    
    nom_propre = nom_ville.strip().title()
    
    if nom_propre not in villes:
        villes.append(nom_propre)
        db["villes_favorites"] = villes # Mise à jour du dict
        _sauvegarder_db_globale(db)     # Sauvegarde globale
        return True, f"✅ {nom_propre} ajoutée !"
    else:
        return False, f"⚠️ {nom_propre} est déjà là."

def supprimer_ville(nom_ville):
    """Supprime une ville."""
    db = _charger_db_globale()
    villes = db.get("villes_favorites", [])
    
    if nom_ville in villes:
        villes.remove(nom_ville)
        db["villes_favorites"] = villes
        _sauvegarder_db_globale(db)
        return True
    return False