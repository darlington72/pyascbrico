from flask import Flask
from models import db
from models import Materiel, Adherent, Consommable, Emprunt, Reparation, TypeEnergie, Categorie, Etat, Statut_Adherent, Type_Paiement, Statut_Emprunt, Statut_Reparation
import json
from datetime import date

UPLOAD_FOLDER = 'uploads'  # Répertoire où vous souhaitez stocker les fichiers

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'mysecretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)

with app.app_context():
    db.create_all()  # Create tables
    # Vider la base de données
    db.drop_all()
    db.create_all()

    # 1. Ajouter des matériels (Materiel)
    materiel1 = Materiel(
        numero_materiel=1001,
        nom_materiel="Perceuse électrique",
        description="Perceuse sans fil, idéale pour les travaux de bricolage",
        prix_location_semaine=15.0,
        etat=Etat.ok,
        date_achat=date(2020, 6, 15),
        quantite_disponible=10,
        categorie=Categorie.automobile,
        poids=2.5,
        marque="Bosch",
        type_energie=TypeEnergie.secteur,
        prix_achat=120.0,
        localisation="A1",
        niveau_danger=1
    )

    materiel2 = Materiel(
        numero_materiel=1002,
        nom_materiel="Tondeuse à gazon",
        description="Tondeuse avec moteur thermique, idéale pour les grands jardins.",
        prix_location_semaine=25.0,
        etat=Etat.ok,
        date_achat=date(2021, 4, 10),
        quantite_disponible=5,
        categorie=Categorie.jardinage,
        poids=15.0,
        marque="Honda",
        type_energie=TypeEnergie.thermique,
        prix_achat=500.0,
        localisation="B2",
        niveau_danger=2
    )

    db.session.add_all([materiel1, materiel2])
    db.session.commit()

    # 2. Ajouter des adhérents (Adherent)
    adherent1 = Adherent(
        nom="Dupont",
        prenom="Jean",
        email="jean.dupont@example.com",
        statut=Statut_Adherent.cie,
        telephone="0612345678",
        depuis=date(2019, 5, 10),
        badge="ADH001"
    )

    adherent2 = Adherent(
        nom="Martin",
        prenom="Sophie",
        email="sophie.martin@example.com",
        statut=Statut_Adherent.retraite,
        telephone="0698765432",
        depuis=date(2018, 8, 25),
        badge="ADH002"
    )

    db.session.add_all([adherent1, adherent2])
    db.session.commit()

    # 3. Ajouter des consommables (Consommable)
    consommable1 = Consommable(
        nom_consommable="Foret 6mm",
        description="Foret pour perceuse, idéal pour les travaux en bois",
        prix=3.0,
        date_achat=date(2021, 7, 1),
        quantite_disponible=100,
        categorie=Categorie.bois,
        marque="Bosch"
    )

    consommable2 = Consommable(
        nom_consommable="Huile moteur 2T",
        description="Huile moteur pour tondeuse à gazon",
        prix=12.0,
        date_achat=date(2022, 5, 10),
        quantite_disponible=50,
        categorie=Categorie.jardinage,
        marque="Castrol"
    )

    db.session.add_all([consommable1, consommable2])
    db.session.commit()

    # 4. Ajouter des emprunts (Emprunt)
    emprunt1 = Emprunt(
        date_debut=date(2023, 1, 5),
        duree=4,  # 4 semaines
        statut=Statut_Emprunt.en_cours,
        id_materiel=materiel1.id_materiel,
        id_adherent=adherent1.id_adherent,
        consommables_ids=json.dumps([consommable1.id_consommable]),
        montant_paye=60.0,
        type_paiement=Type_Paiement.CB
    )

    emprunt2 = Emprunt(
        date_debut=date(2023, 2, 10),
        duree=3,  # 3 semaines
        statut=Statut_Emprunt.en_cours,
        id_materiel=materiel2.id_materiel,
        id_adherent=adherent2.id_adherent,
        consommables_ids=json.dumps([consommable2.id_consommable]),
        montant_paye=80.0,
        type_paiement=Type_Paiement.cheque
    )

    db.session.add_all([emprunt1, emprunt2])
    db.session.commit()

    # 5. Ajouter des réparations (Reparation)
    reparation1 = Reparation(
        statut=Statut_Reparation.en_cours,
        id_materiel=materiel1.id_materiel,
        remarques="Réparation du moteur, il surchauffe après 30 minutes d'utilisation.",
        montant=50.0
    )

    reparation2 = Reparation(
        statut=Statut_Reparation.termine,
        id_materiel=materiel2.id_materiel,
        remarques="Réparation du carter de la tondeuse après un choc.",
        montant=120.0
    )

    db.session.add_all([reparation1, reparation2])
    db.session.commit()

    # Ajouter plus de matériels (Materiel)
    materiel5 = Materiel(
        numero_materiel=1005,
        nom_materiel="Moteur thermique",
        description="Moteur thermique pour générateur, utilisation pour divers équipements.",
        prix_location_semaine=30.0,
        etat=Etat.ok,
        date_achat=date(2022, 3, 15),
        quantite_disponible=5,
        categorie=Categorie.automobile,
        poids=30.0,
        marque="Honda",
        type_energie=TypeEnergie.thermique,
        prix_achat=800.0,
        localisation="E5",
        niveau_danger=3
    )

    materiel6 = Materiel(
        numero_materiel=1006,
        nom_materiel="Meuleuse d'angle",
        description="Meuleuse d'angle professionnelle pour les travaux de découpe et de meulage.",
        prix_location_semaine=22.0,
        etat=Etat.ok,
        date_achat=date(2020, 10, 20),
        quantite_disponible=7,
        categorie=Categorie.batiment,
        poids=4.0,
        marque="Bosch",
        type_energie=TypeEnergie.secteur,
        prix_achat=250.0,
        localisation="F6",
        niveau_danger=2
    )

    materiel7 = Materiel(
        numero_materiel=1007,
        nom_materiel="Scie sauteuse",
        description="Scie sauteuse avec changement rapide de lame, idéale pour découper des matériaux divers.",
        prix_location_semaine=18.0,
        etat=Etat.ok,
        date_achat=date(2018, 5, 10),
        quantite_disponible=10,
        categorie=Categorie.batiment,
        poids=2.0,
        marque="Black & Decker",
        type_energie=TypeEnergie.secteur,
        prix_achat=100.0,
        localisation="G7",
        niveau_danger=2
    )

    db.session.add_all([materiel5, materiel6, materiel7])
    db.session.commit()

    # Ajouter plus d'adhérents (Adherent)
    adherent5 = Adherent(
        nom="Durand",
        prenom="Emilie",
        email="emilie.durand@example.com",
        statut=Statut_Adherent.cie,
        telephone="0623456789",
        depuis=date(2021, 4, 5),
        badge="ADH005"
    )

    adherent6 = Adherent(
        nom="Pires",
        prenom="José",
        email="jose.pires@example.com",
        statut=Statut_Adherent.non_cie,
        telephone="0686549873",
        depuis=date(2022, 1, 10),
        badge="ADH006"
    )

    adherent7 = Adherent(
        nom="Hernandez",
        prenom="Carlos",
        email="carlos.hernandez@example.com",
        statut=Statut_Adherent.retraite,
        telephone="0652148796",
        depuis=date(2017, 11, 25),
        badge="ADH007"
    )

    db.session.add_all([adherent5, adherent6, adherent7])
    db.session.commit()

    # Ajouter plus de consommables (Consommable)
    consommable5 = Consommable(
        nom_consommable="Lame de scie circulaire",
        description="Lame de scie circulaire pour découpe du bois et du métal.",
        prix=20.0,
        date_achat=date(2022, 2, 15),
        quantite_disponible=25,
        categorie=Categorie.bois,
        marque="Makita"
    )

    consommable6 = Consommable(
        nom_consommable="Filtre à air pour moteur",
        description="Filtre à air pour moteurs thermiques, adapté pour tondeuses et générateurs.",
        prix=10.0,
        date_achat=date(2022, 4, 5),
        quantite_disponible=50,
        categorie=Categorie.automobile,
        marque="Honda"
    )

    consommable7 = Consommable(
        nom_consommable="Batterie lithium",
        description="Batterie lithium de remplacement pour perceuses et autres outils sans fil.",
        prix=25.0,
        date_achat=date(2021, 8, 1),
        quantite_disponible=30,
        categorie=Categorie.divers,
        marque="Bosch"
    )

    db.session.add_all([consommable5, consommable6, consommable7])
    db.session.commit()

    # Ajouter plus d'emprunts (Emprunt)
    emprunt5 = Emprunt(
        date_debut=date(2023, 5, 15),
        duree=3,  # 3 semaines
        statut=Statut_Emprunt.en_cours,
        id_materiel=materiel5.id_materiel,
        id_adherent=adherent5.id_adherent,
        consommables_ids=json.dumps([consommable5.id_consommable, consommable6.id_consommable]),
        montant_paye=90.0,
        type_paiement=Type_Paiement.CB
    )

    emprunt6 = Emprunt(
        date_debut=date(2023, 6, 1),
        duree=4,  # 4 semaines
        statut=Statut_Emprunt.en_cours,
        id_materiel=materiel6.id_materiel,
        id_adherent=adherent6.id_adherent,
        consommables_ids=json.dumps([consommable7.id_consommable]),
        montant_paye=70.0,
        type_paiement=Type_Paiement.cheque
    )

    emprunt7 = Emprunt(
        date_debut=date(2023, 7, 10),
        duree=2,  # 2 semaines
        statut=Statut_Emprunt.reserve,
        id_materiel=materiel7.id_materiel,
        id_adherent=adherent7.id_adherent,
        consommables_ids=json.dumps([consommable6.id_consommable]),
        montant_paye=50.0,
        type_paiement=Type_Paiement.espece
    )

    db.session.add_all([emprunt5, emprunt6, emprunt7])
    db.session.commit()

    # Ajouter des réparations (Reparation)
    reparation1 = Reparation(
        statut=Statut_Reparation.en_cours,
        id_materiel=materiel1.id_materiel,
        remarques="Le moteur semble légèrement en surchauffe.",
        montant=75.0
    )

    reparation2 = Reparation(
        statut=Statut_Reparation.termine,
        id_materiel=materiel2.id_materiel,
        remarques="Réparation du moteur, tout fonctionne correctement maintenant.",
        montant=50.0
    )

    reparation3 = Reparation(
        statut=Statut_Reparation.en_cours,
        id_materiel=materiel5.id_materiel,
        remarques="Remplacement des roulements de la scie.",
        montant=40.0
    )

    db.session.add_all([reparation1, reparation2, reparation3])
    db.session.commit()

    print("Base de données peuplée avec succès !")

    print("Base de données peuplée avec succès.")
