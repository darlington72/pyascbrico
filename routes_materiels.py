from flask import render_template, request, redirect, url_for, flash, send_from_directory, abort, Response
from app import app,db  # Importer l'instance de l'application
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from models import Materiel, Categorie, TypeEnergie, Emprunt, Statut_Emprunt, Etat
from sqlalchemy import or_
import csv
from io import StringIO

# Configuration pour les fichiers

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}  # Types de fichiers autorisés

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/materiels')
def get_materiels():
    materiels = Materiel.query.all()
    return render_template('materiels.html', materiels=materiels,categories=Categorie)

@app.route('/materiels/create', methods=['GET'])
def create_materiels_get():
    categories = [c.value for c in Categorie]
    typeenergies = [c.value for c in TypeEnergie]
    return render_template('ajouter_materiel.html', categories=categories,typeenergies=typeenergies)

@app.route('/materiels/create', methods=['POST'])
def create_materiel_post():
    nom_materiel = request.form['nom_materiel']
    numero_materiel = request.form.get('numero_materiel', type=int)
    prix_location_semaine = request.form.get('prix_location_semaine', type=float)
    localisation = request.form['localisation']
    accessoires_inclus = request.form['accessoires_inclus']
    poids = request.form.get('poids', type=float)
    dimensions = request.form['dimensions']
    categorie = request.form['categorie']
    type_energie = request.form['type_energie']
    reference = request.form['reference']
    num_serie = request.form['num_serie']
    marque = request.form['marque']
    description = request.form.get('description', '')
    niveau_danger = request.form['niveau_danger']
    securite = request.form['securite']
    checklist = request.form['checklist']
    
    # Gestion du fichier de document
    file_doc = request.files.get('manuel_user')
    if file_doc and allowed_file(file_doc.filename):
        filename_doc = secure_filename(file_doc.filename)
        file_doc.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_doc))
        document_path = os.path.join(app.config['UPLOAD_FOLDER'], filename_doc)
    else:
        document_path = ""  # Ou gérer selon vos besoins

    # Gestion du fichier de document
    vue_eclatee_doc = request.files.get('vue_eclatee')
    if vue_eclatee_doc and allowed_file(vue_eclatee_doc.filename):
        vue_eclateename_doc = secure_filename(vue_eclatee_doc.filename)
        vue_eclatee_doc.save(os.path.join(app.config['UPLOAD_FOLDER'], vue_eclateename_doc))
        vue_eclatee_path = os.path.join(app.config['UPLOAD_FOLDER'], vue_eclateename_doc)
    else:
        vue_eclatee_path = ""  # Ou gérer selon vos besoins

    date_vidange_str = request.form.get('date_vidange')
    date_entretien_str = request.form.get('date_entretien')
    nb_heure = request.form['nb_heure']

    date_achat_str = request.form.get('date_achat')
    lieu_achat = request.form['lieu_achat']
    prix_achat = request.form.get('prix_achat', type=float)
    # Gestion du fichier de facture
    file = request.files.get('facture')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        facture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    else:
        facture_path = ""  # Ou gérer selon vos besoins


    date_achat = datetime.strptime(date_achat_str, '%Y-%m-%d').date() if date_achat_str else None
    date_vidange = datetime.strptime(date_vidange_str, '%Y-%m-%d').date() if date_vidange_str else None
    date_entretien = datetime.strptime(date_entretien_str, '%Y-%m-%d').date() if date_entretien_str else None

    nouveau_materiel = Materiel(
        nom_materiel=nom_materiel,
        numero_materiel=numero_materiel,
        description=description,
        prix_location_semaine=prix_location_semaine,
        date_achat=date_achat,
        categorie=categorie,
        niveau_danger=niveau_danger,
        poids=poids,
        reference=reference,
        num_serie=num_serie,
        date_vidange=date_vidange,
        date_entretien=date_entretien,
        marque=marque,
        facture=facture_path,
        localisation=localisation,
        lieu_achat=lieu_achat,
        manuel_user=document_path,
        vue_eclatee=vue_eclatee_path,
        type_energie=type_energie,
        dimensions=dimensions,
        accessoires_inclus=accessoires_inclus,
        securite=securite,
        checklist=checklist,
        etat=Etat.ok,
        nb_heure=nb_heure,
        prix_achat=prix_achat
    )

    # ------------------------------------------------------------------------------------------
    # verifier toutes les erreurs possibles
    # ------------------------------------------------------------------------------------------

    # numéro materiel existant
    materiel_existant = Materiel.query.filter_by(numero_materiel=numero_materiel).first()
    if materiel_existant:
        flash('Ce numéro de matériel existe déjà dans la base de données.', 'danger')
        return redirect(url_for('get_materiels'))

    # ------------------------------------------------------------------------------------------
    # envoyer
    # ------------------------------------------------------------------------------------------

    db.session.add(nouveau_materiel)
    db.session.commit()

    flash('Nouveau matériel ajouté avec succès!', 'success')

    return redirect(url_for('get_materiels'))

