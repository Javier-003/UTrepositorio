from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
import requests
import time
import dropbox
from config import Config
from app.func.func import login_required, roles_required

GITEA_URL = "http://216.238.83.143:3000/api/v1"
ADMIN_TOKEN = Config.GITEA_TOKEN_ADMIN

usuarios_routes = Blueprint('usuarios', __name__)

# Registro de usuarios
@usuarios_routes.route('/registro', methods=['GET', 'POST'])
@login_required
@roles_required('administrador')
def registro():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()
        role = "usuario"  # Rol por defecto

        if not username or not email or not password:
            flash("Todos los campos son obligatorios.")
            return redirect(url_for('usuarios.registro'))

        db = current_app.get_db_connection()

        if db['usuarios'].find_one({"username": username}):
            flash("El usuario ya existe.")
            return redirect(url_for('usuarios.registro'))

        # Crear usuario en Gitea como admin
        headers = {
            "Authorization": f"token {ADMIN_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {
            "email": email,
            "username": username,
            "password": password,
            "must_change_password": False,
            "send_notify": False
        }


        resp = requests.post(f"{GITEA_URL}/admin/users", headers=headers, json=data)


        if resp.status_code == 201:
            # Guardar usuario en MongoDB
            usuario_doc = {
                "username": username,
                "email": email,
                "role": role
            }
            db['usuarios'].insert_one(usuario_doc)

            # =========================
            # Crear carpeta en Dropbox
            # =========================
            try:
                access_token = current_app.config['DROPBOX_ACCESS_TOKEN']
                dbx = dropbox.Dropbox(access_token)

                carpeta_usuario = f"/user_{username}"

                # Crear carpeta si no existe
                try:
                    dbx.files_get_metadata(carpeta_usuario)
                    print("La carpeta ya existe en Dropbox.")
                except dropbox.exceptions.ApiError:
                    dbx.files_create_folder_v2(carpeta_usuario)
                    print(f"Carpeta creada en Dropbox: {carpeta_usuario}")

                # Guardar referencia de Dropbox en MongoDB
                db['usuarios'].update_one(
                    {"username": username},
                    {"$set": {"dropbox_folder_path": carpeta_usuario}}
                )

            except Exception as e:
                flash(f"Usuario creado, pero no se pudo crear carpeta en Dropbox: {e}")
                print(f"Error Dropbox: {e}")

            flash("Usuario creado correctamente. Ahora inicia sesión para generar tu token.")
            return redirect(url_for('usuarios.login'))

        else:
            flash(f"Error creando usuario en Gitea: {resp.text}")

    return redirect(url_for('admin.vistaAdmin'))


# Login de usuarios
@usuarios_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        db = current_app.get_db_connection()
        user = db['usuarios'].find_one({"username": username})

        if not user:
            flash("Usuario no encontrado. Regístrate primero.")
            return redirect(url_for('usuarios.registro'))

        # Generar un nombre de token único usando timestamp
        token_name = f"flask-session-token-{int(time.time())}"

        create_resp = requests.post(
            f"{GITEA_URL}/users/{username}/tokens",
            auth=(username, password),
            json={"name": token_name, "scopes": ["all"]}
        )

        if create_resp.status_code == 201:
            token = create_resp.json().get("sha1")
        else:
            flash(f"Error generando token: {create_resp.text}")
            return redirect(url_for('usuarios.login'))

        # Guardar token en MongoDB
        db['usuarios'].update_one(
            {"username": username},
            {"$set": {"gitea_token": token}}
        )

        # Iniciar sesión
        session['user'] = {
            "username": user['username'],
            "role": user.get('role'),
            "token": token
        }
        if user['role'] == 'administrador':
            return redirect(url_for('admin.vistaAdmin'))
        else:
            return redirect(url_for('repos.repositorios'))
        
    return render_template('login.html')


# Logout de usuarios
@usuarios_routes.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('token', None)
    flash("Has cerrado sesión correctamente.")
    return redirect(url_for('usuarios.login'))
