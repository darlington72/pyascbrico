from flask import render_template, request, redirect, url_for, flash
from app import app,db
from models import Emprunt,Adherent,Materiel,Statut_Emprunt,TypeEnergie,Categorie,Etat
from datetime import datetime

@app.route('/emprunts')
def get_emprunts():
    emprunts = Emprunt.query.all()
    return render_template('emprunts.html', emprunts=emprunts)

@app.route('/emprunts/create', methods=['GET', 'POST'])
def create_emprunt():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        date_debut = request.form['date_debut']
        duree = request.form['duree']
        id_materiel = request.form['materiel']
        id_adherent = request.form['adherent']
        remarques = request.form.get('remarques', '')

        date_loc_str = request.form.get('date_debut')
        date_loc = datetime.strptime(date_loc_str, '%Y-%m-%d').date() if date_loc_str else None

        # Créer une nouvelle instance d'Emprunt
        nouvel_emprunt = Emprunt(
            date_debut=date_loc,
            duree=duree,
            statut=Statut_Emprunt.en_cours,
            id_materiel=id_materiel,
            id_adherent=id_adherent,
            remarques=remarques,
        )

        # Ajouter à la base de données
        db.session.add(nouvel_emprunt)
        db.session.commit()

        flash('Emprunt créé avec succès!', 'success')
        return redirect(url_for('get_emprunts'))  # Redirige vers la liste des emprunts

    # Récupérer les matériels et adhérents pour le formulaire
    materiels = Materiel.query.all()
    adherents = Adherent.query.all()
    return render_template('nouvel_emprunt.html', materiels=materiels, adherents=adherents)

