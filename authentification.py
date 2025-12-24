import json
import os
import hashlib
import shutil
import config

# Fichier qui contient la liste des utilisateurs et mots de passe
FICHIER_USERS = config.FICHIER_USERS

def hash_mdp(password):
    """Transforme le mot de passe en suite de chiffres/lettres incompréhensible (SHA-256)"""
    return hashlib.sha256(password.encode()).hexdigest()

def charger_users():
    """Charge la liste des utilisateurs"""
    if not os.path.exists(FICHIER_USERS):
        return {}
    try:
        with open(FICHIER_USERS, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def creer_compte(username, password):
    """Crée un utilisateur et SON dossier personnel"""
    users = charger_users()
    
    # 1. Vérif si l'utilisateur existe déjà
    if username in users:
        return False, "Cet utilisateur existe déjà."
    
    if not username or not password:
        return False, "Pseudo et mot de passe obligatoires."
    
    # 2. Création du dossier de données personnel
    # Structure : data/pseudo_utilisateur/
    dossier_perso = os.path.join("data", username)
    dossier_images = os.path.join(dossier_perso, "images")
    
    if not os.path.exists(dossier_perso):
        os.makedirs(dossier_perso)     # Crée data/paul
        os.makedirs(dossier_images)    # Crée data/paul/images
    
    # 3. Enregistrement dans users.json
    users[username] = hash_mdp(password)
    
    with open(FICHIER_USERS, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4)
    
    return True, f"Compte {username} créé ! Connecte-toi."

def verifier_connexion(username, password):
    """Vérifie si le mot de passe est bon"""
    users = charger_users()
    # On compare le hash du mot de passe entré avec celui stocké
    if username in users and users[username] == hash_mdp(password):
        return True
    return False