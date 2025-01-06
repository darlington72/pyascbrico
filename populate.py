from flask import Flask
from models import db
from models import Materiel, Adherent, Consommable, Emprunt, Reparation, TypeEnergie, Categorie, Etat, Type_Paiement, Statut_Emprunt, Statut_Reparation
import json
from datetime import datetime, timedelta
import random

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

# Peupler la base de données avec des exemples
with app.app_context():

    # Fonction pour générer des données aléatoires pour un `Materiel`
    def generate_random_materiel():
        # Choix des valeurs
        nom = f"Materiel_{random.randint(1, 1000)}"
        description = f"Description détaillée pour {nom}"
        prix_location_semaine = random.uniform(10, 100)
        etat = random.choice([Etat.en_panne, Etat.reforme, Etat.ok])
        date_achat = datetime.today() - timedelta(days=random.randint(100, 3650))
        categorie = random.choice(list(Categorie))
        poids = random.uniform(1, 50)
        reference = f"REF_{random.randint(10000, 99999)}"
        num_serie = f"SN_{random.randint(100000, 999999)}"
        date_vidange = datetime.today() - timedelta(days=random.randint(30, 1000))
        date_entretien = datetime.today() - timedelta(days=random.randint(30, 1000))
        nb_heure = random.randint(0, 1000)
        marque = f"Marque_{random.choice(['A', 'B', 'C', 'D'])}"
        facture = f"/path/to/facture_{random.randint(1, 100)}.pdf"
        prix_achat = random.uniform(50, 5000)
        lieu_achat = f"URL_{random.randint(1, 100)}"
        localisation = f"Loc_{random.randint(1, 100)}"
        manuel_user = f"/path/to/manuel_{random.randint(1, 100)}.pdf"
        vue_eclatee = f"/path/to/vue_eclatee_{random.randint(1, 100)}.jpg"
        type_energie = random.choice(list(TypeEnergie))
        dimensions = f"{random.randint(10, 100)}x{random.randint(10, 100)}x{random.randint(10, 100)}"
        accessoires_inclus = f"Accessoire_{random.randint(1, 100)}"
        niveau_danger = random.randint(1, 3)
        securite = f"Sécurité liée à {nom}"
        checklist = f"Vérifications pour {nom}"
        avis_client = random.uniform(1, 5)

        materiel = Materiel(
            numero_materiel=random.randint(1, 100000),
            nom_materiel=nom,
            description=description,
            prix_location_semaine=prix_location_semaine,
            etat=etat,
            date_achat=date_achat,
            categorie=categorie,
            poids=poids,
            reference=reference,
            num_serie=num_serie,
            date_vidange=date_vidange,
            date_entretien=date_entretien,
            nb_heure=nb_heure,
            marque=marque,
            facture=facture,
            prix_achat=prix_achat,
            lieu_achat=lieu_achat,
            localisation=localisation,
            manuel_user=manuel_user,
            vue_eclatee=vue_eclatee,
            type_energie=type_energie,
            dimensions=dimensions,
            accessoires_inclus=accessoires_inclus,
            niveau_danger=niveau_danger,
            securite=securite,
            checklist=checklist,
            avis_client=avis_client
        )

        db.session.add(materiel)

    # Fonction pour générer des données aléatoires pour un `Adherent`
    def generate_random_adherent():
        nom = f"Adherent_{random.randint(1, 1000)}"
        prenom = f"Prenom_{random.randint(1, 1000)}"
        valide_asc = random.choice([True, False])
        email = f"adherent{random.randint(1, 1000)}@example.com"
        statut = "Agent actif CIE"
        telephone = f"0600{random.randint(100000, 999999)}"
        depuis = datetime.today() - timedelta(days=random.randint(0, 3650))
        badge = f"Badge_{random.randint(1, 100)}"

        adherent = Adherent(
            nom=nom,
            prenom=prenom,
            valide_asc=valide_asc,
            email=email,
            statut=statut,
            telephone=telephone,
            depuis=depuis,
            badge=badge
        )

        db.session.add(adherent)

    # Fonction pour générer des données aléatoires pour un `Consommable`
    def generate_random_consommable():
        nom = f"Consommable_{random.randint(1, 1000)}"
        description = f"Description pour {nom}"
        prix = random.uniform(1, 50)
        date_achat = datetime.today() - timedelta(days=random.randint(30, 1000))
        quantite_disponible = random.randint(1, 100)
        categorie = random.choice(list(Categorie))
        reference = f"REF_{random.randint(10000, 99999)}"
        marque = f"Marque_{random.choice(['X', 'Y', 'Z'])}"
        facture = f"/path/to/facture_{random.randint(1, 100)}.pdf"

        consommable = Consommable(
            nom_consommable=nom,
            description=description,
            prix=prix,
            date_achat=date_achat,
            quantite_disponible=quantite_disponible,
            categorie=categorie,
            reference=reference,
            marque=marque,
            facture=facture
        )

        db.session.add(consommable)

    # Fonction pour générer des données aléatoires pour un `Emprunt`
    def generate_random_emprunt():
        date_debut = datetime.today() - timedelta(days=random.randint(0, 365))
        duree = random.randint(1, 10)  # Durée en semaines
        statut = random.choice(list(Statut_Emprunt))
        id_materiel = random.randint(1, 100)  # Vous devez adapter cela selon vos IDs existants
        id_adherent = random.randint(1, 100)  # Idem pour les IDs d'adhérents
        remarques = f"Remarque sur l'emprunt {random.randint(1, 1000)}"
        date_retour_effective = datetime.today() - timedelta(days=random.randint(0, 365))
        historique_statuts = f"Statut: {statut}"
        consommables_ids = json.dumps([random.randint(1, 100) for _ in range(random.randint(1, 5))])
        montant_paye = random.uniform(10, 100)
        type_paiement = random.choice(list(Type_Paiement))

        emprunt = Emprunt(
            date_debut=date_debut,
            duree=duree,
            statut=statut,
            id_materiel=id_materiel,
            id_adherent=id_adherent,
            remarques=remarques,
            date_retour_effective=date_retour_effective,
            historique_statuts=historique_statuts,
            consommables_ids=consommables_ids,
            montant_paye=montant_paye,
            type_paiement=type_paiement
        )

        db.session.add(emprunt)

    # Fonction pour générer des données aléatoires pour une `Reparation`
    def generate_random_reparation():
        statut = random.choice(list(Statut_Reparation))
        id_materiel = random.randint(1, 100)  # Id du matériel réparé
        remarques = f"Remarques sur la réparation {random.randint(1, 1000)}"
        montant = random.uniform(10, 500)

        reparation = Reparation(
            statut=statut,
            id_materiel=id_materiel,
            remarques=remarques,
            montant=montant
        )

        db.session.add(reparation)


    def populate_data():
        for _ in range(100):
            generate_random_materiel()
            generate_random_adherent()
            generate_random_consommable()
            generate_random_emprunt()
            generate_random_reparation()

        db.session.commit()  # Commit les données dans la base de données


    populate_data()