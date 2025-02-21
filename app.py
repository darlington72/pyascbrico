from flask import Flask
from models import db
import os

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  

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
from routes_tresorerie import *
from routes_pannes import *

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables
    app.run(host="0.0.0.0",port=80)
