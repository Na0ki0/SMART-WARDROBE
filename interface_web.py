import streamlit as st
import os
from gestion_donnees import ajouter_ville, recuperer_villes, supprimer_ville
from meteo_service import obtenir_meteo_actuelle, obtenir_prevision_meteo, analyser_meteo
from gestion_dressing import charger_garde_robe, choisir_tenue, prevision_semaine, laver_vetement, porter_vetement, supprimer_vetement
from scanner_ia import traiter_et_sauvegarder_image
from authentification import verifier_connexion, creer_compte
from gestion_social import envoyer_demande_ami, accepter_demande, refuser_demande, recuperer_demandes_attente, recuperer_amis, supprimer_ami
import config
import time

def afficher_tenue(tenue, date):
    if isinstance(tenue, dict) and "erreur" in tenue:
        st.error(tenue['erreur'])
    elif isinstance(tenue, list):
        st.subheader(f"📅 {date}")
        cols = st.columns(len(tenue))
        for i, v in enumerate(tenue):
            with cols[i]:
                st.image(v['chemin_image'], use_container_width=True)
                st.caption(f"**{v['nom']}**")
                st.text(f"{v['style']} • {v['couleur']}")

def pimper_interface():
    st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        h1 {text-align: center; font-weight: 300; letter-spacing: 2px;}
        .stButton>button {
            border-radius: 25px;
            border: 1px solid #ddd;
            width: 100%;
        }
        .stButton>button:hover {
            border-color: #000;
        }
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="Smart Wardrobe V5", page_icon="👔", layout="wide")
pimper_interface()

# --- GESTION DE SESSION (LOGIN) ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = None

if not st.session_state['logged_in']:
    st.title("🔐 Smart Wardrobe")
    st.info("Connecte-toi pour accéder à ta garde-robe.")
    
    tab_connexion, tab_inscription = st.tabs(["Se connecter", "Créer un compte"])
    
    with tab_connexion:
        user_input = st.text_input("Nom d'utilisateur", key="login_user")
        pass_input = st.text_input("Mot de passe", type="password", key="login_pass")
        if st.button("Se connecter"):
            if verifier_connexion(user_input, pass_input):
                st.session_state['logged_in'] = True
                st.session_state['username'] = user_input
                st.success("Connexion réussie !")
                st.rerun()
            else:
                st.error("Identifiants incorrects.")

    with tab_inscription:
        new_user = st.text_input("Choisis un pseudo", key="new_user")
        new_pass = st.text_input("Choisis un mot de passe", type="password", key="new_pass")
        if st.button("S'inscrire"):
            succes, message = creer_compte(new_user, new_pass)
            if succes: st.success(message)
            else: st.warning(message)
    st.stop()

# --- INTERFACE PRINCIPALE ---
username = st.session_state['username']
st.sidebar.caption(f"👤 **{username}**")

if st.sidebar.button("Déconnexion"):
    st.session_state['logged_in'] = False
    st.rerun()

# --- CHARGEMENT DONNÉES ---
liste_villes = recuperer_villes(username)
if not liste_villes: liste_villes = [config.VILLE_DEFAULT]
choix_ville = st.sidebar.selectbox("📍 Ville", options=liste_villes + ["➕ Ajouter..."])

if choix_ville == "➕ Ajouter...":
    with st.sidebar.form("ajout_ville"):
        nouvelle = st.text_input("Ville :")
        valider = st.form_submit_button("OK")
        if valider:
            ajouter_ville(nouvelle, username)
            st.rerun()
    ville = config.VILLE_DEFAULT # On reste sur la ville par défaut pendant la saisie
else:
    ville = choix_ville
    st.sidebar.markdown("---")
    if st.sidebar.button(f"🗑️ Supprimer {ville}", key=f"del_city_{ville}"):
        supprimer_ville(ville, username)
        st.rerun()

