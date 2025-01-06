from flask import render_template
from app import app,db 

from models import Emprunt

@app.route('/')
def index():

    emprunts = Emprunt.query.all()

    return render_template('index.html')

