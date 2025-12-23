import json
import config
import copy
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
        return tenue
    elif reponse_ia and "erreur" in reponse_ia:
        return {"erreur": f"{reponse_ia['erreur']}"}
    else:
        return {"erreur": "L'IA n'a pas trouvé d'inspiration..."}

def prevision_semaine(vetements, date, temperature, description_meteo):
    """
    Génère 5 à 7 tenues en simulant l'usure des vêtements jour après jour.
    Ne sauvegarde rien.
    """
    # 1. On crée une copie pour la simulation (pour ne pas modifier la vraie liste tout de suite)
    vetements_simules = copy.deepcopy(vetements)
    
    tenues_semaine = []
    
    # 2. On boucle sur chaque jour
    for i in range(len(date)):
        # On demande une tenue en utilisant le stock "simulé"
        # L'IA verra que le jean porté le lundi (i=0) est "sale" pour le mardi (i=1)
        tenue = choisir_tenue(vetements_simules, temperature[i], description_meteo[i])
        
        tenues_semaine.append(tenue)
        
        # 3. Si une tenue valide est trouvée, on la marque comme portée DANS LA SIMULATION
        if isinstance(tenue, list):
            for v_choisi in tenue:
                # On retrouve le vêtement dans la liste simulée pour incrémenter son compteur
                for v_stock in vetements_simules:
                    if v_stock['id'] == v_choisi['id']:
                        v_stock['nb_portes'] += 1
                        break
                        
    return tenues_semaine