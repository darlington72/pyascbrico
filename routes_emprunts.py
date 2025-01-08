from flask import render_template, request, redirect, url_for, flash
from app import app,db
from models import Emprunt,Adherent,Materiel,Statut_Emprunt,TypeEnergie,Categorie,Etat,Type_Paiement, Consommable
from datetime import datetime, timedelta

@app.route('/emprunts')
def get_emprunts():
    emprunts = Emprunt.query.all()
    emprunts_en_cours = Emprunt.query.filter_by(statut=Statut_Emprunt.en_cours).all()
    emprunts_termine = Emprunt.query.filter_by(statut=Statut_Emprunt.retourne).all()

    return render_template('emprunts.html', emprunts=emprunts,emprunts_en_cours=emprunts_en_cours,emprunts_termine=emprunts_termine)

@app.route('/emprunts/create', methods=['GET', 'POST'])
def create_emprunt():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        date_debut = request.form['date_debut']
        duree = int(request.form.get("duree"))
        id_materiel = request.form['materiel']
        id_adherent = request.form['adherent']
        remarques = request.form.get('remarques', '')

        materiel = Materiel.query.filter_by(id_materiel=id_materiel).first()
        adherent = Adherent.query.filter_by(id_adherent=id_adherent).first()

        # Récupérer et traiter la checklist
        checklist = None
        if materiel.checklist:
            checklist = [item.strip() for item in materiel.checklist.split(',') if item.strip()]    

        # Récupérer et traiter les accessoires
        accessoires = None
        if materiel.accessoires_inclus:
            accessoires = [item.strip() for item in materiel.accessoires_inclus.split(',') if item.strip()]   

        # Calcul de la date de fin en fonction de la durée
        date_debut = datetime.strptime(date_debut, "%Y-%m-%d")
        date_fin = (date_debut + timedelta(days=7*duree)).strftime("%Y-%m-%d")

        # Estimation du cout 
        cout_estime = duree * materiel.prix_location_semaine

        # Créer un dictionnaire avec les données pour les passer à la confirmation
        emprunt_data = {
            'date_debut': request.form['date_debut'],
            'duree': duree,
            'remarques': remarques,
            'date_fin': date_fin,
            'cout_estime':cout_estime
        }

        # ---------------------------------------------------------------------------
        # Verifier toutes les erreurs possibles 
        # ---------------------------------------------------------------------------
        # etat de l'adherent
        if adherent.valide_asc != True:
            flash('Impossible. L adherent n est pas valide.', 'danger')
            return redirect(url_for('get_emprunts'))  

        # etat de l'adherent
        if int(adherent.blame) == 3:
            flash('Impossible. L adherent est banni.', 'danger')
            return redirect(url_for('get_emprunts'))  

        # etat du materiel
        if materiel.etat != Etat.ok:
            flash('Impossible. Le matériel est en panne ou reformé.', 'danger')
            return redirect(url_for('get_emprunts'))  

        # statut d'emprunt du materiel sur ces dates
        emprunt_en_cours    = Emprunt.query.filter_by(id_materiel=materiel.id_materiel, statut=Statut_Emprunt.en_cours).first()
        emprunt_reserve     = Emprunt.query.filter_by(id_materiel=materiel.id_materiel, statut=Statut_Emprunt.reserve).all()



        return render_template('confirmation_emprunt.html', emprunt_data=emprunt_data,materiel=materiel,checklist=checklist,
        adherent=adherent,accessoires=accessoires)

    # Récupérer les matériels et adhérents pour le formulaire
    materiels = Materiel.query.all()
    adherents = Adherent.query.all()

    current_date = datetime.now().strftime('%Y-%m-%d')

    return render_template('nouvel_emprunt.html', materiels=materiels, adherents=adherents,current_date=current_date)


@app.route('/emprunts/confirm', methods=['POST'])
def confirm_emprunt():
    # Récupérer les données de l'emprunt depuis le formulaire de confirmation
    duree = request.form['duree']
    id_materiel = request.form['id_materiel']
    id_adherent = request.form['id_adherent']
    remarques = request.form['remarques']

    # Convertir la chaîne en objet datetime.date
    date_loc_str = request.form.get('date_debut')
    date_loc = datetime.strptime(date_loc_str, '%Y-%m-%d').date() if date_loc_str else None

    # Créer l'objet Emprunt
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



@app.route('/emprunts/<int:id_emprunt>/retour', methods=['GET', 'POST'])
def retour_emprunt(id_emprunt):
    emprunt = Emprunt.query.get_or_404(id_emprunt)

    type_paiement = [c.value for c in Type_Paiement]

    # Si la méthode est POST, le matériel est retourné
    if request.method == 'POST':
        # Changer le statut de l'emprunt à "retourné"
        emprunt.statut = Statut_Emprunt.retourne
        emprunt.date_retour_effective = datetime.today().date()  # Date de retour actuelle

        type_paiement = request.form['type_paiement']
        emprunt.type_paiement = type_paiement

        # maj database
        db.session.commit()

        # Récupérer le montant payé
        montant_paye = float(request.form['montant_paye'])

        # Flash message de succès
        flash(f"Emprunt retourné avec succès !", "success")
        return redirect(url_for('get_emprunts'))  # Redirection vers la page des emprunts

    # Récupération des consommables associés (s'ils existent) pour les afficher
    consommables = []
    if emprunt.consommables_list:
        consommables = Consommable.query.filter(Consommable.id_consommable.in_(emprunt.consommables_list)).all()

    return render_template('retour_emprunt.html', emprunt=emprunt, consommables=consommables,type_paiement=type_paiement)


