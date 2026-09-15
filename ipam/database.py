# database.py
# Gestion de la base de donnees SQLite (centralisee).
# Deux tables : "clients" et "plages" (les sous-reseaux /28).

import sqlite3

CHEMIN_BASE = "ipam.db"  # fichier unique = base centralisee (source de verite)


def ouvrir_connexion():
    # Ouvre une connexion a la base et renvoie cette connexion.
    connexion = sqlite3.connect(CHEMIN_BASE)
    # Permet d'acceder aux colonnes par leur nom : ligne["nom"].
    connexion.row_factory = sqlite3.Row
    return connexion


def initialiser_base():
    # Cree les deux tables si elles n'existent pas et remplit les plages.
    connexion = ouvrir_connexion()
    curseur = connexion.cursor()

    # --- Table des clients ---
    curseur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            vlan INTEGER UNIQUE NOT NULL,
            vrf TEXT NOT NULL,
            sous_reseau TEXT NOT NULL,
            passerelle TEXT NOT NULL,
            routeur_pe TEXT NOT NULL,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- Table des plages (les sous-reseaux /28 et leur etat) ---
    curseur.execute("""
        CREATE TABLE IF NOT EXISTS plages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reseau TEXT NOT NULL,
            masque INTEGER NOT NULL,
            etat TEXT DEFAULT 'libre'  -- libre, reservee, allouee
        )
    """)

    # On remplit les plages une seule fois (si la table est vide).
    curseur.execute("SELECT COUNT(*) FROM plages")
    nombre = curseur.fetchone()[0]

    if nombre == 0:
        # Notre /24 (164.166.3.0/24) se decoupe en 16 sous-reseaux /28.
        # Un /28 = 16 adresses, donc 256 / 16 = 16 blocs (.0, .16, .32 ...).
        for i in range(16):
            dernier_octet = i * 16
            reseau = "164.166.3." + str(dernier_octet)
            curseur.execute(
                "INSERT INTO plages (reseau, masque, etat) VALUES (?, 28, 'libre')",
                (reseau,)
            )

    connexion.commit()
    connexion.close()
    print("Base de donnees initialisee.")


if __name__ == "__main__":
    initialiser_base()
