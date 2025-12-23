from meteo_service import obtenir_prevision_meteo, analyser_meteo
from gestion_dressing import charger_garde_robe, choisir_tenue, prevision_semaine
from scanner_ia import scanner_dossier_images, importer_image_manuelle


def demarrer_application():
    print("--- 👔 SMART WARDROBE v2.1 ---")
    ville = input("Ville : ")
    
    mes_vetements, manquants_types = charger_garde_robe()
    if manquants_types:
            print(f"Il n'y a plus de vêtements propres pour le(s) type(s) : {', '.join(manquants_types)}")
    
    date, temperature, desc = obtenir_prevision_meteo(ville)

    if date and "erreur" in date:
        print(f"{date['erreur']}")
        return
    
    while True:

        print("1. 🔮 Suggestion du jour")
        print("2. 📅 Préparer la semaine")
        print("3. ➕ Ajouter une nouvelle photo (Import)")
        print("4. 📸 Lancer le Scan IA (Analyse dossier)")
        print("Q. Quitter")
        choix = input("Ton choix : ").lower()

        if choix == '1':
            print("\n--- SUGGESTION POUR DEMAIN ---")
            print(f"---ANALYSE Pour le {date[0]}---")
            print(f"\nTempérature : {temperature[0]}°C")
            print(f"Ciel : {desc[0]}")
            print(analyser_meteo(temperature[0], desc[0]))
            print("🤔 Le styliste IA analyse tes vêtements...")
            tenue = choisir_tenue(mes_vetements, temperature[0], desc[0])
            print("\n👗 Tenue suggérée pour demain :")
            if tenue and "erreur" in tenue:
                print(f"{tenue['erreur']}")
            else:
                for v in tenue:
                    print(f"- {v['nom']} ({v['type']}, Chaleur: {v['chaleur']})")
                mes_vetements, manquants_types = charger_garde_robe()
                if manquants_types:
                        print(f"Il n'y a plus de vêtements propres pour le(s) type(s) : {', '.join(manquants_types)}")
            break
        elif choix == '2':
            print("\n--- SUGGESTIONS POUR LA SEMAINE ---")
            print("🤔 Le styliste IA analyse tes vêtements...")
            tenues_semaine = prevision_semaine(mes_vetements, date, temperature, desc)
            for i in range(len(tenues_semaine)):
                print(f"\n\n---ANALYSE Pour le {date[i]}---")
                print(f"\nTempérature : {temperature[i]}°C")
                print(f"Ciel : {desc[i]}")
                print(analyser_meteo(temperature[i], desc[i]))
                print(f"\n👗 Tenue suggérée :")
                tenue = tenues_semaine[i]
                if tenue and "erreur" in tenue:
                    print(f"{tenue['erreur']}")
                else:
                    for v in tenue:
                        print(f"- {v['nom']} ({v['type']}, Chaleur: {v['chaleur']})")
                    mes_vetements, manquants_types = charger_garde_robe()
                    if manquants_types:
                            print(f"Il n'y a plus de vêtements propres pour le(s) type(s) : {', '.join(manquants_types)}")
            break
        elif choix == '3':
            print("\n--- IMPORTER UNE IMAGE ---")
            succes = importer_image_manuelle()
            if succes and "erreur" in succes:
                    print(f"{succes['erreur']}")
            elif succes and "message" in succes:
                print(f"{succes['message']}")
                scan_now = input("Veux-tu lancer l'analyse IA sur cette image tout de suite ? (o/n) : ")
                if scan_now.lower() == 'o':
                    scanner_dossier_images()
                    mes_vetements, manquants_types = charger_garde_robe()
                    if manquants_types:
                            print(f"Il n'y a plus de vêtements propres pour le(s) type(s) : {', '.join(manquants_types)}")
        elif choix == '4':
            print("\n--- SCANNER IA ---")
            scan = scanner_dossier_images()

            if scan and "erreur" in scan:
                    print(f"{scan['erreur']}")
            else:
                    for s in scan:
                         print(s)
            mes_vetements, manquants_types = charger_garde_robe()
            if manquants_types:
                    print(f"Il n'y a plus de vêtements propres pour le(s) type(s) : {', '.join(manquants_types)}")
            print("🔄 Garde-robe rechargée avec succès !")
        elif choix == 'q':
            print("Au revoir ! 👋")
            break
        else:
            print("Choix invalide. Veuillez relancer l'application.")

if __name__ == "__main__":
    demarrer_application()