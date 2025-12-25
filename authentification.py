import os
import hashlib
import config
from firebase_admin import firestore

def hash_mdp(password):
    """Securité : On ne stocke jamais les mots de passe en clair."""
    return hashlib.sha256(password.encode()).hexdigest()

def creer_compte(username, password):
    """Crée un utilisateur dans Firestore et son dossier d'images local."""
    
    if not username or not password:
        return False, "Pseudo et mot de passe obligatoires."

    # 1. Référence au document utilisateur dans la collection 'users'
    doc_ref = config.db.collection("users").document(username)

    # 2. Vérifier si l'utilisateur existe déjà dans le Cloud
    if doc_ref.get().exists:
        return False, "Ce pseudo est déjà pris."

    # 3. Création du dossier LOCAL pour les images (Transition V5 Phase 1)
    # On garde ça pour l'instant car on n'a pas encore fait la Phase 2 (Cloudinary)
    dossier_images = os.path.join("data", username, "images")
    if not os.path.exists(dossier_images):
        os.makedirs(dossier_images)

    # 4. Enregistrement dans Google Firestore
    # On crée le document avec le mot de passe hashé ET les préférences par défaut
    try:
        doc_ref.set({
            "password": hash_mdp(password),
            "villes_favorites": ["Paris", "Lyon"],  # On initialise direct ici !
            "date_creation": firestore.SERVER_TIMESTAMP
        })
        return True, f"Compte {username} créé dans le Cloud ! Connecte-toi."
    except Exception as e:
        return False, f"Erreur connexion Cloud : {e}"

def verifier_connexion(username, password):
    """Vérifie les identifiants via Firestore."""
    try:
        # On va chercher le document de l'utilisateur
        doc_ref = config.db.collection("users").document(username)
        doc = doc_ref.get()

        if doc.exists:
            user_data = doc.to_dict()
            # On compare le mot de passe hashé
            if user_data.get("password") == hash_mdp(password):
                return True
                
        return False
    except:
        return False