from meteo_service import obtenir_prevision_meteo, analyser_meteo
from gestion_dressing import charger_garde_robe, choisir_tenue, prevision_semaine

def demarrer_application():
    print("--- 👔 SMART WARDROBE v1.0 ---")
    ville = input("Ville : ")
    
    mes_vetements = charger_garde_robe()
    
    date, temperature, desc = obtenir_prevision_meteo(ville)

    if temperature is None:
        return
    
    while True:
        print("\nQue veux-tu faire ?")
        print("1. Préparer ma tenue uniquement pour Demain")
        print("2. Préparer mes tenues pour toute la semaine")
        print("Q. Quitter")
        choix = input("Ton choix : ").lower()

        if choix == '1':
            print("\n--- SUGGESTION POUR DEMAIN ---")
            print(f"---ANALYSE Pour le {date[0]}---")
            print(f"\nTempérature : {temperature[0]}°C")
            print(f"Ciel : {desc[0]}")
            print(analyser_meteo(temperature[0], desc[0]))
            tenue = choisir_tenue(mes_vetements, temperature[0])
            print("\n👗 Tenue suggérée pour demain :")
            for v in tenue:
                if v['nom'] == "sale":
                    print(f"⚠️ Tous les {v['type']}s ont été portés. Veuillez laver vos {v['type']}.")
                else:
                    print(f"- {v['nom']} ({v['type']}, Chaleur: {v['chaleur']})")
            break

        elif choix == '2':
            print("\n--- SUGGESTIONS POUR LA SEMAINE ---")
            tenues_semaine = prevision_semaine(mes_vetements, date, temperature, desc)
            for i in range(len(tenues_semaine)):
                print(f"\n\n---ANALYSE Pour le {date[i]}---")
                print(f"\nTempérature : {temperature[i]}°C")
                print(f"Ciel : {desc[i]}")
                print(analyser_meteo(temperature[i], desc[i]))
                print(f"\n👗 Tenue suggérée :")
                tenue = tenues_semaine[i]
                for v in tenue:
                    if v['nom'] == "sale":
                        print(f"⚠️ Tous les {v['type']}s ont été portés. Veuillez laver vos {v['type']}.")
                    else:
                        print(f"- {v['nom']} ({v['type']}, Chaleur: {v['chaleur']})")
            break
        elif choix == 'q':
            print("Au revoir ! 👋")
            break
        else:
            print("Choix invalide. Veuillez relancer l'application.")

if __name__ == "__main__":
    demarrer_application()