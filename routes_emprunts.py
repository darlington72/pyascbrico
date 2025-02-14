from flask import render_template, request, redirect, url_for, flash
from app import app,db
from models import Emprunt,Adherent,Materiel,Statut_Emprunt,TypeEnergie,Categorie,Etat,Type_Paiement, Consommable
from datetime import datetime, timedelta
import calendar
from sqlalchemy import or_

@app.route('/emprunts')
def get_emprunts():
    emprunts = Emprunt.query.all()

    emprunts_en_cours = Emprunt.query.filter_by(statut=Statut_Emprunt.en_cours).all()

    emprunts_reserve = Emprunt.query.filter_by(statut=Statut_Emprunt.reserve).all()

    emprunts_termine = Emprunt.query.filter(
        or_(Emprunt.statut == Statut_Emprunt.retourne, Emprunt.statut == Statut_Emprunt.annule)
    ).all()

    emprunts_retour = []
    emprunts_courant = []
    for emprunt in emprunts_en_cours:
        # Calculer la semaine et l'année de la date de retour
        date_retour = emprunt.date_debut + timedelta(weeks=emprunt.duree)
        year_retour, week_retour = date_retour.isocalendar()[0], date_retour.isocalendar()[1]
        
        # Obtenir l'année et la semaine actuelles
        current_year, current_week = datetime.now().isocalendar()[0], datetime.now().isocalendar()[1]

        # Comparer année et semaine
        if year_retour < current_year or (year_retour == current_year and week_retour <= current_week):
            emprunts_retour.append(emprunt)
        else:
            emprunts_courant.append(emprunt)

    return render_template('emprunts.html', emprunts=emprunts,emprunts_courant=emprunts_courant,emprunts_retour=emprunts_retour,emprunts_reserve=emprunts_reserve,emprunts_termine=emprunts_termine)


@app.route('/emprunts/historique')
def get_historique_emprunts():
    emprunts_termine = Emprunt.query.filter(
        or_(Emprunt.statut == Statut_Emprunt.retourne, Emprunt.statut == Statut_Emprunt.annule)
    ).all()

    return render_template('historique_emprunts.html',emprunts_termine=emprunts_termine)


