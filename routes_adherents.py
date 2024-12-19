from flask import render_template, request, redirect, url_for, flash
from app import app,db
from models import Adherent

@app.route('/adherents')
def get_adherents():
    adherents = Adherent.query.all()  # Récupère tout de la base de données
    return render_template('adherents.html', adherents=adherents)

@app.route('/adherents/add', methods=['GET', 'POST'])
def ajouter_adherent():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        statut = request.form['statut']
        telephone = request.form['telephone']

        depuis_str = request.form.get('date_entretien')
        depuis = datetime.strptime(depuis_str, '%Y-%m-%d').date() if depuis_str else None

        # Créez un nouvel objet Adherent
        nouvel_adherent = Adherent(
            nom=nom,
            prenom=prenom,
            email=email,
            statut=statut,
            telephone=telephone,
            depuis=depuis
        )

        try:
            db.session.add(nouvel_adherent)
            db.session.commit()
            flash('Adhérent ajouté avec succès!', 'success')
            return redirect(url_for('get_adherents'))
        except Exception as e:
            db.session.rollback()
            flash('Erreur lors de l\'ajout de l\'adhérent: ' + str(e), 'danger')

    return render_template('ajouter_adherent.html')




