from flask import Flask
from models import db

UPLOAD_FOLDER = 'uploads'  # Répertoire où vous souhaitez stocker les fichiers

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'mysecretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite à 16MB pour les fichiers

db.init_app(app)

# Importer les routes
from routes import *
from routes_materiels import *
from routes_adherents import *
from routes_consommables import *
from routes_emprunts import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables
    app.run(debug=True)
