# reseau.py
# Toute la logique "reseau" du projet IPAM :
#  - trouver et attribuer un sous-reseau /28 libre
#  - calculer l'adresse de passerelle
#  - generer la configuration Cisco
#  - ajouter / supprimer un client

from database import ouvrir_connexion

NUMERO_AS = 65556  # numero d'AS de la societe (sert pour le Route Distinguisher)


def calculer_passerelle(reseau):
    # Premiere adresse utilisable du sous-reseau = adresse reseau + 1
    # Exemple : 164.166.3.0  ->  164.166.3.1  (le .0 est l'adresse reseau)
    parties = reseau.split(".")
    dernier = int(parties[3]) + 1
    return parties[0] + "." + parties[1] + "." + parties[2] + "." + str(dernier)


def generer_configuration(client):
    # Construit le texte de configuration Cisco pour un client.
    configuration = f"""! ============================================
! Configuration client : {client['nom']}
! Genere automatiquement par IPAM - Groupe 3
! ============================================

! --- VRF ---
ip vrf {client['vrf']}
 rd {NUMERO_AS}:{client['vlan']}
 route-target export {NUMERO_AS}:{client['vlan']}
 route-target import {NUMERO_AS}:{client['vlan']}
!

! --- Sous-interface ---
interface GigabitEthernet0/0.{client['vlan']}
 encapsulation dot1Q {client['vlan']}
 ip vrf forwarding {client['vrf']}
 ip address {client['passerelle']} 255.255.255.240
 description CLIENT_{client['nom'].upper()}
!"""
    return configuration


def ajouter_client(nom, routeur_pe):
    # Ajoute un client et lui attribue automatiquement un sous-reseau /28.
    connexion = ouvrir_connexion()
    curseur = connexion.cursor()

    # 1) On cherche le premier sous-reseau encore libre
    curseur.execute("SELECT id, reseau FROM plages WHERE etat = 'libre' ORDER BY id")
    plage = curseur.fetchone()
    if plage is None:
        connexion.close()
        return None, "Aucun sous-reseau disponible."

    plage_id = plage["id"]
    reseau = plage["reseau"]

    # 2) On reserve ce sous-reseau (etat temporaire) puis on calcule la passerelle
    curseur.execute("UPDATE plages SET etat = 'reservee' WHERE id = ?", (plage_id,))
    passerelle = calculer_passerelle(reseau)

    # 3) On enregistre le client.
    #    Le VLAN doit etre egal au numero du client (= son id dans la base).
    #    On insere d'abord avec un VLAN provisoire (0), puis on le corrige.
    curseur.execute(
        "INSERT INTO clients (nom, vrf, sous_reseau, passerelle, routeur_pe, vlan) VALUES (?, ?, ?, ?, ?, ?)",
        (nom, nom, reseau, passerelle, routeur_pe, 0)
    )
    numero_client = curseur.lastrowid
    curseur.execute("UPDATE clients SET vlan = ? WHERE id = ?", (numero_client, numero_client))

    # 4) Le sous-reseau passe en "allouee"
    curseur.execute("UPDATE plages SET etat = 'allouee' WHERE id = ?", (plage_id,))
    connexion.commit()

    # On relit le client complet pour generer sa configuration
    curseur.execute("SELECT * FROM clients WHERE id = ?", (numero_client,))
    client = dict(curseur.fetchone())
    connexion.close()

    configuration = generer_configuration(client)
    return client, configuration


def supprimer_client(numero_client):
    # Supprime un client et libere son sous-reseau.
    connexion = ouvrir_connexion()
    curseur = connexion.cursor()

    # On recupere d'abord son sous-reseau (pour pouvoir le liberer ensuite)
    curseur.execute("SELECT sous_reseau FROM clients WHERE id = ?", (numero_client,))
    client = curseur.fetchone()
    if client is None:
        connexion.close()
        return False, "Client introuvable."

    sous_reseau = client["sous_reseau"]
    curseur.execute("DELETE FROM clients WHERE id = ?", (numero_client,))
    # Le sous-reseau redevient libre
    curseur.execute("UPDATE plages SET etat = 'libre' WHERE reseau = ?", (sous_reseau,))
    connexion.commit()
    connexion.close()
    return True, "Client supprime avec succes."


def lister_clients():
    # Renvoie la liste de tous les clients.
    connexion = ouvrir_connexion()
    curseur = connexion.cursor()
    curseur.execute("SELECT * FROM clients ORDER BY id")
    lignes = curseur.fetchall()
    connexion.close()

    clients = []
    for ligne in lignes:
        clients.append(dict(ligne))
    return clients


def clients_du_site(routeur_pe):
    # Renvoie les clients rattaches a un site (routeur PE) donne.
    connexion = ouvrir_connexion()
    curseur = connexion.cursor()
    curseur.execute("SELECT * FROM clients WHERE routeur_pe = ? ORDER BY id", (routeur_pe,))
    lignes = curseur.fetchall()
    connexion.close()

    clients = []
    for ligne in lignes:
        clients.append(dict(ligne))
    return clients


def chercher_client(numero_client):
    # Renvoie un seul client, ou None s'il n'existe pas.
    connexion = ouvrir_connexion()
    curseur = connexion.cursor()
    curseur.execute("SELECT * FROM clients WHERE id = ?", (numero_client,))
    ligne = curseur.fetchone()
    connexion.close()

    if ligne is None:
        return None
    return dict(ligne)


def lister_plages():
    # Renvoie l'etat de tous les sous-reseaux.
    connexion = ouvrir_connexion()
    curseur = connexion.cursor()
    curseur.execute("SELECT * FROM plages ORDER BY id")
    lignes = curseur.fetchall()
    connexion.close()

    plages = []
    for ligne in lignes:
        plages.append(dict(ligne))
    return plages
