from flask import render_template, request, redirect, url_for, flash
from app import app,db
from models import Materiel,Etat, Adherent, Reparation, Statut_Reparation
from datetime import datetime

@app.route('/pannes')
def get_pannes():
    materiels_en_panne = Materiel.query.filter_by(etat=Etat.en_panne).all()

    reparations_en_cours = Reparation.query.filter_by(statut=Statut_Reparation.en_cours).all()
    reparations_termine  = Reparation.query.filter_by(statut=Statut_Reparation.termine).all()

    return render_template('pannes.html', materiels_en_panne=materiels_en_panne,reparations_en_cours=reparations_en_cours,reparations_termine=reparations_termine)


@app.route('/pannes/nouvelle', methods=['GET', 'POST'])
def nouvelle_panne():
    materiels = Materiel.query.filter_by(etat=Etat.ok).all()

    if request.method == 'POST':
        id_materiel = request.form['materiel']
        remarques = request.form['remarques']
        date_creation = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')

        nouvelle_rep = Reparation(
            id_materiel=id_materiel,
            remarques=remarques,
            statut=Statut_Reparation.en_cours,
            date_creation=date_creation
        )

        materiel = Materiel.query.filter_by(id_materiel=id_materiel).first()
        materiel.etat = Etat.en_panne

        db.session.add(nouvelle_rep)
        db.session.commit()
        flash("Panne déclarée avec succès.", "success")
        return redirect(url_for('get_pannes'))

    return render_template('nouvelle_panne.html', materiels=materiels)


@app.route('/pannes/traiter/<int:id>', methods=['GET', 'POST'])
def traiter_panne(id):
    reparation = Reparation.query.get_or_404(id)
    adherents = Adherent.query.all()

    if request.method == 'POST':
        reparation.remarques = request.form['remarques']
        reparation.id_adherent = request.form['adherent']
        reparation.statut = Statut_Reparation.termine
        reparation.montant = request.form.get('montant', 0)
        reparation.date_cloture = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')

        materiel = Materiel.query.filter_by(id_materiel=reparation.id_materiel).first()
        materiel.etat = Etat.ok

        db.session.commit()
        flash("Réparation enregistrée.", "success")
        return redirect(url_for('get_pannes'))

    return render_template('traiter_panne.html', reparation=reparation, adherents=adherents)
