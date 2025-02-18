from flask import render_template, request, redirect, url_for, flash
from app import app,db
from models import Emprunt,Statut_Emprunt,Type_Paiement
from datetime import datetime
from collections import defaultdict

from datetime import datetime
from collections import defaultdict

@app.route('/recettes')
def recettes():
    current_year = datetime.today().year  # Obtenir l'année courante

    # Récupérer les emprunts retournés pour l'année courante
    emprunts_retournes = Emprunt.query.filter(
        Emprunt.statut == Statut_Emprunt.retourne
    ).all()

    # Vérification de la récupération des emprunts retournés
    if not emprunts_retournes:
        flash("Aucun emprunt retourné pour l'année en cours.", "warning")
        return render_template('recettes.html', recettes=[], semaines=[], types_paiement=[])

    # Types de paiement disponibles, normalisation pour éviter les différences de casse ou espaces
    types_paiement = sorted(set([e.value.strip().lower() for e in Type_Paiement]))  # Normalisation : en minuscules, sans espaces

    # Créer un dictionnaire pour associer chaque type de paiement à son index dans la matrice
    type_paiement_index = {tp.strip().lower(): idx for idx, tp in enumerate(types_paiement)}

    # Initialiser une matrice 52xN (52 semaines x N types de paiement)
    matrice_recettes = [[0] * len(types_paiement) for _ in range(52)]  # 52 semaines, N types de paiement

    # Parcourir les emprunts retournés pour calculer les recettes
    for emprunt in emprunts_retournes:
        if emprunt.montant_paye and emprunt.date_retour_effective.year == current_year:  # Vérifier que le montant payé est non nul
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

    # Passer les données au template pour affichage
    return render_template('recettes.html', recettes=recettes_affichees, semaines=semaines, types_paiement=types_paiement)
