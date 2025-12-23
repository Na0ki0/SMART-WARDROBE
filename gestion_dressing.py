import json
import config
from styliste_ia import demander_conseil_styliste

def charger_garde_robe():
    with open(config.FICHIER_DB, 'r', encoding='utf-8') as f:
        vetements = json.load(f)
        manquants_types = types_sans_propres(vetements)
        return vetements, manquants_types
    
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

def est_propre(v):
    # même logique que le styliste pour définir "propre"
    if v.get('type') == 't-shirt':
        limite = 1
    elif v.get('type') == 'haut' or v.get('type') == 'bas':
        limite = 3
    else:
        limite = 100
    return v.get('nb_portes', 0) < limite

def types_sans_propres(vetements, types_a_verifier=None):
    # si types_a_verifier est None -> on vérifie tous les types présents
    types = set(v.get('type', 'inconnu') for v in vetements)
    cible = types_a_verifier if types_a_verifier is not None else types
    return [t for t in cible if not any(est_propre(v) and v.get('type') == t for v in vetements)]

def choisir_tenue(vetements, temperature, description):
    reponse_ia = demander_conseil_styliste(vetements, temperature, description)
    if reponse_ia and "ids_choisis" in reponse_ia:
        tenue = []
        for v in vetements:
            if v['id'] in reponse_ia['ids_choisis']:
                tenue.append(v)
        for v in tenue:
            porter_vetement(vetements, v['id'])
        return tenue
    elif reponse_ia and "erreur" in reponse_ia:
        return {"erreur": f"{reponse_ia['erreur']}"}
    else:
        return {"erreur": "L'IA n'a pas trouvé d'inspiration..."}

def prevision_semaine(vetements, date, temperature, description_meteo):
    tenues_semaine = []
    for i in range(len(date)):
        tenue = choisir_tenue(vetements, temperature[i], description_meteo[i])
        tenues_semaine.append(tenue)
    return tenues_semaine