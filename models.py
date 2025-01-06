from enum import Enum
import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class TypeEnergie(Enum):
    """Enum représentant les types d'énergie des matériels."""
    batterie = "batterie"
    secteur = "secteur"
    thermique = "thermique"
    manuel = "manuel"

class Categorie(Enum):
    """Enum représentant les catégories de matériels."""
    automobile = "automobile"
    bois = "bois"
    batiment = "batiment"
    divers = "divers"
    plomberie = "plomberie"
    tapisserie = "tapisserie"
    jardinage = "jardinage"

class Etat(Enum):
    """Enum représentant les catégories de matériels."""
    en_panne = "en_panne"
    reforme = "reforme"
    ok = "ok"

class Materiel(db.Model):
    """Modèle représentant un matériel à louer.

    Attributs :
        id_materiel (int): Identifiant unique du matériel.
        numero_materiel(int) : Numéro d'identification du matériel.
        nom_materiel (str): Nom du matériel.
        description (str): Description détaillée du matériel.
        prix_location_semaine (float): Prix de location par semaine.
        etat (Etat): Indique l'état du matériel.
        date_achat (date): Date d'achat du matériel.
        categorie (Categorie): Catégorie du matériel.
        niveau_danger (bool): Indique si le matériel est dangereux (de 1 à 3).
        poids (float): Poids du matériel.
        reference (str): Référence du matériel.
        num_serie (str): Numéro de série du matériel.
        date_vidange (date): Date de dernière vidange.
        date_entretien (date): Date de dernier entretien.
        nb_heure (int): Nombre d'heures d'utilisation.
        marque (str): Marque du matériel.
        facture (str): Chemin vers le document de facture.
        prix_achat (float): Prix d'achat du matériel.
        lieu_achat (str): Lieu d'achat du matériel : url, adresse.
        localisation (str): Localisation du matériel.
        manuel_user (str): Chemin vers un le manuel utilisateur.
        vue_eclatee (str): Chemin vers un la vue ecaltee.
        type_energie (TypeEnergie): Type d'énergie du matériel.
        dimensions (str): Dimensions du matériel.
        accessoires_inclus (str): Liste des accessoires inclus.
        securite (str): Informations sur les précautions de sécurité.
        checklist (str): liste de points à verifier sur le matériel.
        avis_client (float): Note attribuée par les clients (doit être entre 1 et 5).
    """

    __tablename__ = 'materiels'

    # Champs 
    id_materiel = db.Column(db.Integer, primary_key=True, index=True)
    numero_materiel = db.Column(db.Integer, nullable=False, index=True)
    nom_materiel = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    prix_location_semaine = db.Column(db.Float, nullable=False)
    etat = db.Column(db.Enum(Etat), index=True, default=Etat.ok)
    date_achat = db.Column(db.Date)
    categorie = db.Column(db.Enum(Categorie), index=True)
    poids = db.Column(db.Float)
    reference = db.Column(db.String(50))
    num_serie = db.Column(db.String(255))
    date_vidange = db.Column(db.Date)
    date_entretien = db.Column(db.Date)
    nb_heure = db.Column(db.Integer, default=0)
    marque = db.Column(db.String(100))
    facture = db.Column(db.String(255))
    prix_achat = db.Column(db.Float)
    lieu_achat = db.Column(db.String(255))
    localisation = db.Column(db.String(10))
    manuel_user = db.Column(db.String(255))
    vue_eclatee = db.Column(db.String(255))
    type_energie = db.Column(db.Enum(TypeEnergie))
    dimensions = db.Column(db.String(50))
    accessoires_inclus = db.Column(db.Text)
    niveau_danger = db.Column(db.Integer, default=1)
    securite = db.Column(db.Text)
    checklist = db.Column(db.Text)
    avis_client = db.Column(db.Float, default=0)

    def __repr__(self):
        """Représentation sous forme de chaîne du matériel."""
        return (f"<Materiel {self.nom_materiel}, Marque: {self.marque}, "
                f"Catégorie: {self.categorie}, Type d'énergie: {self.type_energie}, "
                f"Avis Client: {self.avis_client}>")

    def set_avis_client(self, note):
        """Définit la note du client après validation.

        Args:
            note (float): La note à attribuer.

        Raises:
            ValueError: Si la note n'est pas entre 1 et 5.
        """
        if note < 1 or note > 5:
            raise ValueError("La note doit être entre 1 et 5.")
        self.avis_client = note


