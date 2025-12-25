# 👗 Smart Wardrobe (V5 - Cloud Edition)

**Smart Wardrobe** est un assistant styliste personnel intelligent. L'application numérise votre garde-robe, analyse vos vêtements grâce à l'IA (Google Gemini) et vous suggère des tenues adaptées à la météo réelle de votre ville.

> **Nouveauté V5 :** L'application est désormais **Cloud Native**. Les données sont persistantes (Firestore) et les images sont hébergées en ligne (Cloudinary), permettant une utilisation depuis n'importe quel appareil sans perte de données.

---

## 🚀 Fonctionnalités Clés

* **☁️ Architecture 100% Cloud :** Plus de stockage local. Vos données et images sont sécurisées et accessibles partout.
* **📸 Scanner IA Intelligent :** Ajoutez une photo de vêtement, l'IA détecte automatiquement : Type, Couleur, Style, Coupe et Saisonnalité.
* **🎨 Styliste Virtuel :** En panne d'inspiration ? L'IA analyse la météo locale et compose une tenue cohérente avec vos vêtements propres.
* **📅 Planificateur :** Visualisez vos tenues pour la semaine à venir.
* **🧹 Gestion Automatisée :** Suivi du nombre de ports (sale/propre), mode "Buanderie", et suppression synchronisée (Base de données + Cloud).
* **🔐 Multi-Utilisateurs :** Système d'authentification sécurisé.

---

## 🛠️ Stack Technique

* **Langage :** Python 3.8+
* **Interface :** [Streamlit](https://streamlit.io/)
* **Intelligence Artificielle :** Google Gemini 1.5 Flash
* **Base de Données :** Google Firestore (NoSQL)
* **Stockage Images :** Cloudinary
* **Météo :** OpenWeatherMap API

---

## ⚙️ Installation en Local

1.  **Cloner le projet**
    ```bash
    git clone [https://github.com/votre-pseudo/SMART-WARDROBE.git](https://github.com/votre-pseudo/SMART-WARDROBE.git)
    cd SMART-WARDROBE
    ```

2.  **Installer les dépendances**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuration des Clés API (Fichier .env)**
    Créez un fichier `.env` à la racine et ajoutez vos clés :
    ```env
    OPENWEATHER_API_KEY="votre_cle_meteo"
    GEMINI_API_KEY="votre_cle_gemini"

    CLOUDINARY_CLOUD_NAME="votre_cloud_name"
    CLOUDINARY_API_KEY="votre_api_key"
    CLOUDINARY_API_SECRET="votre_api_secret"
    ```

4.  **Configuration Firebase**
    * Placez votre fichier `firebase_key.json` (téléchargé depuis la console Firebase) à la racine du projet.
    * *Note : Ce fichier est ignoré par Git pour la sécurité.*

5.  **Lancer l'application**
    ```bash
    streamlit run interface_web.py
    ```

---

## ☁️ Déploiement sur Streamlit Cloud

Pour mettre l'application en ligne, ne commitez JAMAIS vos fichiers de clés (`.env` ou `.json`). Utilisez les **Secrets** de Streamlit.

Dans la console Streamlit Cloud (**Settings** > **Secrets**), configurez comme suit :

```toml
OPENWEATHER_API_KEY = "votre_cle_meteo"
GEMINI_API_KEY = "votre_cle_gemini"
CLOUDINARY_CLOUD_NAME = "votre_cloud_name"
CLOUDINARY_API_KEY = "votre_api_key"
CLOUDINARY_API_SECRET = "votre_api_secret"

[firebase]
type = "service_account"
project_id = "votre-project-id"
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
client_email = "..."
client_id = "..."
auth_uri = "[https://accounts.google.com/o/oauth2/auth](https://accounts.google.com/o/oauth2/auth)"
token_uri = "[https://oauth2.googleapis.com/token](https://oauth2.googleapis.com/token)"
auth_provider_x509_cert_url = "[https://www.googleapis.com/oauth2/v1/certs](https://www.googleapis.com/oauth2/v1/certs)"
client_x509_cert_url = "..."