@app.route('/materiels/<int:numero_materiel>')
def get_materiel(numero_materiel):
    checklist=None
    accessoires_inclus=None

    materiel = Materiel.query.filter_by(numero_materiel=numero_materiel).first()
    if not materiel:
        flash('Le matériel demandé n\'existe pas.', 'danger')
        return redirect(url_for('get_materiels'))

    emprunt_en_cours    = Emprunt.query.filter_by(id_materiel=materiel.id_materiel, statut=Statut_Emprunt.en_cours).first()
    emprunt_reserve     = Emprunt.query.filter_by(id_materiel=materiel.id_materiel, statut=Statut_Emprunt.reserve).all()
    emprunt_historique  = Emprunt.query.filter(
        Emprunt.id_materiel == materiel.id_materiel,
        or_(
            Emprunt.statut == Statut_Emprunt.retourne,
            Emprunt.statut == Statut_Emprunt.annule
        )
    ).all()

    # Récupérer et traiter la checklist
    if materiel.checklist:
        checklist = [item.strip() for item in materiel.checklist.split(',') if item.strip()]        

    # Récupérer et traiter les accessoires
    if materiel.accessoires_inclus and materiel.accessoires_inclus != "None":
        accessoires_inclus = [item.strip() for item in materiel.accessoires_inclus.split(',') if item.strip()]    


    return render_template('materiel.html', materiel=materiel,checklist=checklist,emprunt_en_cours=emprunt_en_cours,
    emprunt_reserve=emprunt_reserve,emprunt_historique=emprunt_historique,accessoires_inclus=accessoires_inclus)

@app.route('/materiels/delete/<int:numero_materiel>', methods=['POST'])
def delete_materiel(numero_materiel):

    materiel = Materiel.query.filter_by(numero_materiel=numero_materiel).first()
    if not materiel:
        flash('Le matériel demandé n\'existe pas.', 'danger')
        return redirect(url_for('get_materiels'))

    db.session.delete(materiel)
    db.session.commit()
    return redirect(url_for('get_materiels'))

@app.route('/materiels/edit/<int:numero_materiel>', methods=['GET'])
def edit_materiel_get(numero_materiel):

    materiel = Materiel.query.filter_by(numero_materiel=numero_materiel).first()

    if not materiel:
        flash('Le matériel n\'existe pas.', 'danger')
        return redirect(url_for('get_materiels'))

    categories = [c.value for c in Categorie]
    typeenergies = [c.value for c in TypeEnergie]
    etats = [c.value for c in Etat]
    
    return render_template('modifier_materiel.html', materiel=materiel, categories=categories, typeenergies=typeenergies,etats=etats)

@app.route('/materiels/edit/<int:numero_materiel>', methods=['POST'])
def edit_materiel_post(numero_materiel):

    materiel = Materiel.query.filter_by(numero_materiel=numero_materiel).first()

    if not materiel:
        flash('Le matériel n\'existe pas.', 'danger')
        return redirect(url_for('get_materiels'))

    # Récupérer les nouvelles données depuis le formulaire
    materiel.etat = request.form['etat']
    materiel.nom_materiel = request.form['nom_materiel']
    materiel.numero_materiel = request.form.get('numero_materiel', type=int)
    materiel.prix_location_semaine = request.form.get('prix_location_semaine', type=float)
    materiel.localisation = request.form['localisation']
    materiel.accessoires_inclus = request.form['accessoires_inclus']
    materiel.poids = request.form.get('poids', type=float)
    materiel.dimensions = request.form['dimensions']
    materiel.categorie = request.form['categorie']
    materiel.type_energie = request.form['type_energie']
    materiel.reference = request.form['reference']
    materiel.num_serie = request.form['num_serie']
    materiel.marque = request.form['marque']
    materiel.description = request.form.get('description', '')
    materiel.niveau_danger = request.form['niveau_danger']
    materiel.securite = request.form['securite']
    materiel.checklist = request.form['checklist']

    # Gestion du fichier de document (si un nouveau fichier est téléchargé)
    file_doc = request.files.get('manuel_user')
    if file_doc and allowed_file(file_doc.filename):
        filename_doc = secure_filename(file_doc.filename)
        file_doc.save(os.path.join(app.config['UPLOAD_FOLDER'], filename_doc))
        materiel.manuel_user = os.path.join(app.config['UPLOAD_FOLDER'], filename_doc)
    
    # Gestion du fichier de vue éclatée (si un nouveau fichier est téléchargé)
    vue_eclatee_doc = request.files.get('vue_eclatee')
    if vue_eclatee_doc and allowed_file(vue_eclatee_doc.filename):
        vue_eclateename_doc = secure_filename(vue_eclatee_doc.filename)
        vue_eclatee_doc.save(os.path.join(app.config['UPLOAD_FOLDER'], vue_eclateename_doc))
        materiel.vue_eclatee = os.path.join(app.config['UPLOAD_FOLDER'], vue_eclateename_doc)
    
    date_vidange_str = request.form.get('date_vidange')
    date_entretien_str = request.form.get('date_entretien')
    materiel.nb_heure = request.form['nb_heure']

    date_achat_str = request.form.get('date_achat')
    materiel.lieu_achat = request.form['lieu_achat']
    materiel.prix_achat = request.form.get('prix_achat', type=float)
    # Gestion du fichier de facture (si un nouveau fichier est téléchargé)
    file = request.files.get('facture')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        materiel.facture = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    materiel.date_achat = datetime.strptime(date_achat_str, '%Y-%m-%d').date() if date_achat_str else None
    materiel.date_vidange = datetime.strptime(date_vidange_str, '%Y-%m-%d').date() if date_vidange_str else None
    materiel.date_entretien = datetime.strptime(date_entretien_str, '%Y-%m-%d').date() if date_entretien_str else None

    # ------------------------------------------------------------------------------------------
    # verifier toutes les erreurs possibles
    # ------------------------------------------------------------------------------------------


    # ------------------------------------------------------------------------------------------
    # envoyer
    # ------------------------------------------------------------------------------------------

    db.session.commit()

    flash('Matériel modifié avec succès!', 'success')
    return redirect(url_for('get_materiel', numero_materiel=materiel.numero_materiel))