st.title("👗 Smart Wardrobe")
tab_home, tab_dressing, tab_laundry, tab_social, tab_scan = st.tabs(["🏠 Accueil", "👗 Dressing", "🧺 Buanderie", "👥 Social", "📸 Scanner"])

with tab_home:
    st.header(f"Bonjour, météo à {ville}")
    date, temp, desc = obtenir_prevision_meteo(ville)
    temp_inst, desc_inst = obtenir_meteo_actuelle(ville)
    
    col1, col2, col3 = st.columns(3)
    if temp_inst:
        col1.metric("Temp.", f"{temp_inst}°C")
        col2.info(f"{desc_inst}")
        col3.success(analyser_meteo(temp_inst, desc_inst))
    
    st.markdown("---")
    
    # TENUE DU JOUR
    st.subheader("✨ Tenu pour demain")
    if 'tenue_du_jour' not in st.session_state:
        if st.button("Proposer une tenue pour demain"):
            with st.spinner("Le styliste réfléchit..."):
                vetements, _ = charger_garde_robe(username)
                if date and temp and desc:
                    tenue_jour = choisir_tenue(vetements, temp[0], desc[0])
                    st.session_state['tenue_du_jour'] = tenue_jour
                    st.rerun()
                else:
                    st.error("Météo indisponible.")
    if 'tenue_du_jour' in st.session_state:
        tenue = st.session_state['tenue_du_jour']
        afficher_tenue(tenue, "Demain")

        col_valid_sem, col_refus_sem = st.columns(2)
        with col_valid_sem:
            if st.button("✅ Valider la tenue", use_container_width=True):
                vetements_a_jour, _ = charger_garde_robe(username)
                for v in tenue: porter_vetement(username, v['id'])
                st.balloons()
                st.success("Planning enregistré !")
                del st.session_state['tenue_du_jour']
                time.sleep(2)
                st.rerun()
        with col_refus_sem:
            if st.button("❌ Annuler", use_container_width=True):
                del st.session_state['tenue_du_jour']
                st.rerun()

    st.markdown("---")

    # PLANNING SEMAINE
    st.subheader("📅 Planning de la Semaine")
    if 'proposition_semaine' not in st.session_state:
        if st.button("Organiser ma semaine entière"):
            with st.spinner("L'IA organise ta semaine..."):
                vetements_actuels, _ = charger_garde_robe(username)
                if date and temp and desc:
                    resultat_semaine = prevision_semaine(vetements_actuels, date, temp, desc)
                    st.session_state['proposition_semaine'] = resultat_semaine
                    st.rerun()
                else:
                    st.error("Météo indisponible.")

    if 'proposition_semaine' in st.session_state:
        tenues_semaine = st.session_state['proposition_semaine']
        for i, tenue_jour in enumerate(tenues_semaine):
            if i < len(date): 
                afficher_tenue(tenue_jour, date[i])
                st.markdown("---")

        col_valid_sem, col_refus_sem = st.columns(2)
        with col_valid_sem:
            if st.button("✅ Valider la semaine", use_container_width=True):
                vetements_a_jour, _ = charger_garde_robe(username)
                for tenue in tenues_semaine:
                    if isinstance(tenue, list):
                        for v in tenue: porter_vetement(username, v['id'])
                st.balloons()
                st.success("Planning enregistré !")
                del st.session_state['proposition_semaine']
                time.sleep(2)
                st.rerun()
        with col_refus_sem:
            if st.button("❌ Annuler", use_container_width=True):
                del st.session_state['proposition_semaine']
                st.rerun()

