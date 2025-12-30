import config
from firebase_admin import firestore

def envoyer_demande_ami(mon_pseudo, pseudo_destinataire):
    """Envoie une demande d'ami (Mise en attente)."""
    
    # 1. Vérifications de base
    if mon_pseudo == pseudo_destinataire:
        return False, "Tu ne peux pas t'ajouter toi-même !"
    
    users_ref = config.db.collection("users")
    dest_doc = users_ref.document(pseudo_destinataire).get()
    mon_doc = users_ref.document(mon_pseudo).get()

    if not dest_doc.exists:
        return False, f"L'utilisateur {pseudo_destinataire} n'existe pas."

    # 2. Vérifier si déjà amis ou demande déjà envoyée
    data_dest = dest_doc.to_dict()
    data_moi = mon_doc.to_dict()

    if pseudo_destinataire in data_moi.get("amis", []):
        return False, "Vous êtes déjà amis !"
    
    if mon_pseudo in data_dest.get("demandes_recues", []):
        return False, "Demande déjà envoyée, patience !"

    # 3. Envoyer la demande (Ajout dans la liste 'demandes_recues' du destinataire)
    try:
        users_ref.document(pseudo_destinataire).update({
            "demandes_recues": firestore.ArrayUnion([mon_pseudo])
        })
        return True, f"📩 Demande envoyée à {pseudo_destinataire} !"
    except Exception as e:
        return False, f"Erreur : {e}"

def supprimer_ami(mon_pseudo, pseudo_ami):
    """Supprime un ami (Rupture réciproque)."""
    try:
        users_ref = config.db.collection("users")
        
        # 1. Retirer de MA liste
        users_ref.document(mon_pseudo).update({
            "amis": firestore.ArrayRemove([pseudo_ami])
        })

        # 2. Retirer de SA liste (car l'amitié était partagée)
        users_ref.document(pseudo_ami).update({
            "amis": firestore.ArrayRemove([mon_pseudo])
        })
        
        return True, f"💔 Tu n'es plus ami avec {pseudo_ami}."
    except Exception as e:
        return False, f"Erreur : {e}"

def accepter_demande(mon_pseudo, pseudo_demandeur):
    """Accepte une demande : Devient ami réciproquement."""
    try:
        users_ref = config.db.collection("users")
        
        # A. Ajouter dans MES amis et retirer de MES demandes reçues
        users_ref.document(mon_pseudo).update({
            "amis": firestore.ArrayUnion([pseudo_demandeur]),
            "demandes_recues": firestore.ArrayRemove([pseudo_demandeur])
        })

        # B. M'ajouter dans SES amis (Réciprocité)
        users_ref.document(pseudo_demandeur).update({
            "amis": firestore.ArrayUnion([mon_pseudo])
        })
        
        return True, f"🎉 Tu es maintenant ami avec {pseudo_demandeur} !"
    except Exception as e:
        return False, f"Erreur : {e}"

def refuser_demande(mon_pseudo, pseudo_demandeur):
    """Refuse une demande (Supprime de la liste d'attente)."""
    try:
        users_ref = config.db.collection("users")
        users_ref.document(mon_pseudo).update({
            "demandes_recues": firestore.ArrayRemove([pseudo_demandeur])
        })
        return True, "Demande refusée."
    except Exception as e:
        return False, f"Erreur : {e}"

def recuperer_demandes_attente(username):
    """Récupère la liste des gens qui veulent être tes amis."""
    try:
        doc = config.db.collection("users").document(username).get()
        if doc.exists:
            return doc.to_dict().get("demandes_recues", [])
        return []
    except:
        return []

def recuperer_amis(username):
    """Récupère la liste officielle des amis."""
    try:
        doc = config.db.collection("users").document(username).get()
        if doc.exists:
            return doc.to_dict().get("amis", [])
        return []
    except:
        return []