@app.route('/emprunts/<int:id_emprunt>')
def get_emprunt(id_emprunt):

    emprunt = Emprunt.query.filter_by(id_emprunt=id_emprunt).first()
    if not emprunt:
        flash('L emprunt demandé n\'existe pas.', 'danger')
        return redirect(url_for('get_emprunts'))

    materiel = Materiel.query.filter_by(id_materiel=emprunt.id_materiel).first()
    adherent = Adherent.query.filter_by(id_adherent=emprunt.id_adherent).first()

    consommables = []
    for consommable_id in emprunt.consommables_ids:
        consommable = Consommable.query.filter_by(id_consommable=consommable_id).first()
        if(consommable):
            consommables.append(consommable)

    annule = False
    if emprunt.statut == Statut_Emprunt.en_cours or emprunt.statut == Statut_Emprunt.reserve:
        annule = True

    retour = False
    if emprunt.statut == Statut_Emprunt.en_cours:
        # Calculer la semaine et l'année de la date de retour
        date_retour = emprunt.date_debut + timedelta(weeks=emprunt.duree)
        year_retour, week_retour = date_retour.isocalendar()[0], date_retour.isocalendar()[1]
        
        # Obtenir l'année et la semaine actuelles
        current_year, current_week = datetime.now().isocalendar()[0], datetime.now().isocalendar()[1]

        # Comparer année et semaine
        if year_retour < current_year or (year_retour == current_year and week_retour <= current_week):
            retour = True

    return render_template('emprunt.html', emprunt=emprunt,materiel=materiel,adherent=adherent,annule=annule,retour=retour,consommables=consommables)

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
        date_debut_str = datetime.strftime(date_debut, "%Y-%m-%d")
        date_fin = (date_debut + timedelta(weeks=duree))
        date_fin_str = date_fin.strftime("%Y-%m-%d")

        # Gérer les consommables (par défaut, aucun consommable)
        consommables_ids = request.form.getlist('consommables[]')

        cout_consommables = 0
        consommables = []
        for consommable_id in consommables_ids:
            consommable = Consommable.query.filter_by(id_consommable=consommable_id).first()
            cout_consommables = cout_consommables + consommable.prix
            consommables.append(consommable)

        # Estimation du cout 
        cout_estime = duree * materiel.prix_location_semaine + cout_consommables

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

        # etat des consommables
        for consommable in consommables:
            if consommable.quantite_disponible == 0:
                flash('Impossible. L\'un des consommables n\'est pas disponible', 'danger')
                return redirect(url_for('get_emprunts'))  

        # disponible sur cette date
        emprunts = Emprunt.query.filter(
            Emprunt.id_materiel == materiel.id_materiel,  # Argument positionnel
            Emprunt.statut.in_([Statut_Emprunt.en_cours, Statut_Emprunt.reserve])
        ).all()
        conflit = 0
        for emprunt in emprunts:
            date_fin_emprunt = (emprunt.date_debut + timedelta(weeks=emprunt.duree))
            if (emprunt.date_debut < date_fin.date() and date_fin_emprunt > date_debut.date()):
                conflit = 1
                break
        if conflit:
            flash('Impossible. Le matériel est déjà reservé sur ce créneau.', 'danger')
            return redirect(url_for('get_emprunts'))  

        # disponible immediatemment
        emprunts_en_cours = Emprunt.query.filter_by(id_materiel=id_materiel,statut=Statut_Emprunt.en_cours).first()
        if emprunts_en_cours and date_debut.isocalendar()[1] <= datetime.now().isocalendar()[1]:
            flash('Impossible. Le matériel n est pas encore revenu', 'danger')
            return redirect(url_for('get_emprunts')) 


        # verifier si c'est en cours ou reservé pour plus tard
        if datetime.now().isocalendar()[1] < date_debut.isocalendar()[1] and datetime.now().year == date_debut.year:
            statut = Statut_Emprunt.reserve
        else:
            statut = Statut_Emprunt.en_cours

        # Créer un dictionnaire avec les données pour les passer à la confirmation
        emprunt_data = {
            'date_debut': date_debut_str,
            'duree': duree,
            'remarques': remarques,
            'date_fin': date_fin_str,
            'cout_estime':cout_estime,
            'statut':statut,
            'consommables_ids':consommables_ids
        }

        return render_template('confirmation_emprunt.html', emprunt_data=emprunt_data,materiel=materiel,checklist=checklist,
        adherent=adherent,accessoires=accessoires,consommables=consommables)

    # Récupérer les matériels et adhérents pour le formulaire
    materiels = Materiel.query.all()
    adherents = Adherent.query.all()
    consommables = Consommable.query.all()

    current_date = datetime.now().strftime('%Y-%m-%d')

    return render_template('nouvel_emprunt.html', materiels=materiels, adherents=adherents,current_date=current_date,consommables=consommables)


@app.route('/emprunts/confirm', methods=['POST'])
def confirm_emprunt():
    # Récupérer les données de l'emprunt depuis le formulaire de confirmation
    duree = request.form['duree']
    id_materiel = request.form['id_materiel']
    id_adherent = request.form['id_adherent']
    remarques = request.form['remarques']
    statut = request.form['statut']
    consommables_ids = request.form['consommables_ids']

    # Convertir la chaîne en objet datetime.date
    date_loc_str = request.form.get('date_debut')
    date_loc = datetime.strptime(date_loc_str, '%Y-%m-%d').date() if date_loc_str else None

    # Créer l'objet Emprunt
    nouvel_emprunt = Emprunt(
        date_debut=date_loc,
        duree=duree,
        statut=statut,
        id_materiel=id_materiel,
        id_adherent=id_adherent,
        remarques=remarques,
        consommables_ids=consommables_ids
    )

    for consommable_id in consommables_ids:
        consommable = Consommable.query.filter_by(id_consommable=consommable_id).first()
        if(consommable):
            consommable.quantite_disponible = consommable.quantite_disponible - 1

    # Ajouter à la base de données
    db.session.add(nouvel_emprunt)
    db.session.commit()

    flash('Emprunt créé avec succès!', 'success')
    return redirect(url_for('get_emprunts'))  # Redirige vers la liste des emprunts

