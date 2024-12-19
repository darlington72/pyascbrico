from flask import render_template, request, redirect, url_for, flash,jsonify
from app import app,db  
from models import Consommable


@app.route('/consommables', methods=['GET'])
def get_consommables():
    consommables = Consommable.query.all()
    #return jsonify([consommable.as_dict() for consommable in consommables])
    return render_template('consommables.html', consommables=consommables)

@app.route('/consommables', methods=['POST'])
def create_consommable():

    nom_consommable = "test"
    prix=1

    nouveau_consommable = Consommable(
        nom_consommable=nom_consommable,
        prix=prix,
    )

    db.session.add(nouveau_consommable)
    db.session.commit()
    
    flash('Nouveau consommable ajouté avec succès!', 'success')
    return redirect(url_for('get_consommables'))

@app.route('/consommables/<int:id>', methods=['GET'])
def get_consommable(id):
    consommable = Consommable.query.get_or_404(id)
    return jsonify(consommable.as_dict())

@app.route('/consommables/<int:id>', methods=['PUT'])
def update_consommable(id):
    consommable = Consommable.query.get_or_404(id)
    data = request.json
    for key, value in data.items():
        setattr(consommable, key, value)
    db.session.commit()
    return jsonify(consommable.as_dict())

@app.route('/consommables/<int:id>', methods=['DELETE'])
def delete_consommable(id):
    consommable = Consommable.query.get_or_404(id)
    db.session.delete(consommable)
    db.session.commit()
    return '', 204
