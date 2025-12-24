import streamlit as st
import os
from gestion_donnees import ajouter_ville, recuperer_villes, supprimer_ville
from meteo_service import obtenir_meteo_actuelle, obtenir_prevision_meteo, analyser_meteo
from gestion_dressing import charger_garde_robe, choisir_tenue, prevision_semaine, laver_vetement, porter_vetement
from scanner_ia import scanner_dossier_images
from authentification import verifier_connexion, creer_compte
import config
from PIL import Image

def afficher_tenue(tenue, date):
    if isinstance(tenue, dict) and "erreur" in tenue:
        st.error(tenue['erreur'])
    elif isinstance(tenue, list):
        st.balloons()
        st.subheader(f"Voici la tenue idéale pour le {date}:")
        # Affichage en colonnes des vêtements proposés
        cols = st.columns(len(tenue))
        for i, v in enumerate(tenue):
            with cols[i]:
                st.image(v['chemin_image'], use_container_width=True)
                st.caption(f"**{v['nom']}**")
                st.text(f"{v['style']} • {v['couleur']}")

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Smart Wardrobe V3", page_icon="👔", layout="wide")

# --- CSS PERSONNALISÉ (Pour faire joli) ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
    }
    .img-container {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# --- GESTION DE SESSION (LOGIN) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = None

# SI L'UTILISATEUR N'EST PAS CONNECTÉ, ON AFFICHE JUSTE LE LOGIN
if not st.session_state['logged_in']:
    st.title("🔐 Smart Wardrobe - Connexion")
    st.info("Connecte-toi pour accéder à ta garde-robe personnelle.")
    
    tab_connexion, tab_inscription = st.tabs(["Se connecter", "Créer un compte"])
    
    with tab_connexion:
        user_input = st.text_input("Nom d'utilisateur", key="login_user")
        pass_input = st.text_input("Mot de passe", type="password", key="login_pass")
        
        if st.button("Se connecter"):
            if verifier_connexion(user_input, pass_input):
                st.session_state['logged_in'] = True
                st.session_state['username'] = user_input
                st.success("Connexion réussie ! (Rechargement...)")
                st.rerun()
            else:
                st.error("Identifiants incorrects.")

    with tab_inscription:
        new_user = st.text_input("Choisis un pseudo", key="new_user")
        new_pass = st.text_input("Choisis un mot de passe", type="password", key="new_pass")
        
        if st.button("S'inscrire"):
            succes, message = creer_compte(new_user, new_pass)
            if succes:
                st.success(message)
            else:
                st.warning(message)
    
    st.stop() # 🛑 ARRÊTE LE SCRIPT ICI SI PAS CONNECTÉ

# --- BARRE LATÉRALE : INFO UTILISATEUR ---
username = st.session_state['username']
st.sidebar.caption(f"👤 Connecté en tant que : **{username}**")

if st.sidebar.button("Déconnexion"):
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.rerun()

# --- SIDEBAR (Menu) ---
st.sidebar.title("👔 Smart Wardrobe")
menu = st.sidebar.radio(
    "Navigation", 
    ["🏠 Accueil & Styliste", "👗 Ma Garde-Robe", "🧺 Buanderie", "📸 Scanner / Ajouter"]
)

st.sidebar.markdown("---")
# 1. Chargement des villes depuis la DB générique
liste_villes = recuperer_villes(username)

# 2. Gestion de l'index par défaut
try:
    index_defaut = liste_villes.index(config.VILLE_DEFAULT)
except ValueError:
    index_defaut = 0

# 3. Le Sélecteur
choix_ville = st.sidebar.selectbox(
    "📍 Ma Localisation", 
    options=liste_villes + ["⚙️ Gérer mes villes..."]
)

# 4. Logique d'affichage
if choix_ville == "⚙️ Gérer mes villes...":
    st.sidebar.markdown("---")
    st.sidebar.subheader("Gestion des lieux")
    
    # AJOUT
    with st.sidebar.form("form_add_city"):
        nouvelle = st.text_input("Nouvelle ville :")
        btn_ajout = st.form_submit_button("Ajouter")
        
        if btn_ajout and nouvelle:
            succes, msg = ajouter_ville(nouvelle, username)
            if succes:
                st.success(msg)
                st.rerun()
            else:
                st.warning(msg)
            
    # SUPPRESSION
    ville_a_supprimer = st.sidebar.selectbox("Retirer une ville", liste_villes)
    if st.sidebar.button("🗑️ Supprimer la ville"):
        supprimer_ville(ville_a_supprimer, username)
        st.sidebar.success(f"{ville_a_supprimer} retirée.")
        st.rerun()
        
    ville = config.VILLE_DEFAULT # Valeur par défaut pendant qu'on configure
else:
    ville = choix_ville

# Chargement des données au démarrage
if 'vetements' not in st.session_state:
    vetements, manquants = charger_garde_robe(username)
    st.session_state['vetements'] = vetements

# --- PAGE 1 : ACCUEIL & STYLISTE ---
if menu == "🏠 Accueil & Styliste":
    st.title(f"Bonjour ! Météo à {ville}")
    
    vetements, manquants = charger_garde_robe(username)

    # 1. MÉTÉO
    if ville:
        date, temp, desc = obtenir_prevision_meteo(ville)
        temp_inst, desc_inst = obtenir_meteo_actuelle(ville)
        if date and isinstance(date, list) and len(date) > 0:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Température", value=f"{temp_inst}°C")
            with col2:
                st.info(f"Ciel : {desc_inst}")
            with col3:
                conseil_meteo = analyser_meteo(temp_inst, desc_inst)
                st.success(conseil_meteo)

            st.markdown("---")

            if manquants:
                st.warning(f"Il n'y a plus de vêtements propres pour le(s) type(s) : {', '.join(manquants)}")
            else:
                st.success("Tous tes vêtements sont propres ! 🎉")

            st.markdown("---")
            
            # 2. STYLISTE IA
            # --- 2. STYLISTE IA (INTERACTIF) ---
            st.header("🤖 Le Styliste IA")
            
            # A. Le bouton pour lancer la réflexion
            # On ne lance l'IA que si on n'a pas déjà une proposition en attente
            if 'proposition_ia' not in st.session_state:
                if st.button("✨ Suggère-moi une tenue pour demain !"):
                    with st.spinner("L'IA analyse tes vêtements et la météo..."):
                        # Appel à l'IA
                        vetements_actuels, _ = charger_garde_robe(username)
                        tenue_proposee = choisir_tenue(vetements_actuels, temp[0], desc[0])
                        
                        # On stocke le résultat en mémoire pour qu'il ne disparaisse pas
                        st.session_state['proposition_ia'] = tenue_proposee
                        st.rerun() # On recharge pour afficher le résultat

            # B. Zone de Validation (S'affiche uniquement si une proposition existe en mémoire)
            if 'proposition_ia' in st.session_state:
                tenue = st.session_state['proposition_ia']
                
                # On utilise ta fonction d'affichage existante
                afficher_tenue(tenue, date[0])
                
                # Si l'IA n'a pas renvoyé d'erreur, on affiche les boutons de choix
                if not (isinstance(tenue, dict) and "erreur" in tenue):
                    st.info("Cette tenue te convient-elle ?")
                    
                    col_oui, col_non = st.columns(2)
                    
                    with col_oui:
                        # --- BOUTON : J'ACCEPTE ---
                        if st.button("✅ Oui, je porte ça !", use_container_width=True):
                            # C'est MAINTENANT qu'on enregistre dans la base de données
                            for v in tenue:
                                porter_vetement(username, v['id'])
                            
                            st.balloons() # Petite fête
                            st.success("C'est noté ! Tenue enregistrée et vêtements marqués comme portés.")
                            
                            # On vide la mémoire pour pouvoir recommencer demain
                            del st.session_state['proposition_ia']
                            
                            # Petit délai pour lire le message puis rechargement
                            import time
                            time.sleep(2)
                            st.rerun()

                    with col_non:
                        # --- BOUTON : JE REFUSE ---
                        if st.button("❌ Non, propose autre chose", use_container_width=True):
                            # On ne fait rien d'autre que supprimer la proposition
                            del st.session_state['proposition_ia']
                            st.warning("Proposition ignorée. Tu peux relancer l'IA !")
                            st.rerun()
                
                else:
                    # Si c'était une erreur (ex: pas de vêtements propres), on ajoute un bouton pour effacer le message
                    if st.button("Réessayer"):
                        del st.session_state['proposition_ia']
                        st.rerun()

            # --- C. PARTIE SEMAINE (INTERACTIF) ---
            if 'proposition_semaine' not in st.session_state:
                if st.button("📅 Planifie ma semaine complète !"):
                    with st.spinner("L'IA organise ta semaine (simulation de l'usure incluse)..."):
                        # Appel à la fonction de simulation
                        vetements_actuels, _ = charger_garde_robe(username)
                        # Note : Assure-toi que 'date', 'temp', 'desc' sont bien disponibles (récupérés plus haut dans ton code météo)
                        resultat_semaine = prevision_semaine(vetements_actuels, date, temp, desc)
                        
                        st.session_state['proposition_semaine'] = resultat_semaine
                        st.rerun()

            # Affichage de la validation SEMAINE
            if 'proposition_semaine' in st.session_state:
                st.subheader("🗓️ Voici le planning proposé :")
                
                tenues_semaine = st.session_state['proposition_semaine']
                
                # Affichage jour par jour
                # On utilise 'date' qui vient de la météo (assure-toi qu'elle est dispo dans le scope)
                for i, tenue_jour in enumerate(tenues_semaine):
                    if i < len(date): # Sécurité index
                        st.markdown(f"#### {date[i]}")
                        afficher_tenue(tenue_jour, date[i])
                        st.markdown("---")

                st.info("Veux-tu valider ce planning ? (Cela marquera tous ces vêtements comme portés)")

                col_valid_sem, col_refus_sem = st.columns(2)

                with col_valid_sem:
                    if st.button("✅ Valider la semaine", use_container_width=True):
                        # C'est ICI qu'on sauvegarde tout d'un coup
                        vetements_a_jour, _ = charger_garde_robe(username)
                        
                        count_vetements = 0
                        for tenue in tenues_semaine:
                            if isinstance(tenue, list):
                                for v in tenue:
                                    porter_vetement(username, v['id'])
                                    count_vetements += 1
                        
                        st.balloons()
                        st.success(f"Planning enregistré ! {count_vetements} vêtements marqués.")
                        del st.session_state['proposition_semaine']
                        
                        import time
                        time.sleep(2)
                        st.rerun()

                with col_refus_sem:
                    if st.button("❌ Refuser tout", use_container_width=True):
                        st.warning("Planning annulé.")
                        del st.session_state['proposition_semaine']
                        st.rerun()
        else:
            st.warning("Impossible de récupérer la météo. Vérifie le nom de la ville.")

# --- PAGE 2 : MA GARDE-ROBE (Galerie) ---
elif menu == "👗 Ma Garde-Robe":
    st.title("Mon Dressing")
    
    vetements, manquants = charger_garde_robe(username)
    
    # Filtres
    filtre_type = st.multiselect("Filtrer par type", ["haut", "bas", "chaussures", "veste", "t-shirt"])
    
    if filtre_type:
        vetements = [v for v in vetements if v['type'] in filtre_type]
    
    # Affichage en grille
    # On crée des lignes de 4 colonnes
    cols = st.columns(4)
    for index, v in enumerate(vetements):
        with cols[index % 4]:
            try:
                st.image(v['chemin_image'], use_container_width=True)
                st.markdown(f"**{v['nom']}**")
                
                # Indicateur de propreté
                if v['type'] == 't-shirt': limite = 1 
                elif v['type'] in ['bas', 'haut']: limite = 3
                else: limite = 100
                
                if v['nb_portes'] >= limite:
                    st.error(f"Sale ({v['nb_portes']} ports)")
                else:
                    st.success(f"Propre ({v['nb_portes']} ports)")
                    
                st.caption(f"ID: {v['id']} | {v['style']}")
            except:
                st.warning(f"Image introuvable : {v['nom']}")

# --- PAGE 3 : BUANDERIE (Machine à laver) ---
elif menu == "🧺 Buanderie":
    st.title("🧺 Ma Buanderie")
    
    vetements, manquants = charger_garde_robe(username)
    
    # --- 1. IDENTIFICATION DU LINGE SALE ---
    linge_sale = []
    for v in vetements:
        if v['type'] == 't-shirt': limite = 1 
        elif v['type'] in ['bas', 'haut']: limite = 3
        else: limite = 100
        
        if v.get('nb_portes', 0) >= limite:
            linge_sale.append(v)

    if not linge_sale:
        st.balloons()
        st.success("Tout est propre ! Profite de ta journée. ✨")
        st.image("https://media.giphy.com/media/3o6vXVzKWtkOIpyNMc/giphy.gif", width=300)
    else:
        # On divise l'écran : 
        # Colonne de GAUCHE (70%) : La grille des vêtements sales
        # Colonne de DROITE (30%) : Le Panier récapitulatif (fixe)
        col_grille, col_panier = st.columns([3, 1])
        
        panier_a_laver = [] # Liste temporaire pour stocker les sélections

        with col_grille:
            st.subheader(f"Pile de linge sale ({len(linge_sale)} articles)")
            
            # Bouton pour tout laver d'un coup (toujours utile)
            if st.button("⚡ Tout laver immédiatement"):
                with st.spinner("Grand nettoyage..."):
                    for v in linge_sale:
                        laver_vetement(username, v['id'])
                st.success("Tout est propre !")
                st.rerun()
            
            st.markdown("---")
            
            # GRILLE VISUELLE
            cols = st.columns(3) # 3 images par ligne
            for index, v in enumerate(linge_sale):
                with cols[index % 3]:
                    st.image(v['chemin_image'], use_container_width=True)
                    st.caption(f"**{v['nom']}** ({v['nb_portes']} ports)")
                    
                    # C'est ici que la magie opère : la Checkbox remplace le Drag & Drop
                    # Si coché, on l'ajoute à la liste 'panier_a_laver'
                    if st.checkbox("Mettre au panier", key=f"check_{v['id']}"):
                        panier_a_laver.append(v)
                    
                    st.markdown("---")

        # COLONNE DE DROITE : LE PANIER
        with col_panier:
            st.info(f"### 🛒 Mon Panier\n**{len(panier_a_laver)} articles sélectionnés**")
            
            if panier_a_laver:
                # On affiche la liste des items dans le panier
                for v in panier_a_laver:
                    st.write(f"▪️ {v['nom']}")
                
                st.markdown("---")
                
                # LE GROS BOUTON D'ACTION
                if st.button("🧼 LAVER LE PANIER", type="primary"):
                    with st.spinner("Lavage en cours..."):
                        for v in panier_a_laver:
                            laver_vetement(username, v['id'])
                    st.balloons()
                    st.toast("Panier lavé avec succès !")
                    st.rerun()
            else:
                st.caption("Coche les cases à gauche pour remplir ton panier.")

# --- PAGE 4 : SCANNER / AJOUTER ---
elif menu == "📸 Scanner / Ajouter":
    st.title("Ajouter un vêtement")
    
    tab1, tab2 = st.tabs(["📤 Import Manuel", "🤖 Scan Dossier Images"])
    
    with tab1:
        st.write("Upload une photo et laisse l'IA remplir la fiche technique.")
        
        # 1. On initialise une clé unique dans la mémoire si elle n'existe pas
        if 'cle_unique' not in st.session_state:
            st.session_state.cle_unique = 0

        # 2. Le File Uploader (avec la clé dynamique)
        # Tant que la clé ne change pas, le fichier reste là.
        fichier_upload = st.file_uploader(
            "Choisis une image", 
            type=['jpg', 'png', 'jpeg', 'webp'],
            key=f"uploader_{st.session_state.cle_unique}" # <-- L'astuce est ici
        )
        
        # 3. Dès qu'un fichier est chargé, on l'affiche (PREVIEW)
        if fichier_upload is not None:
            col_preview, col_bouton = st.columns([1, 2])
            
            with col_preview:
                st.image(fichier_upload, caption="Aperçu avant enregistrement", width=200)
            
            with col_bouton:
                st.write("L'image est prête !")
                # 4. Le bouton d'enregistrement
                if st.button("💾 Valider et Enregistrer l'image"):
                    
                    # A. Sauvegarde
                    dossier_user_images = os.path.join("data", username, "images") # Dossier perso
                    if not os.path.exists(dossier_user_images):
                        os.makedirs(dossier_user_images)

                    chemin_temp = os.path.join(dossier_user_images, fichier_upload.name)
                    
                    with open(chemin_temp, "wb") as f:
                        f.write(fichier_upload.getbuffer())
                    
                    # B. Feedback
                    st.success(f"Image {fichier_upload.name} sauvegardée !")
                    
                    # C. RESET : On change la clé pour forcer Streamlit à créer un "nouveau" chargeur vide
                    st.session_state.cle_unique += 1
                    
                    # D. On recharge la page immédiatement
                    st.rerun()
    with tab2:
        with st.spinner("Scan automatique de toutes les images du dossier `/images`."):
            if st.button("Lancer le Scan complet"):
                logs = scanner_dossier_images(username)
                
                # Affichage des logs
                if isinstance(logs, dict) and "erreur" in logs:
                    st.error(logs["erreur"])
                elif isinstance(logs, list):
                    st.write("Journal du scan :")
                    for ligne in logs:
                        if isinstance(ligne, str):
                            st.text(ligne)