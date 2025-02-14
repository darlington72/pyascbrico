from flask import render_template, request, redirect, url_for, flash
from app import app,db
from models import Materiel,Etat

@app.route('/pannes')
def get_pannes():
    materiels_en_panne = Materiel.query.filter_by(etat=Etat.en_panne).all()
    return render_template('pannes.html', materiels_en_panne=materiels_en_panne)

