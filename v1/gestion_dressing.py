import json
import random
import config

def charger_garde_robe():
    with open(config.FICHIER_DB, 'r', encoding='utf-8') as f:
        vetements = json.load(f)
        return vetements
    
def porter_vetement(vetements, id_vetement):
    trouve = False
    for v in vetements:
        if v['id'] == id_vetement:
            nb_actuel = v.get('nb_portes', 0)
            
            v['nb_portes'] = nb_actuel + 1

            trouve = True
            break

    if trouve:
        with open(config.FICHIER_DB, 'w', encoding='utf-8') as f:
            json.dump(vetements, f, indent=4, ensure_ascii=False)
    else:
        print("❌ Vêtement introuvable.")

def laver_vetement(vetements, id_vetement):
    trouve = False
    for v in vetements:
        if v['id'] == id_vetement:
            v['nb_portes'] = 0
            trouve = True
            break

    if trouve:
        with open(config.FICHIER_DB, 'w', encoding='utf-8') as f:
            json.dump(vetements, f, indent=4, ensure_ascii=False)
    else:
        print("❌ Vêtement introuvable.")

def choisir_tenue(vetements, temperature):
    suggestion = []

    # Algorithme simple de suggestion
    # Si temp < 5°C => Chaleur >= 7
    # Si 5°C <= temp <= 15°C => Chaleur entre 4 et 7
    # Si temp > 15°C => Chaleur <= 4
    vetements_chauds = [v for v in vetements if v['chaleur'] >= 7]
    vetements_moyens = [v for v in vetements if 4 <= v['chaleur'] < 7]
    vetements_froids = [v for v in vetements if v['chaleur'] <= 4]

    # On choisi la liste adaptée
    if temperature < 5:
        liste_adaptee = vetements_chauds
    elif 5 <= temperature <= 15:
        liste_adaptee = vetements_moyens
    else:
        liste_adaptee = vetements_froids

    hauts_dispo = [v for v in liste_adaptee if v['type'] == 'haut' and v['nb_portes'] < 3]
    bas_dispo = [v for v in liste_adaptee if v['type'] == 'bas' and v['nb_portes'] < 3]
    t_shirt_dispo = [v for v in vetements if v['type'] == 't-shirt' and v['nb_portes'] < 1]

    if not hauts_dispo: 
        hauts_dispo = [v for v in vetements if v['type'] == 'haut' and v['nb_portes'] < 3]
        if not hauts_dispo:
            hauts_dispo = [{'nom': 'sale', 'type': 'haut', 'chaleur': 0}]
    if not bas_dispo: 
        bas_dispo = [v for v in vetements if v['type'] == 'bas' and v['nb_portes'] < 3]
        if not bas_dispo:
            bas_dispo = [{'nom': 'sale', 'type': 'bas', 'chaleur': 0}]
    if not t_shirt_dispo:
        t_shirt_dispo = [{'nom': 'sale', 'type': 't-shirt', 'chaleur': 0}]

    if hauts_dispo:
        suggestion.append(random.choice(hauts_dispo))
    if bas_dispo:
        suggestion.append(random.choice(bas_dispo))
    if t_shirt_dispo:
        suggestion.append(random.choice(t_shirt_dispo))

    return suggestion

def prevision_semaine(vetements, date, temperature, description_meteo):
    tenues_semaine = []
    for i in range(len(date)):
        tenue = choisir_tenue(vetements, temperature[i])
        tenues_semaine.append(tenue)
        for v in tenue:
            if v['nom'] != "sale":
                porter_vetement(vetements, v['id'])
    for v in vetements:
        laver_vetement(vetements, v['id'])
    return tenues_semaine