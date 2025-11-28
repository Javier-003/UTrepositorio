from bson import ObjectId
import dropbox
from flask import Blueprint, render_template, request, redirect, url_for, current_app, session, flash
import base64
import requests
from app.func.func import login_required, roles_required


admin_routes = Blueprint('admin', __name__)

@admin_routes.route('/Administrador/')
@login_required
@roles_required('administrador')
def vistaAdmin():
    db = current_app.get_db_connection()
    # Mostrar los repositorios que existen
    repos = list(db['repositorios'].find())

    return render_template('admin.html', repos=repos)

@admin_routes.route('/administrador/informacion_proyecto/<repo_id>')
@login_required
@roles_required('administrador')
def ver_informacion_proyecto(repo_id):
    db = current_app.get_db_connection()

    # Buscar el repositorio
    repo = db['repositorios'].find_one({"_id": ObjectId(repo_id)})

    # Buscar archivos del repo
    archivos = list(db['archivos'].find({"repo_id": ObjectId(repo_id)}))

    return render_template('admin_verProyecto.html', repo=repo, archivos=archivos)

@admin_routes.route("/administrador/rechazar_proyecto/<repo_id>", methods=["GET", "POST"])
@login_required
@roles_required('administrador')
def rechazar_proyecto(repo_id):
    db = current_app.get_db_connection()
    razon = request.form.get('razon', '')

    # Actualizar el estado del repositorio a 'rechazado'
    db['repositorios'].update_one(
        {"_id": ObjectId(repo_id)},
        {"$set": {"estado": "rechazado",
                  "razon_rechazo":razon}}
    )

    flash("Proyecto rechazado correctamente.", "success")
    return redirect(url_for('admin.ver_informacion_proyecto', repo_id=repo_id))

@admin_routes.route("/administrador/aceptar_proyecto/<repo_id>", methods=["GET", "POST"])
@login_required
@roles_required('administrador')
def aceptar_proyecto(repo_id):
    db = current_app.get_db_connection()
    # Actualizar el estado del repositorio a 'aceptado'
    db['repositorios'].update_one(
        {"_id": ObjectId(repo_id)},
        {"$set": {"estado": "aceptado"}}
    )
    flash("Proyecto aceptado correctamente.", "success")
    return redirect(url_for('admin.ver_informacion_proyecto', repo_id=repo_id))

@admin_routes.route("/administrador/Registro_usuario", methods=["GET", "POST"])
@login_required
@roles_required('administrador')
def crear_usuario():
    return render_template('registro.html')