with tab_dressing:
    st.header("Ma Collection")
    vetements, manquants = charger_garde_robe(username)
    
    filtre = st.multiselect("Filtrer", ["haut", "bas", "chaussures", "veste", "t-shirt"])
    if filtre: vetements = [v for v in vetements if v['type'] in filtre]
    
    cols = st.columns(4)
    for index, v in enumerate(vetements):
        with cols[index % 4]:
            with st.container(border=True):
                st.image(v['chemin_image'], use_container_width=True)
                st.markdown(f"**{v['nom']}**")
                
                # Jauge
                if v['type'] == 't-shirt': limite = 1 
                elif v['type'] in ['bas', 'haut']: limite = 3
                else: limite = 100
                nb = v.get('nb_portes', 0)
                
                if nb >= limite:
                    st.caption(f"🔴 Sale ({nb}/{limite})")
                    if st.button("Laver", key=f"lav_{v['id']}"):
                        laver_vetement(username, v['id'])
                        st.rerun()
                else:
                    st.progress(nb/limite)
                    st.caption(f"🟢 Propre ({nb}/{limite})")

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("👕", key=f"port_{v['id']}", help="Porter"):
                        porter_vetement(username, v['id'])
                        st.toast("Porté !", icon="✅")
                        time.sleep(0.5)
                        st.rerun()
                with c2:
                    if st.button("🗑️", key=f"del_{v['id']}", help="Supprimer"):
                        succes, msg = supprimer_vetement(username, v['id'])
                        if succes:
                            st.toast("Supprimé !", icon="🗑️")
                            time.sleep(1)
                            st.rerun()

with tab_laundry:
    st.header("🧺 Ma Buanderie")
    vetements, _ = charger_garde_robe(username)
    
    linge_sale = []
    for v in vetements:
        if v['type'] == 't-shirt': limite = 1 
        elif v['type'] in ['bas', 'haut']: limite = 3
        else: limite = 100
        if v.get('nb_portes', 0) >= limite:
            linge_sale.append(v)

    if not linge_sale:
        st.snow()
        st.success("Tout est propre ! ✨")
    else:
        col_grille, col_panier = st.columns([3, 1])
        panier_a_laver = [] 

        with col_grille:
            st.subheader(f"Pile de linge sale ({len(linge_sale)} articles)")
            if st.button("⚡ Tout laver immédiatement"):
                with st.spinner("Grand nettoyage..."):
                    for v in linge_sale: laver_vetement(username, v['id'])
                st.success("Tout est propre !")
                st.rerun()
            
            st.markdown("---")
            cols = st.columns(3)
            for index, v in enumerate(linge_sale):
                with cols[index % 3]:
                    st.image(v['chemin_image'], use_container_width=True)
                    st.caption(f"**{v['nom']}**")
                    if st.checkbox("Mettre au panier", key=f"check_{v['id']}"):
                        panier_a_laver.append(v)

        with col_panier:
            st.info(f"### 🛒 Panier\n**{len(panier_a_laver)} articles**")
            if panier_a_laver:
                if st.button("🧼 LAVER LE PANIER", type="primary"):
                    for v in panier_a_laver: laver_vetement(username, v['id'])
                    st.snow()
                    st.toast("Panier lavé !")
                    st.rerun()