class Adherent(db.Model):
    """Modèle représentant un adhérent.

    Attributs :
        id_adherent (int): Identifiant unique de l'adhérent.
        numero_asc (int):  Numéro ASC de l'adhérent.
        nom (str): Nom de l'adhérent.
        prenom (str): Prénom de l'adhérent.
        valide_asc (bool): Indique si l'adhérent est valide.
        email (str): Adresse email de l'adhérent.
        statut (str): Statut de l'adhérent.
        telephone (str): Numéro de téléphone de l'adhérent.
        depuis (date): Date d'adhésion.
        badge (str): Identifiant de badge de l'adhérent.
    """

    __tablename__ = 'adherents'

    # Champs
    id_adherent = db.Column(db.Integer, primary_key=True)
    numero_asc = db.Column(db.Integer)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    valide_asc = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(100),  nullable=False)
    statut = db.Column(db.String(100))
    telephone = db.Column(db.String(15), nullable=True)
    depuis = db.Column(db.Date)
    badge = db.Column(db.String(100))

class Consommable(db.Model):
    """Modèle représentant un consommable.

    Attributs :
        id_consommable (int): Identifiant unique du consommable.
        nom_consommable (str): Nom du consommable.
        description (str): Description du consommable.
        prix (float): Prix du consommable.
        date_achat (date): Date d'achat du consommable.
        quantite_disponible (int): Quantité disponible.
        categorie (Categorie): Catégorie du consommable.
        reference (str): Référence du consommable.
        marque (str): Marque du consommable.
        facture (str): Chemin vers la facture du consommable.
    """

    __tablename__ = 'consommables'

    # Champs 
    id_consommable = db.Column(db.Integer, primary_key=True, index=True)
    nom_consommable = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    prix = db.Column(db.Float, nullable=False, index=True)
    date_achat = db.Column(db.Date, index=True)
    quantite_disponible = db.Column(db.Integer, default=1)
    categorie = db.Column(db.Enum(Categorie), index=True)
    reference = db.Column(db.String(50), index=True)
    marque = db.Column(db.String(100))
    facture = db.Column(db.String(255))

    def as_dict(self):
        """Convertit l'instance en dictionnaire."""
        return {
            'id_consommable': self.id_consommable,
            'nom_consommable': self.nom_consommable,
            'description': self.description,
            'prix': self.prix,
            'date_achat': self.date_achat,
            'quantite_disponible': self.quantite_disponible,
            'categorie': self.categorie.value if self.categorie else None,
            'reference': self.reference,
            'marque': self.marque,
            'facture': self.facture
        }

class Statut_Emprunt(Enum):
    """Enum représentant les statuts possibles d'emprunts."""
    en_cours = "en_cours"
    reserve = "reserve"
    retourne = "retourne"
    annule = "annule"

class Type_Paiement(Enum):
    """Enum représentant les types de paiments possibles."""
    CB = "CB"
    espece = "espece"
    cheque = "cheque"
    autre = "autre"


