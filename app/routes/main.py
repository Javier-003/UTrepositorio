from bson import ObjectId
from flask import Blueprint, render_template, request, redirect, url_for, current_app, session, flash
import base64
import requests

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    db = current_app.get_db_connection()

    # Mostrar los repositorios que existen
    repos = list(db['repositorios'].find())
    return render_template('index.html', repos=repos)

@main_routes.route('/informacion/<repo_id>')
def informacion(repo_id):
    db = current_app.get_db_connection()

    # Buscar el repositorio
    repo = db['repositorios'].find_one({"_id": ObjectId(repo_id)})

    # Buscar archivos del repo
    archivos = list(db['archivos'].find({"repo_id": ObjectId(repo_id)}))

    return render_template('informacion.html', repo=repo, archivos=archivos)