@app.route('/telecharger_facture/<int:numero_materiel>')
def telecharger_facture(numero_materiel):
    materiel = Materiel.query.filter_by(numero_materiel=numero_materiel).first()

    if not materiel or not materiel.facture:
        flash('Aucune facture disponible pour ce matériel.', 'danger')
        return redirect(url_for('get_materiels'))

    # Vérifier si le fichier existe
    facture_path = materiel.facture  # Le chemin vers le fichier de la facture
    if not os.path.exists(facture_path):
        abort(404)  # Si le fichier n'existe pas, retourner une erreur 404

    # Envoyer le fichier
    filename = os.path.basename(facture_path)  # Extraire le nom du fichier
    return send_from_directory(os.path.dirname(facture_path), filename, as_attachment=True)

@app.route('/telecharger_mu/<int:numero_materiel>')
def telecharger_mu(numero_materiel):
    materiel = Materiel.query.filter_by(numero_materiel=numero_materiel).first()

    if not materiel or not materiel.manuel_user:
        flash('Aucune facture disponible pour ce matériel.', 'danger')
        return redirect(url_for('get_materiels'))

    # Vérifier si le fichier existe
    file_path = materiel.manuel_user  # Le chemin vers le fichier de la facture
    if not os.path.exists(file_path):
        abort(404)  # Si le fichier n'existe pas, retourner une erreur 404

    # Envoyer le fichier
    filename = os.path.basename(file_path)  # Extraire le nom du fichier
    return send_from_directory(os.path.dirname(file_path), filename, as_attachment=True)

@app.route('/telecharger_vue_eclatee/<int:numero_materiel>')
def telecharger_vue_eclatee(numero_materiel):
    materiel = Materiel.query.filter_by(numero_materiel=numero_materiel).first()

    if not materiel or not materiel.vue_eclatee:
        flash('Aucune facture disponible pour ce matériel.', 'danger')
        return redirect(url_for('get_materiels'))

    # Vérifier si le fichier existe
    file_path = materiel.vue_eclatee  # Le chemin vers le fichier de la facture
    if not os.path.exists(file_path):
        abort(404)  # Si le fichier n'existe pas, retourner une erreur 404

    # Envoyer le fichier
    filename = os.path.basename(file_path)  # Extraire le nom du fichier
    return send_from_directory(os.path.dirname(file_path), filename, as_attachment=True)


@app.route('/materiels/export_csv')
def export_materiels_csv():
    # Récupérer tous les matériels
    materiels = Materiel.query.all()

    # Créer un objet StringIO pour écrire dans le flux mémoire
    si = StringIO()
    writer = csv.writer(si)

    # Écrire l'en-tête du CSV
    writer.writerow(['id_materiel','numero_materiel', 'nom_materiel', 'description','prix_location_semaine','etat','date_achat','categorie','poids','reference','num_serie','date_vidange','date_entretien','nb_heure','marque','prix_achat','lieu_achat','localisation','type_energie','dimensions','accessoires_inclus','niveau_danger','securite','checklist'])

    # Écrire les données des matériels
    for materiel in materiels:
        writer.writerow([materiel.id_materiel,materiel.numero_materiel, materiel.nom_materiel, materiel.description,materiel.prix_location_semaine,materiel.etat.value,materiel.date_achat,materiel.categorie.value,materiel.poids,materiel.reference,materiel.num_serie,materiel.date_vidange,materiel.date_entretien,materiel.nb_heure,materiel.marque,materiel.prix_achat,materiel.prix_achat,materiel.lieu_achat,materiel.localisation,materiel.type_energie.value,materiel.dimensions,materiel.accessoires_inclus,materiel.niveau_danger,materiel.securite,materiel.checklist ])

    # Revenir au début du flux mémoire pour le lire
    si.seek(0)

    # Créer une réponse avec le fichier CSV
    response = Response(si.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=materiels.csv'

    return response