class Emprunt(db.Model):
    """Modèle représentant un emprunt de matériel.

    Attributs :
        id_emprunt (int): Identifiant unique de l'emprunt.
        date_debut (date): Date de début de l'emprunt.
        duree (int): Durée de l'emprunt (en semaines).
        statut (Statut_Emprunt): Statut de l'emprunt.
        id_materiel (int): Identifiant de l'objet matériel emprunté.
        id_adherent (int): Identifiant de l'adherent.
        remarques (str): Remarques sur l'emprunt.
        date_retour_effective (date): Date de retour effective.
        historique_statuts (str): Historique des statuts de l'emprunt.
        consommables_ids (str): Liste des identifiants de consommables (sous forme JSON).
        montant_paye (float): Montant payé pour l'emprunt.
    """

    __tablename__ = 'emprunts'

    # Champs
    id_emprunt = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date_debut = db.Column(db.Date, nullable=False)
    duree = db.Column(db.Integer, nullable=False)
    statut = db.Column(db.Enum(Statut_Emprunt), index=True)
    id_materiel = db.Column(db.Integer, db.ForeignKey('materiels.id_materiel'))
    id_adherent = db.Column(db.Integer, db.ForeignKey('adherents.id_adherent'))
    remarques = db.Column(db.Text)
    date_retour_effective = db.Column(db.Date)
    historique_statuts = db.Column(db.Text)
    consommables_ids = db.Column(db.Text)  # Liste des identifiants de consommables (en JSON)
    montant_paye = db.Column(db.Float)
    type_paiement = db.Column(db.Enum(Type_Paiement), index=True)

    # Relations
    adherent = db.relationship('Adherent', backref='emprunts')
    materiel = db.relationship('Materiel', backref='emprunts')

    @property
    def consommables_list(self):
        """Convertit la chaîne JSON en liste d'identifiants de consommables.

        Returns:
            list: Liste des identifiants de consommables.
        """
        if self.consommables_ids:
            return json.loads(self.consommables_ids)
        return []

    @consommables_list.setter
    def consommables_list(self, value):
        """Convertit la liste d'identifiants de consommables en chaîne JSON.

        Args:
            value (list): Liste d'identifiants de consommables à convertir en JSON.
        """
        self.consommables_ids = json.dumps(value)

    def duree_reelle_en_semaines(self):
        """Calcule la durée réelle de l'emprunt en semaines en utilisant les numéros de semaine."""
        if self.date_retour_effective:
            # Utiliser la date de retour effective si renseignée
            date_retour = self.date_retour_effective
        else:
            # Sinon, utiliser la date actuelle
            date_retour = datetime.today().date()

        # Obtenir les numéros de semaine pour la date de début (emprunt) et la date de retour
        semaine_debut = self.date_debut.isocalendar()[1]  # Numéro de semaine de la date de début
        semaine_retour = date_retour.isocalendar()[1]  # Numéro de semaine de la date de retour

        # Si l'emprunt traverse une année, ajuster pour les années différentes
        if date_retour.year > self.date_debut.year:
            # Calculer la différence en semaines en tenant compte des changements d'année
            nb_semaines = (52 - semaine_debut + 1) + semaine_retour
        else:
            # Sinon, simple différence de numéros de semaine
            nb_semaines = semaine_retour - semaine_debut + 1

        return nb_semaines-1

    def cout_emprunt(self):
        """Calcule le coût total de l'emprunt (matériel + consommables)."""
        # Calcul du coût de la location du matériel
        cout_location = self.materiel.prix_location_semaine * self.duree_reelle_en_semaines()

        # Calcul du coût des consommables
        cout_consommables = 0
        for consommable_id in self.consommables_list:
            consommable = Consommable.query.get(consommable_id)
            if consommable:
                cout_consommables += consommable.prix * self.duree_reelle_en_semaines()

        # Coût total de l'emprunt
        return cout_location + cout_consommables


class Statut_Reparation(Enum):
    """Enum représentant les statuts possibles de réparation."""
    en_cours = "en_cours"
    irreparable = "irreparable"
    termine = "termine"
    annule = "annule"

class Reparation(db.Model):
    """Modèle représentant une réparation de matériel.

    Attributs :
        id_reparation (int): Identifiant unique de la réparation.
        statut (Statut_Reparation): Statut de la réparation.
        id_materiel (int): Identifiant de l'objet matériel réparé.
        remarques (str): Remarques sur la réparation.
        montant (float): Montant de la réparation.
    """

    __tablename__ = 'reparations'

    # Champs
    id_reparation = db.Column(db.Integer, primary_key=True, autoincrement=True)
    statut = db.Column(db.Enum(Statut_Reparation), index=True)
    id_materiel = db.Column(db.Integer, db.ForeignKey('materiels.id_materiel'))
    remarques = db.Column(db.Text)
    montant = db.Column(db.Float)

    # Relations
    #adherent = db.relationship('Adherent', backref='reparations')
    #materiel = db.relationship('Materiel', backref='reparations')

