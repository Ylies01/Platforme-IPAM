# IPAM - Groupe 3 | IUT Villetaneuse 2025-2026

Plateforme de gestion d'adresses IP (IPAM) pour la SAE 2.03.
Plage attribuée : **164.166.3.0/24** — sous-réseaux en /28.

---

## Installation

### Prérequis
- Python 3.8+
- pip

### 1. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 2. Lancer l'application

```bash
python app.py
```

L'application est accessible sur : **http://localhost:5000**

La base de données `ipam.db` est créée automatiquement au premier lancement.

---

## Fonctionnalités

| Page | URL | Description |
|------|-----|-------------|
| Liste clients | `/` | Affiche tous les clients avec leurs infos réseau |
| Nouveau client | `/ajouter` | Formulaire d'ajout + génération config automatique |
| Config client | `/client/<id>` | Détails + configuration Cisco IOS générée |
| Plages IP | `/plages` | État de tous les /28 (libre / allouée) |

---

## Architecture

```
ipam/
├── app.py          # Application Flask (routes)
├── database.py     # Init SQLite + connexion
├── reseau.py       # Logique métier (attribution IP, génération config)
├── requirements.txt
├── ipam.db         # Base SQLite (créée auto)
└── templates/
    ├── base.html   # Layout commun
    ├── index.html  # Liste clients
    ├── ajouter.html # Formulaire nouveau client
    ├── config.html  # Affichage config générée
    └── plages.html  # Visualisation plages IP
```

---

## Choix techniques

- **Python / Flask** : framework web léger, adapté au niveau BUT1
- **SQLite** : base SQL centralisée, fichier unique, aucune installation serveur
- **Jinja2** : moteur de templates intégré à Flask
- **HTML/CSS pur** : pas de dépendance externe (pas de Bootstrap)

---

## Plan d'adressage (Groupe 3)

| Bloc | Réseau | Plage hôtes | Broadcast |
|------|--------|-------------|-----------|
| 1 | 164.166.3.0/28 | .1 → .14 | .15 |
| 2 | 164.166.3.16/28 | .17 → .30 | .31 |
| ... | ... | ... | ... |
| 16 | 164.166.3.240/28 | .241 → .254 | .255 |

---

## Paramètres réseau

- AS société : **65556**
- Route Distinguisher : `65556:<numéro_client>`
- VLAN = numéro client (incrémental)
- Nom VRF = nom du client

---


- Ajout de plusieurs clients successifs → vérification attribution /28 séquentielle
- Suppression client → vérification libération du sous-réseau
- Ajout après suppression → vérification réattribution correcte
- Vérification génération config Cisco (VRF, sous-interface, adressage)
