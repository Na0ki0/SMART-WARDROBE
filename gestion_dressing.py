import json
import os
import config
import copy
from styliste_ia import demander_conseil_styliste

def get_path_dressing(username):
    return os.path.join("data", username, "garde_robe.json")

def charger_garde_robe(username):
    path = get_path_dressing(username)
    # Si le fichier n'existe pas encore (nouveau compte), on renvoie des listes vides
    if not os.path.exists(path):
        return [], []
        
    with open(path, 'r', encoding='utf-8') as f:
        try:
            vetements = json.load(f)
            manquants_types = types_sans_propres(vetements)
            return vetements, manquants_types
        except:
            return [], []

def porter_vetement(username, id_vetement):
    # 1. On charge la garde-robe de l'utilisateur spécifique
    vetements, _ = charger_garde_robe(username)
    trouve = False
    
    for v in vetements:
        if v['id'] == id_vetement:
            nb_actuel = v.get('nb_portes', 0)
            v['nb_portes'] = nb_actuel + 1
            trouve = True
            break

    # 2. On sauvegarde DANS LE FICHIER DE L'UTILISATEUR
    if trouve:
        path = get_path_dressing(username)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(vetements, f, indent=4, ensure_ascii=False)

def laver_vetement(username, id_vetement):
    vetements, _ = charger_garde_robe(username)
    trouve = False
    
    for v in vetements:
        if v['id'] == id_vetement:
            v['nb_portes'] = 0
            trouve = True
            break

    if trouve:
        path = get_path_dressing(username)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(vetements, f, indent=4, ensure_ascii=False)

def est_propre(v):
    if v.get('type') == 't-shirt': limite = 1
    elif v.get('type') in ['bas', 'haut']: limite = 3
    else: limite = 100
    return v.get('nb_portes', 0) < limite

def types_sans_propres(vetements, types_a_verifier=None):
    types = set(v.get('type', 'inconnu') for v in vetements)
    cible = types_a_verifier if types_a_verifier is not None else types
    return [t for t in cible if not any(est_propre(v) and v.get('type') == t for v in vetements)]

def choisir_tenue(vetements, temperature, description):
    # Cette fonction ne change pas (elle travaille en mémoire)
    reponse_ia = demander_conseil_styliste(vetements, temperature, description)
    if reponse_ia and "ids_choisis" in reponse_ia:
        tenue = []
        for v in vetements:
            if v['id'] in reponse_ia['ids_choisis']:
                tenue.append(v)
        return tenue
    elif reponse_ia and "erreur" in reponse_ia:
        return {"erreur": f"{reponse_ia['erreur']}"}
    else:
        return {"erreur": "L'IA n'a pas trouvé d'inspiration..."}

def prevision_semaine(vetements, date, temperature, description_meteo):
    # Cette fonction ne change pas (elle simule en mémoire)
    vetements_simules = copy.deepcopy(vetements)
    tenues_semaine = []
    
    for i in range(len(date)):
        tenue = choisir_tenue(vetements_simules, temperature[i], description_meteo[i])
        tenues_semaine.append(tenue)
        
        if isinstance(tenue, list):
            for v_choisi in tenue:
                for v_stock in vetements_simules:
                    if v_stock['id'] == v_choisi['id']:
                        v_stock['nb_portes'] += 1
                        break
    return tenues_semaine