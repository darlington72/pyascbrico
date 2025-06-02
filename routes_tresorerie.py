from flask import render_template, request, redirect, url_for, flash
from app import app,db
from models import Emprunt,Statut_Emprunt,Type_Paiement, Materiel, Consommable, Reparation, Caisse
from datetime import datetime
from collections import defaultdict
from sqlalchemy import func, extract

from datetime import datetime
from collections import defaultdict

@app.route('/tresorerie')
def tresorerie():
    annee_courante = datetime.now().year

    achats_materiels = Materiel.query.filter(
        db.extract('year', Materiel.date_achat) == annee_courante,
        Materiel.prix_achat > 0
    ).all()
    achats_consommables = Consommable.query.filter(
        db.extract('year', Consommable.date_achat) == annee_courante,
        Consommable.prix > 0
    ).all()
    reparations = Reparation.query.filter(
        db.extract('year', Reparation.date_cloture) == annee_courante,
        Reparation.montant > 0
    ).all()

    total_materiel = sum(m.prix_achat for m in achats_materiels if m.prix_achat)
    total_consommables = sum(c.prix for c in achats_consommables if c.prix)
    total_reparations = sum(r.montant for r in reparations if r.montant)
    total_global = total_materiel + total_consommables + total_reparations

    # Filtrer les emprunts dont le statut est "retourné"
    emprunts_retournes = Emprunt.query.filter(Emprunt.statut == 'retourne').all()

    recettes_par_paiement = db.session.query(
        Emprunt.type_paiement,
        func.sum(Emprunt.montant_paye).label('total_recette')
    ).filter(
        Emprunt.statut == 'retourne',  # Filtrer les emprunts retournés,
        extract('year', Emprunt.date_retour_effective) == annee_courante  # Filtrer par année en cours
    ).group_by(
        Emprunt.type_paiement
    ).all()

    # Calculer le total global
    total_recettes = sum(total for _, total in recettes_par_paiement)

    return render_template(
        'tresorerie.html',
        achats_materiels=achats_materiels,
        achats_consommables=achats_consommables,
        reparations=reparations,
        total_materiel=total_materiel,
        total_consommables=total_consommables,
        total_reparations=total_reparations,
        total_global=total_global,
        annee=annee_courante,
        recettes_par_paiement=recettes_par_paiement,
        total_recettes=total_recettes
    )

@app.route('/caisse')
def caisse():

    today = datetime.today()
    current_year = today.year
    current_week = today.isocalendar()[1]

    # ----------------------------
    # recupere les emprunts et les mouvements

    mouvements = Caisse.query.all()

    emprunts = Emprunt.query.filter(
        Emprunt.statut == Statut_Emprunt.retourne,
        Emprunt.montant_paye > 0,
    ).all()

    # Vérification de la récupération des emprunts retournés
    if not emprunts:
        flash("Aucun emprunt retourné pour l'année en cours.", "danger")
        return render_template('caisse.html', recettes=[], semaines=[], types_paiement=[])

    # Types de paiement disponibles, normalisation pour éviter les différences de casse ou espaces
    types_paiement = sorted(set([e.value.strip().lower() for e in Type_Paiement]))  # Normalisation : en minuscules, sans espaces

    # Créer un dictionnaire pour associer chaque type de paiement à son index dans la matrice
    type_paiement_index = {tp.strip().lower(): idx for idx, tp in enumerate(types_paiement)}

    # Initialiser une matrice 52xN (52 semaines x N types de paiement)
    matrice_recettes = [[0] * len(types_paiement) for _ in range(52)]  # 52 semaines, N types de paiement

    # Parcourir les emprunts retournés pour calculer les recettes
    for emprunt in emprunts:
        if emprunt.date_retour_effective.year == current_year:  # Vérifier que le montant payé est non nul
            semaine_retour = emprunt.date_retour_effective.isocalendar()[1] - 1  # Convertir en index 0-51
            type_paiement = emprunt.type_paiement.value.strip().lower()  # Normalisation du type de paiement (en minuscules et sans espaces)

            # Vérifier si le type de paiement existe dans le dictionnaire
            index_type_paiement = type_paiement_index.get(type_paiement)

            # Si un index valide est trouvé, mettre à jour la matrice
            if index_type_paiement is not None:
                matrice_recettes[semaine_retour][index_type_paiement] += emprunt.montant_paye

    # Préparer les données pour l'affichage
    semaines = list(range(1, 53))  # Les 52 semaines de l'année
    recettes_affichees = []
    for i, semaine in enumerate(semaines):
        recettes_semaine = {types_paiement[j]: matrice_recettes[i][j] for j in range(len(types_paiement))}
        recettes_affichees.append({'semaine': semaine, 'recettes': recettes_semaine})

    # ----------------------------
    # solde CB par semaine

    total_cb = 0
    for emprunt in emprunts:
        if emprunt.date_retour_effective.year == current_year and emprunt.type_paiement == Type_Paiement.CB and emprunt.date_retour_effective.isocalendar()[1] == current_week: 
            total_cb += emprunt.montant_paye

    # ----------------------------
    # etat de l'espece = sommes des emprunts retournes en especes - mouvement banquaire en espece

    total_espece = 0
    for emprunt in emprunts:
        if emprunt.type_paiement == Type_Paiement.espece: 
            total_espece = total_espece + emprunt.montant_paye
    for mouvement in mouvements:
        if mouvement.moyen_paiement == Type_Paiement.espece:
            total_espece = total_espece - mouvement.montant

    # ----------------------------
    # etat des cheques = sommes des emprunts retournes en cheque - mouvement banquaire en cheque

    total_cheque = 0
    for emprunt in emprunts:
        if emprunt.type_paiement == Type_Paiement.cheque: 
            total_cheque = total_cheque + emprunt.montant_paye
    for mouvement in mouvements:
        if mouvement.moyen_paiement == Type_Paiement.cheque:
            total_cheque = total_cheque - mouvement.montant    
    

    # Passer les données au template pour affichage
    return render_template('caisse.html', recettes_affichees=recettes_affichees, semaines=semaines,
    total_cb=total_cb,total_espece=total_espece,total_cheque=total_cheque,
    types_paiement=types_paiement,mouvements=mouvements)


@app.route("/nouveau_mouvement", methods=["POST"])
def nouveau_mouvement():
    try:
        montant = float(request.form.get("montant"))
        type_paiement = request.form.get("types_paiement")
        description = request.form.get("description")

        if montant <= 0:
            flash("Veuillez remplir tous les champs correctement.", "danger")
            return redirect(url_for("caisse"))

        mouvement = Caisse(
            montant=montant,
            moyen_paiement=Type_Paiement[type_paiement],
            description=description,
            date_mouvement=datetime.now()
        )
        db.session.add(mouvement)
        db.session.commit()
        flash("Mouvement de caisse enregistré avec succès.", "success")
        return redirect(url_for("caisse"))

    except Exception as e:
        db.session.rollback()
        flash(f"Erreur lors de l'enregistrement : {str(e)}", "danger")
        return redirect(url_for("caisse"))

    return redirect(url_for('caisse'))
