from flask import render_template, request, redirect, url_for, flash
from app import app,db  # Importer l'instance de l'application
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from models import Materiel, Categorie, TypeEnergie, Emprunt, Statut_Emprunt
from sqlalchemy import or_

# Configuration pour les fichiers

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}  # Types de fichiers autorisés

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/materiels')
def get_materiels():
    materiels = Materiel.query.all()  # Récupère tous les matériels de la base de données
    return render_template('materiels.html', materiels=materiels,categories=Categorie)
    # return jsonify([materiel.as_dict() for materiel in materiels])

@app.route('/materiels/create', methods=['GET'])
def create_materiels_get():
    categories = [c.value for c in Categorie]
    typeenergies = [c.value for c in TypeEnergie]
    return render_template('ajouter_materiel.html', categories=categories,typeenergies=typeenergies)

@app.route('/materiels/create', methods=['POST'])
def create_materiel_post():
    nom_materiel = request.form['nom_materiel']
    numero_materiel = request.form['numero_materiel']
    description = request.form.get('description', '')
    prix_location_semaine = request.form['prix_location_semaine']
    quantite_disponible = request.form['quantite_disponible']
    categorie = request.form['categorie'].lower()
    niveau_danger = request.form['niveau_danger']
    poids = request.form.get('poids', type=float)
    reference = request.form['reference']
    num_serie = request.form['num_serie']
    marque = request.form['marque']
    localisation = request.form['localisation']
    lieu_achat = request.form['lieu_achat']
    type_energie = request.form['type_energie'].lower()
    dimensions = request.form['dimensions']
    accessoires_inclus = request.form['accessoires_inclus']
    securite = request.form['securite']
    checklist = request.form['checklist']

    # Gestion du fichier de facture
    file = request.files.get('facture')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        facture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    else:
        facture_path = ""  # Ou gérer selon vos besoins

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

    # Récupérer et convertir les dates
    date_achat_str = request.form.get('date_achat')
    date_vidange_str = request.form.get('date_vidange')
    date_entretien_str = request.form.get('date_entretien')

    date_achat = datetime.strptime(date_achat_str, '%Y-%m-%d').date() if date_achat_str else None
    date_vidange = datetime.strptime(date_vidange_str, '%Y-%m-%d').date() if date_vidange_str else None
    date_entretien = datetime.strptime(date_entretien_str, '%Y-%m-%d').date() if date_entretien_str else None

    nouveau_materiel = Materiel(
        nom_materiel=nom_materiel,
        numero_materiel=numero_materiel,
        description=description,
        prix_location_semaine=float(prix_location_semaine),
        date_achat=date_achat,
        quantite_disponible=int(quantite_disponible),
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
        checklist=checklist
    )

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
    emprunt_historique  = Emprunt.query.filter_by(id_materiel=materiel.id_materiel, statut=Statut_Emprunt.retourne).all()

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
    materiel = Materiel.query.get_or_404(numero_materiel)
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
    
    return render_template('modifier_materiel.html', materiel=materiel, categories=categories, typeenergies=typeenergies)

@app.route('/materiels/edit/<int:numero_materiel>', methods=['POST'])
def edit_materiel_post(numero_materiel):
    materiel = Materiel.query.filter_by(numero_materiel=numero_materiel).first()

    if not materiel:
        flash('Le matériel n\'existe pas.', 'danger')
        return redirect(url_for('get_materiels'))

    # Récupérer les nouvelles données depuis le formulaire
    materiel.nom_materiel = request.form['nom_materiel']
    materiel.numero_materiel = request.form['numero_materiel']
    materiel.description = request.form.get('description', '')
    materiel.prix_location_semaine = float(request.form['prix_location_semaine'])
    materiel.quantite_disponible = int(request.form['quantite_disponible'])
    materiel.categorie = request.form['categorie'].lower()
    materiel.niveau_danger = request.form['niveau_danger']
    materiel.poids = request.form.get('poids', type=float)
    materiel.reference = request.form['reference']
    materiel.num_serie = request.form['num_serie']
    materiel.marque = request.form['marque']
    materiel.localisation = request.form['localisation']
    materiel.lieu_achat = request.form['lieu_achat']
    materiel.type_energie = request.form['type_energie'].lower()
    materiel.dimensions = request.form['dimensions']
    materiel.accessoires_inclus = request.form['accessoires_inclus']
    materiel.securite = request.form['securite']

    # Gestion du fichier de facture (si un nouveau fichier est téléchargé)
    file = request.files.get('facture')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        materiel.facture = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
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

    # Récupérer et convertir les dates
    date_achat_str = request.form.get('date_achat')
    date_vidange_str = request.form.get('date_vidange')
    date_entretien_str = request.form.get('date_entretien')

    materiel.date_achat = datetime.strptime(date_achat_str, '%Y-%m-%d').date() if date_achat_str else None
    materiel.date_vidange = datetime.strptime(date_vidange_str, '%Y-%m-%d').date() if date_vidange_str else None
    materiel.date_entretien = datetime.strptime(date_entretien_str, '%Y-%m-%d').date() if date_entretien_str else None

    # Sauvegarder les changements dans la base de données
    db.session.commit()

    flash('Matériel modifié avec succès!', 'success')
    return redirect(url_for('get_materiel', numero_materiel=materiel.numero_materiel))
