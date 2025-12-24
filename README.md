# 👔 Smart Wardrobe (V4)

**Votre assistant styliste personnel propulsé par l'Intelligence Artificielle.**

Smart Wardrobe est une application Python (Streamlit) qui gère votre garde-robe, suit l'état de propreté de vos vêtements et utilise l'IA **Google Gemini** pour analyser visuellement vos habits et composer des tenues adaptées à la météo locale.

🚀 **Nouveauté V4 :** Support Multi-Utilisateurs sécurisé ! Chaque membre de la famille a son propre dressing et ses préférences.

## ✨ Fonctionnalités Principales

* **🤖 Styliste IA Visuel :** L'IA "regarde" vos vêtements (photos) et vous suggère une tenue complète en fonction de la météo et du style.
* **🌦️ Météo Intelligente :** Connexion en temps réel à OpenWeatherMap pour adapter les suggestions (pluie, froid, chaleur...).
* **📸 Scanner Automatique :** Importez une photo de vêtement, l'IA remplit automatiquement la fiche technique (Type, Couleur, Style, Coupe).
* **🧺 Gestion Buanderie :** Suivi automatique de l'usure. Les vêtements portés partent dans la corbeille "Linge sale" après X utilisations.
* **👥 Multi-Utilisateurs :** Création de comptes, login sécurisé et isolation des données (chaque utilisateur a son dossier privé).
* **📅 Planificateur Semaine :** Génération d'un planning de tenues pour la semaine en simulant l'usure des vêtements jour après jour.

## 🛠️ Prérequis technique

* Python 3.8 ou supérieur
* Une clé API **OpenWeatherMap** (Gratuite)
* Une clé API **Google Gemini** (Gratuite via Google AI Studio)

## 📦 Installation

1. **Cloner ou télécharger le projet**
   ```bash
   git clone [https://github.com/votre-pseudo/smart-wardrobe.git](https://github.com/votre-pseudo/smart-wardrobe.git)
   cd smart-wardrobe