@app.route('/emprunts/cancel/<int:id_emprunt>', methods=['POST'])
def cancel_emprunt(id_emprunt):

    emprunt = Emprunt.query.filter_by(id_emprunt=id_emprunt).first()
    if not emprunt:
        flash('L emprunt demandé n\'existe pas.', 'danger')
        return redirect(url_for('get_emprunts'))

    if emprunt.statut == Statut_Emprunt.retourne or emprunt.statut == Statut_Emprunt.annule:
        flash('L emprunt est déjà cloturé.', 'danger')
        return redirect(url_for('get_emprunts'))

    emprunt.statut = Statut_Emprunt.annule

    db.session.commit()

    flash('Emprunt annulé avec succès!', 'success')
    return redirect(url_for('get_emprunts'))  # Redirige vers la liste des emprunts


@app.route('/emprunts/<int:id_emprunt>/retour', methods=['GET', 'POST'])
def retour_emprunt(id_emprunt):
    emprunt = Emprunt.query.get_or_404(id_emprunt)

    type_paiement = [c.value for c in Type_Paiement]
    etats = [c.value for c in Etat]

    # Récupérer et traiter la checklist
    checklist = None
    if emprunt.materiel.checklist:
        checklist = [item.strip() for item in emprunt.materiel.checklist.split(',') if item.strip()]    

    # Récupérer et traiter les accessoires
    accessoires = None
    if emprunt.materiel.accessoires_inclus:
        accessoires = [item.strip() for item in emprunt.materiel.accessoires_inclus.split(',') if item.strip()]  

    emprunt.date_retour_effective = datetime.today().date()  # Date de retour actuelle
    if emprunt.date_debut.year != emprunt.date_retour_effective.year:
        duree_reelle = 52 - emprunt.date_debut.isocalendar()[1] + emprunt.date_retour_effective.isocalendar()[1] 
    else:
        duree_reelle = emprunt.date_retour_effective.isocalendar()[1] - emprunt.date_debut.isocalendar()[1] 

    # cout reel
    """Calcule le coût total de l'emprunt (matériel + consommables)."""
    # Calcul du coût de la location du matériel
    cout_location = emprunt.materiel.prix_location_semaine * duree_reelle

    # Calcul du coût des consommables
    consommables = []
    cout_consommables = 0
    for consommable_id in emprunt.consommables_ids:
        consommable = Consommable.query.filter_by(id_consommable=consommable_id).first()
        if(consommable):
            cout_consommables += consommable.prix
            consommables.append(consommable)

    # Coût total de l'emprunt
    cout_reel = cout_location + cout_consommables

    # Si la méthode est POST, le matériel est retourné
    if request.method == 'POST':
        # Changer le statut de l'emprunt à "retourné"
        emprunt.statut = Statut_Emprunt.retourne
        
        emprunt.type_paiement = request.form['type_paiement']
        emprunt.montant_paye = float(request.form['montant_paye'])
        emprunt.duree = duree_reelle
        emprunt.materiel.nb_heure = emprunt.materiel.nb_heure + int(request.form['nb_heure'])
        emprunt.materiel.etat = request.form['etat']

        # maj database
        db.session.commit()

        # Flash message de succès
        flash(f"Emprunt retourné avec succès !", "success")
        return redirect(url_for('get_emprunts'))  # Redirection vers la page des emprunts

    return render_template('retour_emprunt.html', emprunt=emprunt, etats=etats,consommables=consommables,
    type_paiement=type_paiement,duree_reelle=duree_reelle,cout_reel=cout_reel,
    checklist=checklist,accessoires=accessoires)