with tab_social:
    st.header("👥 Mes Amis")

    # 1. NOTIFICATIONS (Demandes reçues)
    demandes = recuperer_demandes_attente(username)
    if demandes:
        st.info(f"🔔 Tu as {len(demandes)} nouvelle(s) demande(s) d'ami !")
        for demandeur in demandes:
            col_txt, col_ok, col_no = st.columns([3, 1, 1])
            col_txt.markdown(f"**{demandeur}** veut voir ton dressing.")
            
            if col_ok.button("✅ Accepter", key=f"acc_{demandeur}"):
                succes, msg = accepter_demande(username, demandeur)
                if succes: st.success(msg)
                st.rerun()
            
            if col_no.button("❌ Refuser", key=f"ref_{demandeur}"):
                refuser_demande(username, demandeur)
                st.rerun()
        st.markdown("---")

    # 2. CHERCHER / AJOUTER
    with st.expander("➕ Chercher un ami", expanded=False):
        c1, c2 = st.columns([3, 1])
        pseudo_dest = c1.text_input("Pseudo de l'ami", label_visibility="collapsed", placeholder="Ex: SophieMode")
        if c2.button("Envoyer demande"):
            succes, msg = envoyer_demande_ami(username, pseudo_dest)
            if succes: st.success(msg)
            else: st.warning(msg)

    # 3. MES AMIS & DRESSINGS
    st.subheader("Mes Amis")
    liste_amis = recuperer_amis(username)
    
    if not liste_amis:
        st.caption("Ta liste d'amis est vide. Lance des invitations !")
    else:
        # Sélecteur d'ami
        ami_selectionne = st.selectbox("👗 Voir le dressing de :", ["-- Choisir --"] + liste_amis)
        
        if ami_selectionne != "-- Choisir --":
            c_titre, c_delete = st.columns([3, 1])
            with c_titre:
                st.markdown(f"### Garde-robe de **{ami_selectionne}**")
            
            with c_delete:
                # Le bouton rouge pour supprimer
                if st.button("💔 Retirer ami", key=f"delete_{ami_selectionne}", type="secondary"):
                    succes, msg = supprimer_ami(username, ami_selectionne)
                    if succes:
                        st.toast(msg, icon="💔")
                        import time
                        time.sleep(1)
                        st.rerun() # On recharge pour mettre à jour la liste
                    else:
                        st.error(msg)

            # Chargement du dressing de l'ami
            vetements_ami, _ = charger_garde_robe(ami_selectionne)
            
            if not vetements_ami:
                st.warning(f"{ami_selectionne} n'a pas encore ajouté de vêtements.")
            else:
                # Affichage Read-Only (Pas de boutons d'action)
                cols = st.columns(4)
                for index, v in enumerate(vetements_ami):
                    with cols[index % 4]:
                        with st.container(border=True):
                            st.image(v['chemin_image'], use_container_width=True)
                            st.caption(f"**{v['nom']}**")
                            
                            # Petit système de Like "fictif" (Interaction UI)
                            if st.button("🔥 J'adore", key=f"like_{v['id']}"):
                                st.toast(f"Tu as envoyé du feu à {ami_selectionne} !", icon="🔥")

with tab_scan:
    st.header("Ajouter des vêtements")
    st.info("Sélectionne tes photos. Prévisualise-les, puis lance l'IA.")

    uploaded_files = st.file_uploader(
        "Choisis tes images", 
        type=['jpg', 'png', 'jpeg', 'webp'], 
        accept_multiple_files=True
    )

    if uploaded_files:
        st.markdown("---")
        st.subheader(f"👀 Aperçu ({len(uploaded_files)} images)")
        
        # --- AJOUT : PRÉVISUALISATION EN GRILLE ---
        cols_preview = st.columns(5) # 5 images par ligne
        for i, fichier in enumerate(uploaded_files):
            with cols_preview[i % 5]:
                st.image(fichier, use_container_width=True)
                st.caption(fichier.name)
        
        st.markdown("---")
        
        # Le bouton est maintenant sous la prévisualisation
        if st.button("🚀 Lancer l'analyse et l'ajout", type="primary"):
            
            barre = st.progress(0)
            status = st.empty()
            dossier_temp = os.path.join("data", username, "temp_upload")
            if not os.path.exists(dossier_temp): os.makedirs(dossier_temp)

            logs_complets = []

            for i, fichier in enumerate(uploaded_files):
                status.write(f"Traitement de : **{fichier.name}** ({i+1}/{len(uploaded_files)})...")
                
                chemin_temp = os.path.join(dossier_temp, fichier.name)
                with open(chemin_temp, "wb") as f:
                    f.write(fichier.getbuffer())
                
                logs = traiter_et_sauvegarder_image(chemin_temp, username)
                logs_complets.extend(logs)
                barre.progress((i + 1) / len(uploaded_files))

            status.success("✅ Terminé !")
            st.balloons()
            
            with st.expander("Voir le rapport", expanded=True):
                for l in logs_complets:
                    if "✅" in l: st.success(l)
                    elif "❌" in l: st.error(l)
                    else: st.info(l)
            
            if st.button("Rafraîchir ma garde-robe"):
                st.rerun()