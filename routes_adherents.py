from flask import render_template, request, redirect, url_for, flash
from app import app,db
from models import Adherent
from datetime import datetime
import csv
import os
from werkzeug.utils import secure_filename

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

        depuis_str = request.form.get('depuis')
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

ALLOWED_EXTENSIONS = {'csv'}  # Types de fichiers autorisés

# Vérification de l'extension du fichier
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route pour traiter le fichier CSV uploadé
@app.route('/import_csv', methods=['POST'])
def import_csv():
    if 'csv_file' not in request.files:
        flash('Aucun fichier sélectionné', 'danger')
        return redirect(request.url)

    file = request.files['csv_file']

    if file.filename == '':
        flash('Aucun fichier sélectionné', 'danger')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)  # Sécuriser le nom du fichier
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)  # Sauvegarder le fichier sur le serveur

        try:
            # Appel de la fonction pour traiter le fichier CSV et importer les adhérents
            nb_adherent_added, nb_adherent_modified = load_adherents_from_csv(filepath)
            flash(f'{nb_adherent_added} adhérents ont été importés avec succès ! {nb_adherent_modified} adhérents ont été modifiés.', 'success')
        except Exception as e:
            flash(f'Erreur lors de l\'importation : {e}', 'danger')

        return redirect(url_for('get_adherents'))

    flash('Le fichier téléchargé n\'est pas un fichier CSV valide.', 'danger')
    return redirect(request.url)

# Fonction pour charger les adhérents depuis un fichier CSV
def load_adherents_from_csv(csv_file_path):
    with open(csv_file_path, 'r', encoding='ISO-8859-1') as file:
        reader = csv.DictReader(file, delimiter=';')

        adherents_to_insert = []

        nb_adherent_modified = 0

        for row in reader:
            # Conversion de la date 'Depuis' en objet datetime
            depuis = datetime.strptime(row['Depuis'], "%d/%m/%Y") if row['Depuis'] else None

            # Vérifier si un adhérent avec le même numéro ASC existe déjà dans la base de données
            existing_adherent = Adherent.query.filter_by(numero_asc=row['n° ASC']).first()

            # l'adherent exsite on le met a jour
            if existing_adherent:
                nb_adherent_modified = nb_adherent_modified + 1
                existing_adherent.valide_asc = True if row['Etat d\'inscription à l\'ASC'] == 'Valide' else False
                existing_adherent.email      = row['Mel']
                existing_adherent.nom        = row['Nom']
                existing_adherent.statut     = row['Statut']
                existing_adherent.telephone  = row['Tél. bureau']
                existing_adherent.depuis     = depuis
                db.session.commit()
                
                continue  # Ignorez l'adhérent et passez à l'élément suivant

            # Si l'adhérent n'existe pas, créez un nouveau modèle Adherent
            adherent = Adherent(
                numero_asc=int(row['n° ASC']),
                nom=row['Nom'],
                prenom=row['Prénom'],
                valide_asc=True if row['Etat d\'inscription à l\'ASC'] == 'Valide' else False,
                email=row['Mel'],
                statut=row['Statut'],
                telephone=row['Tél. bureau'],
                depuis=depuis,
                badge=None  
            )

            # Ajoutez l'adhérent à la liste pour insertion en masse
            adherents_to_insert.append(adherent)

        # Insertion en masse dans la base de données
        db.session.bulk_save_objects(adherents_to_insert)
        db.session.commit()

    return len(adherents_to_insert), nb_adherent_modified
