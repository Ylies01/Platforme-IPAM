# app.py
# Application web Flask : definit les routes (les pages) et fait le lien
# entre l'interface, la logique reseau (reseau.py) et la base (database.py).

from flask import Flask, render_template, request, redirect, url_for, flash
from database import initialiser_base
from reseau import (
    ajouter_client, supprimer_client, lister_clients,
    chercher_client, lister_plages, generer_configuration, clients_du_site
)

app = Flask(__name__)
app.secret_key = "cle_secrete_groupe3"  # necessaire pour les messages flash

initialiser_base()  # cree la base et les sous-reseaux au demarrage si besoin

ROUTEURS_PE = ["PE1", "PE2", "PE3"]  # les 3 sites de production (routeurs Provider Edge)


@app.route("/")
def accueil():
    # Page d'accueil : liste de tous les clients.
    clients = lister_clients()
    return render_template("index.html", clients=clients)


@app.route("/ajouter", methods=["GET", "POST"])
def ajouter():
    # GET : affiche le formulaire. POST : cree le client et montre la config.
    if request.method == "POST":
        nom = request.form.get("nom", "").strip()
        routeur_pe = request.form.get("routeur_pe", "PE1")

        if not nom:
            flash("Le nom du client est obligatoire.", "erreur")
            return redirect(url_for("ajouter"))

        client, configuration = ajouter_client(nom, routeur_pe)
        if client is None:
            # configuration contient ici le message d'erreur
            flash(configuration, "erreur")
            return redirect(url_for("ajouter"))

        flash("Client " + nom + " ajoute avec succes !", "succes")
        return render_template("config.html", client=client, configuration=configuration)

    return render_template("ajouter.html", routeurs=ROUTEURS_PE)


@app.route("/supprimer/<int:numero_client>", methods=["POST"])
def supprimer(numero_client):
    # Supprime un client puis revient a la liste.
    succes, message = supprimer_client(numero_client)
    if succes:
        flash(message, "succes")
    else:
        flash(message, "erreur")
    return redirect(url_for("accueil"))


@app.route("/client/<int:numero_client>")
def voir_client(numero_client):
    # Affiche le detail d'un client et regenere sa configuration.
    client = chercher_client(numero_client)
    if not client:
        flash("Client introuvable.", "erreur")
        return redirect(url_for("accueil"))
    configuration = generer_configuration(client)
    return render_template("config.html", client=client, configuration=configuration)


@app.route("/plages")
def plages():
    # Visualisation de l'etat des 16 sous-reseaux /28.
    toutes_les_plages = lister_plages()
    return render_template("plages.html", plages=toutes_les_plages)


@app.route("/site/<routeur_pe>")
def site(routeur_pe):
    # Consultation des clients d'un site (routeur PE) donne.
    if routeur_pe not in ROUTEURS_PE:
        flash("Routeur PE invalide.", "erreur")
        return redirect(url_for("accueil"))
    clients = clients_du_site(routeur_pe)
    return render_template("site.html", clients=clients, routeur_pe=routeur_pe, routeurs=ROUTEURS_PE)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
