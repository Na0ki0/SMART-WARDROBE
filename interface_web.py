import streamlit as st
import os
from gestion_donnees import ajouter_ville, recuperer_villes, supprimer_ville
from meteo_service import obtenir_meteo_actuelle, obtenir_prevision_meteo, analyser_meteo
from gestion_dressing import charger_garde_robe, choisir_tenue, prevision_semaine, laver_vetement
from scanner_ia import scanner_dossier_images
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

# --- SIDEBAR (Menu) ---
st.sidebar.title("👔 Smart Wardrobe")
menu = st.sidebar.radio(
    "Navigation", 
    ["🏠 Accueil & Styliste", "👗 Ma Garde-Robe", "🧺 Buanderie", "📸 Scanner / Ajouter"]
)

st.sidebar.markdown("---")
# 1. Chargement des villes depuis la DB générique
liste_villes = recuperer_villes()

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
            succes, msg = ajouter_ville(nouvelle)
            if succes:
                st.success(msg)
                st.rerun()
            else:
                st.warning(msg)
            
    # SUPPRESSION
    ville_a_supprimer = st.sidebar.selectbox("Retirer une ville", liste_villes)
    if st.sidebar.button("🗑️ Supprimer la ville"):
        supprimer_ville(ville_a_supprimer)
        st.sidebar.success(f"{ville_a_supprimer} retirée.")
        st.rerun()
        
    ville = config.VILLE_DEFAULT # Valeur par défaut pendant qu'on configure
else:
    ville = choix_ville

# Chargement des données au démarrage
if 'vetements' not in st.session_state:
    vetements, manquants = charger_garde_robe()
    st.session_state['vetements'] = vetements

# --- PAGE 1 : ACCUEIL & STYLISTE ---
if menu == "🏠 Accueil & Styliste":
    st.title(f"Bonjour ! Météo à {ville}")
    
    vetements, manquants = charger_garde_robe()

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
            st.header("🤖 Le Styliste IA")
            if st.button("✨ Suggère-moi une tenue pour demain !"):
                with st.spinner("L'IA analyse tes vêtements et la météo..."):
                    # On appelle ton cerveau IA
                    vetements_actuels, _ = charger_garde_robe()
                    tenue = choisir_tenue(vetements_actuels, temp[0], desc[0])
                    afficher_tenue(tenue, date[0])
                    st.success("Bonne journée ! 😎 (Tenue marquée comme portée)")
            if st.button("✨ Suggère-moi une tenue pour La semaine !"):
                with st.spinner("L'IA analyse tes vêtements et la météo..."):
                    # On appelle ton cerveau IA
                    vetements_actuels, _ = charger_garde_robe()
                    tenues_semaine = prevision_semaine(vetements_actuels, date, temp, desc)
                    for i in range(len(tenues_semaine)):
                        tenue = tenues_semaine[i]
                        afficher_tenue(tenue, date[i])
                        st.markdown("---")        
                    st.success("Bonne journée ! 😎 (Tenue marquée comme portée)")
        else:
            st.warning("Impossible de récupérer la météo. Vérifie le nom de la ville.")

# --- PAGE 2 : MA GARDE-ROBE (Galerie) ---
elif menu == "👗 Ma Garde-Robe":
    st.title("Mon Dressing")
    
    vetements, manquants = charger_garde_robe()
    
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
    
    vetements, manquants = charger_garde_robe()
    
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
                        laver_vetement(vetements, v['id'])
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
                            laver_vetement(vetements, v['id'])
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
                    chemin_temp = os.path.join("images", fichier_upload.name)
                    if not os.path.exists("images"):
                        os.makedirs("images")
                    
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
                logs = scanner_dossier_images()
                
                # Affichage des logs
                if isinstance(logs, dict) and "erreur" in logs:
                    st.error(logs["erreur"])
                elif isinstance(logs, list):
                    st.write("Journal du scan :")
                    for ligne in logs:
                        if isinstance(ligne, str):
                            st.text(ligne)